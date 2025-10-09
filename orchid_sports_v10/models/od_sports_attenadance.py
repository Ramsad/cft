# -*- coding: utf-8 -*-
# from openerp.osv import fields, osv
# from openerp.tools.translate import _
import copy
import math
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
import datetime
import dateutil.relativedelta
from datetime import date, timedelta
import itertools
from lxml import etree
import odoo.addons.decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime


def simply(l):
    result = []
    for item in l:
        check = False
        # check item, is it exist in result yet (r_item)
        for r_item in result:
            if item['partner_id'] == r_item['partner_id']:
                # if found, add all key to r_item ( previous record)
                check = True
                fees = r_item['fees'] + item['fees']
                r_item['fees'] = fees
        if check == False:
            result.append(item)
    return result


class od_sports_attendance(models.Model):
    _name = 'od.sports.attendance'
    _order = 'id desc'

    # 
    # @api.depends('date_from','date_to')
    # def get_time_diff(self):

    #     date_from = self.date_from
    #     date_to = self.date_to
    #     if date_from and date_to:
    #         start_time = datetime.strptime(date_from, DEFAULT_SERVER_DATETIME_FORMAT)
    #         complete_time = datetime.strptime(date_to, DEFAULT_SERVER_DATETIME_FORMAT)
    #         diff = (complete_time -start_time)
    #         days = diff.days * 24
    #         seconds = diff.seconds
    #         hour= days + float(seconds)/3600
    #         self.duration = hour
    @api.depends('date_from', 'date_to')
    def get_time_diff(self):
        for rec in self:
            date_from = rec.date_from
            date_to = rec.date_to
            if date_from and date_to:
                date_from = date_from
                date_to = date_to
                diff = (date_to - date_from)
                rec.duration = diff

    name = fields.Char(string='Name', required=True, default='/')
    date = fields.Date('Date', required=True)
    # time_from = fields.Char(string='Time From',required="0",size=16)
    # time_to = fields.Char(string='Time To',required="0",size=16)
    date_from = fields.Float(string="Date From")
    date_to = fields.Float(string="Date To")
    duration = fields.Float(string="Duration", compute="get_time_diff", store=True)
    activities_id = fields.Many2one('od.activities', string='Program', required=True)
    day = fields.Char(string='Day', invisible='1')
    od_scheduled = fields.Many2one('od.scheduled', string='Schedule')
    move_id = fields.Many2one('account.move', string='Journal Number', readonly=True)
    provision_move_id = fields.Many2one('account.move', string='Provision Journal', readonly=True)
    booking_move_id = fields.Many2one('account.move', string='Booking Journal', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft')
    venue_id = fields.Many2one('od.venue', string='Venue', readonly=True, states={'draft': [('readonly', False)]})
    coach_id = fields.Many2one('res.partner', string='Coach', readonly=True, states={'draft': [('readonly', False)]})
    percentage = fields.Float(string="Percentage", readonly=True, states={'draft': [('readonly', False)]})
    academy_id = fields.Many2one('res.partner', string='Academy', readonly=True)
    product_id = fields.Many2one('product.product', string='Term', )
    term_id = fields.Many2one('od.terms', string='Term')
    fees = fields.Float(string='Fees', readonly=True)
    no_of_class = fields.Integer(string='Number Of Class', readonly=True)
    attendance_line = fields.One2many('od.sports.attendance.line', 'attendance_id', string='Attendance Lines')
    cost_centre_id = fields.Many2one('orchid.account.cost.center', string='Cost Centre')
    tick_all = fields.Boolean('Select All')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('od.sports.attendance') or '/'
        return super(od_sports_attendance, self).create(vals)

    def action_confirm(self):

        obj = self.env['od.sports.attendance'].browse(self._ids)
        revenue_account_id = obj.activities_id.revenue_account_id.id

        academy_comm_exp_id = obj.activities_id.academy_comm_exp_id.id
        coach_comm_exp_id = obj.activities_id.coach_comm_exp_id.id
        attendance_pro_journal = obj.activities_id.attendance_pro_journal.id
        attendance_journal_id = obj.activities_id.attendance_journal_id.id
        prepaid_revenue_account_id = obj.activities_id.prepaid_revenue_account_id.id
        attendance_line = obj.attendance_line
        program_id = obj.activities_id.id
        od_attendance_journal_id = obj.activities_id.attendance_journal_id and obj.activities_id.attendance_journal_id.id
        account_move_obj = self.env['account.move']
        account_coach_comm_prov_id = obj.activities_id.account_coach_comm_prov_id and obj.activities_id.account_coach_comm_prov_id.id
        account_acdmy_comm_prov_id = obj.activities_id.account_acdmy_comm_prov_id and obj.activities_id.account_acdmy_comm_prov_id.id

        term_name = obj.term_id.name
        date = obj.date
        analytic_acc_id = obj.venue_id.analytic_acc_id.id
        account_coach_comm_collected_id = obj.activities_id.account_coach_comm_collected_id.id
        provision_journal = obj.activities_id.attendance_pro_journal.id
        booking_journal = obj.activities_id.attendance_booking_journal_id.id

        coach_payable = obj.coach_id and obj.coach_id.property_account_payable_id and obj.coach_id.property_account_payable_id.id

        data_line = []
        data_line2 = []
        data_line3 = []
        for line in attendance_line:
            partner_id = line.partner_id.id
            product_id = obj.term_id.product_id.id
            orchid_cc_id = line.type_id.cost_centre_id.id
            type_id = line.type_id.id
            camp_line = self.env['od.activities.camp.line'].search(
                [('activities_id', '=', program_id), ('type_id', '=', type_id)])
            amount = 0
            x_amount = 0
            y_amount = 0
            commission = camp_line.commission
            if term_name == 'Term-1':

                amount = camp_line.t1_fee
                x_amount = (amount * commission) / 100
                y_amount = (amount * obj.venue_id.commission) / 100

            if term_name == 'Term-2':

                amount = camp_line.t2_fee
                x_amount = (amount * commission) / 100
                y_amount = (amount * obj.venue_id.commission) / 100
            if term_name == 'Term-3':

                amount = camp_line.t3_fee
                x_amount = (amount * commission) / 100
                y_amount = (amount * obj.venue_id.commission) / 100

            dr_line = (0, 0, {

                'date': date,
                'naration': obj.name,
                'name': obj.name,
                'account_id': prepaid_revenue_account_id,
                'debit': amount,
                'credit': 0,
                'partner_id': partner_id,
                'product_id': product_id,
                'orchid_cc_id': orchid_cc_id,
                'analytic_account_id': analytic_acc_id,
            })

            cr_line = (0, 0, {

                'date': date,
                'naration': obj.name,
                'name': obj.name,
                'account_id': revenue_account_id,
                'debit': 0,
                'credit': amount,
                'partner_id': partner_id,
                'product_id': product_id,
                'orchid_cc_id': orchid_cc_id,
                'analytic_account_id': analytic_acc_id,
            })

            x_dr_line = (0, 0, {

                'date': date,
                'naration': obj.name,
                'name': line.partner_id.name,
                'account_id': account_coach_comm_collected_id,
                'debit': x_amount,
                'credit': 0,
                'partner_id': partner_id,
                'product_id': product_id,
                'orchid_cc_id': orchid_cc_id,
                'analytic_account_id': analytic_acc_id,
            })

            x_cr_line = (0, 0, {

                'date': date,
                'naration': obj.name,
                'name': line.partner_id.name,
                'account_id': coach_payable,
                'debit': 0,
                'credit': x_amount,
                'partner_id': partner_id,
                'product_id': product_id,
                'orchid_cc_id': orchid_cc_id,
                'analytic_account_id': analytic_acc_id,
            })

            b_c_cr_line = (0, 0, {

                'date': date,
                'naration': obj.name,
                'name': line.partner_id.name,
                'account_id': account_coach_comm_prov_id,
                'debit': 0,
                'credit': x_amount,
                'partner_id': obj.coach_id and obj.coach_id.id,
                'product_id': product_id,
                'orchid_cc_id': orchid_cc_id,
                'analytic_account_id': analytic_acc_id,
            })

            b_c_dr_line = (0, 0, {

                'date': date,
                'naration': obj.name,
                'name': line.partner_id.name,
                'account_id': coach_comm_exp_id,
                'debit': x_amount,
                'credit': 0,
                'partner_id': obj.coach_id and obj.coach_id.id,
                'product_id': product_id,
                'orchid_cc_id': orchid_cc_id,
                'analytic_account_id': analytic_acc_id,
            })

            a_b_cr_line = (0, 0, {

                'date': date,
                'naration': obj.name,
                'name': line.partner_id.name,
                'account_id': account_acdmy_comm_prov_id,
                'debit': 0,
                'credit': y_amount,
                'partner_id': obj.venue_id.owner and obj.venue_id.owner.id,
                'product_id': product_id,
                'orchid_cc_id': orchid_cc_id,
                'analytic_account_id': analytic_acc_id,
            })

            a_c_dr_line = (0, 0, {

                'date': date,
                'naration': obj.name,
                'name': line.partner_id.name,
                'account_id': academy_comm_exp_id,
                'debit': y_amount,
                'credit': 0,
                'partner_id': obj.venue_id.owner and obj.venue_id.owner.id,
                'product_id': product_id,
                'orchid_cc_id': orchid_cc_id,
                'analytic_account_id': analytic_acc_id,
            })
            data_line.append(dr_line)
            data_line.append(cr_line)
            data_line2.append(x_cr_line)
            data_line2.append(x_dr_line)
            data_line3.append(b_c_dr_line)
            data_line3.append(b_c_cr_line)

            data_line3.append(a_c_dr_line)
            data_line3.append(a_b_cr_line)
        data = {
            'journal_id': od_attendance_journal_id,
            'date': date,
            'state': 'draft',
            'ref': obj.activities_id.name,
            'line_ids': data_line,
        }

        data1 = {
            'journal_id': provision_journal,
            'date': date,
            'state': 'draft',
            'ref': obj.activities_id.name,
            'line_ids': data_line2,
        }
        data2 = {
            'journal_id': booking_journal,
            'date': date,
            'state': 'draft',
            'ref': obj.activities_id.name,
            'line_ids': data_line3,
        }
        #        account_move_id = account_move_obj.create(data)
        #        provision_move_id = account_move_obj.create(data1)
        #        booking_move_id = account_move_obj.create(data2)
        self.state = 'confirm'
        #        self.move_id = account_move_id.id
        #        self.provision_move_id = provision_move_id.id
        #        self.booking_move_id = booking_move_id.id
        return True

    #        for line in obj.attendance_line:
    #            if line.jv:
    #                no_students_attended = no_students_attended + 1
    #        if no_students_attended == 0:
    #            raise UserError(_('no students attended'))
    #        account_move_obj = self.env['account.move']
    #        od_fees = obj.activities_id.fees
    #        od_cost_centre_id = obj.activities_id.cost_centre_id and obj.activities_id.cost_centre_id.id or False
    #        od_no_of_class = obj.activities_id.no_of_class
    #        od_product_id = obj.activities_id.product_id and obj.activities_id.product_id.id
    #        # coach_percentage = obj.activities_id.coach_percentage
    #        accademy_percentage = obj.activities_id.academy_percentage
    #
    #        od_prepaid_revenue_account_id = obj.activities_id.prepaid_revenue_account_id and obj.activities_id.prepaid_revenue_account_id.id or False
    #        od_income_account_id = obj.activities_id.income_account_id and obj.activities_id.income_account_id.id or False
    #        academy_commission_acc_id = obj.activities_id.academy_commission_acc_id and obj.activities_id.academy_commission_acc_id.id or False
    #        provider_commission_acc_id = obj.activities_id.provider_commission_acc_id and obj.activities_id.provider_commission_acc_id.id or False
    #        if not od_income_account_id:
    #            raise UserError(_('define income account in activities'))
    #        if not academy_commission_acc_id:
    #            raise UserError(_('define academy commission acc in activities'))
    #        if not provider_commission_acc_id:
    #            raise UserError(_('define provider commission acc in activities'))
    #        od_prepaid_expense_account_id = obj.activities_id.prepaid_expense_account_id and obj.activities_id.prepaid_expense_account_id.id or False
    #        if not od_prepaid_expense_account_id:
    #            raise UserError(_('define prepaid Expense account in activities'))
    #        coach_id = obj.activities_id.coach_id and obj.activities_id.coach_id.id
    #        if not coach_id:
    #            raise UserError(_('define coach in activities'))
    #        # coach_name = obj.activities_id.coach_id and obj.activities_id.coach_id.name
    #        coach_name = obj.coach_id and obj.coach_id.id
    #        analytic_account_id = obj.venue_id and obj.venue_id.analytic_acc_id and obj.venue_id.analytic_acc_id.id or False
    #        coach_percentage = obj.percentage
    #        coach_acc_id = obj.coach_id.property_account_payable and obj.coach_id.property_account_payable.id or False
    #        accademy_id = obj.activities_id.academy_id and obj.activities_id.academy_id.id
    #        accademy_name = obj.activities_id.academy_id and obj.activities_id.academy_id.name
    #        accademy_account_id = obj.activities_id.academy_id.property_account_payable and obj.activities_id.academy_id.property_account_payable.id
    #        #fees
    #        fees_amount = 0.0
    #        camp_line = self.env['od.activities.camp.line']
    #        activities_id = obj.activities_id and obj.activities_id.id
    #        for line in obj.attendance_line:
    #            if line.jv:
    #                type_id = line.type_id and line.type_id.id
    #                fee_line_id = camp_line.search([('activities_id','=',activities_id),('type_id','=',type_id)],limit=1)
    #                if not fee_line_id:
    #                    raise UserError("Please Check The Fee Structure With The Program")
    #                fee_line_obj = camp_line.browse(cr,uid,fee_line_id)
    #                unit_fees = fee_line_obj.fees / fee_line_obj.no_of_class
    #                fees_amount += unit_fees

    #        if not od_prepaid_revenue_account_id:
    #            raise UserError(_('define prepaid Revenue account in activities'))
    #        if not od_attendance_journal_id:
    #            raise UserError(_('define attendance journal in activities'))
    #        date = obj.date
    #        period_pool = self.env['account.period']
    #        search_periods = period_pool.find(date)
    #        period_id = search_periods[0]
    #        data_lines = []
    #        x_c = round( (( fees_amount*(coach_percentage))/100),2)
    #        y_a = round( (( fees_amount*(accademy_percentage))/100),2)
    #        if coach_percentage >0 and accademy_percentage >0:

    #            total_per = x_c + y_a

    #            vals1 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'partner_id':coach_name,
    #                    'analytic_account_id':analytic_account_id,
    #                    'date':date,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':od_income_account_id,
    #                    'credit':fees_amount,
    #                    'debit':0.0,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }

    #            vals2 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'partner_id':coach_name,
    #                    'analytic_account_id':analytic_account_id,
    #                    'date':date,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':od_prepaid_revenue_account_id,
    #                    'debit':fees_amount,
    #                    'credit':0.0,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }

    #            vals3 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'analytic_account_id':analytic_account_id,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':provider_commission_acc_id,
    #                    'debit':x_c,
    #                    'credit':0.0,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }

    #            vals5 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'analytic_account_id':analytic_account_id,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':academy_commission_acc_id,
    #                    'debit':y_a,
    #                    'credit':0.0,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }

    #            vals4 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'analytic_account_id':analytic_account_id,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':od_prepaid_expense_account_id,
    #                    'credit':y_a,
    #                    'debit':0.0,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }
    #            vals6 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'analytic_account_id':analytic_account_id,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':coach_acc_id,
    #                    'credit':x_c,
    #                    'debit':0.0,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }
    #            data_lines.append([0,0,vals1])
    #            data_lines.append([0,0,vals2])
    #            data_lines.append([0,0,vals4])
    #            data_lines.append([0,0,vals3])
    #            data_lines.append([0,0,vals5])
    #            data_lines.append([0,0,vals6])
    #        elif coach_percentage >0 and accademy_percentage ==0:
    #            vals1 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'analytic_account_id':analytic_account_id,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':od_income_account_id,
    #                    'credit':fees_amount,
    #                    'debit':0.0,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }
    #            vals2 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'analytic_account_id':analytic_account_id,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':od_prepaid_revenue_account_id,
    #                    'debit':fees_amount,
    #                    'credit':0.0,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }

    #            vals3 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'analytic_account_id':analytic_account_id,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':provider_commission_acc_id,
    #                    'debit':x_c,
    #                    'credit':0.0,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }

    #            vals4 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'analytic_account_id':analytic_account_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':coach_acc_id,
    #                    'credit':x_c,
    #                    'debit':0.0,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }

    #            data_lines.append([0,0,vals1])
    #            data_lines.append([0,0,vals2])
    #            data_lines.append([0,0,vals3])
    #            data_lines.append([0,0,vals4])

    #        elif accademy_percentage >0 and  coach_percentage==0:

    #            vals1 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'analytic_account_id':analytic_account_id,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':od_income_account_id,
    #                    'credit':fees_amount,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }

    #            vals2 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'analytic_account_id':analytic_account_id,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':od_prepaid_revenue_account_id,
    #                    'debit':fees_amount,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }

    #            vals3 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'naration':'Attendance',
    #                    'analytic_account_id':analytic_account_id,
    #                    'name':'Attendance',
    #                    'account_id':academy_commission_acc_id,
    #                    'debit':y_a,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }

    #            vals4 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'naration':'Attendance',
    #                    'analytic_account_id':analytic_account_id,
    #                    'name':'Attendance',
    #                    'account_id':od_prepaid_expense_account_id,
    #                    'credit':y_a,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }
    #            data_lines.append([0,0,vals1])
    #            data_lines.append([0,0,vals2])
    #            data_lines.append([0,0,vals3])
    #            data_lines.append([0,0,vals4])

    #        elif accademy_percentage ==0 and  coach_percentage==0:

    #            vals1 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'analytic_account_id':analytic_account_id,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':od_income_account_id,
    #                    'credit':fees_amount,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }

    #            vals2 = {
    #                    'period_id':period_id,
    #                    'journal_id':od_attendance_journal_id,
    #                    'date':date,
    #                    'partner_id':coach_name,
    #                    'analytic_account_id':analytic_account_id,
    #                    'naration':'Attendance',
    #                    'name':'Attendance',
    #                    'account_id':od_prepaid_revenue_account_id,
    #                    'debit':fees_amount,
    #                    'product_id':od_product_id or False,
    #                    'od_cost_centre_id':od_cost_centre_id or False
    #            }
    #            data_lines.append([0,0,vals1])
    #            data_lines.append([0,0,vals2])
    #        data = {
    #            'journal_id':od_attendance_journal_id,
    #            'date':date,
    #            'state':'draft',
    #            'ref':obj.activities_id.name,
    #            'line_ids':data_lines,
    #        }
    ##        account_move_id = account_move_obj.create(data)
    ##        self.env['od.sports.attendance'].write({'state':'confirm','move_id':account_move_id})
    ##        return True
    def action_cancel(self):
        obj = self.env['od.sports.attendance'].browse(self._ids)
        move_id = obj.move_id and obj.move_id.id
        provision_move_id = obj.provision_move_id and obj.provision_move_id.id
        booking_move_id = obj.booking_move_id and obj.booking_move_id.id
        if move_id:
            obj.move_id.button_cancel()
            obj.move_id.unlink()
        if provision_move_id:
            obj.provision_move_id.button_cancel()
            obj.provision_move_id.unlink()
        if booking_move_id:
            obj.booking_move_id.button_cancel()
            obj.booking_move_id.unlink()

        self.state = 'cancel'
        return True

    
    def set_to_draft(self):
        self.state = 'draft'

    
    def onchange_activities_id(self, activities_id):
        if activities_id:
            activities = self.env['od.activities'].browse(activities_id)
            return {
                'value': {
                    'venue_id': activities.venue_id and activities.venue_id.id or False,
                    'coach_id': activities.coach_id and activities.coach_id.id or False,
                    'academy_id': activities.academy_id and activities.academy_id.id or False,
                    'product_id': activities.product_id and activities.product_id.id or False,
                    'fees': activities.fees,
                    'no_of_class': activities.no_of_class
                }
            }
        return {}

    @api.onchange('tick_all')
    def onchange_tick_all(self):

        if self.tick_all:
            for lines in self.attendance_line:
                lines.tick_me = True

        # return True

    
    def unlink(self):
        for obj in self:
            if obj.state not in ('draft'):
                raise UserError(_('You cannot delete it,it is not in draft'))
        return super(od_sports_attendance, self).unlink()

    
    def od_fill(self):
        for obj in self:
            attendance_line = obj.attendance_line
            attendance_line.unlink()
        activities_id = self.activities_id and self.activities_id.id or False
        cost_centre_id = self.cost_centre_id and self.cost_centre_id.id
        od_sports_receipt_ids = self.env['od.sports.receipt'].search([('activities_id', '=', activities_id)])
        res = []
        for recipt in od_sports_receipt_ids:

            for reciept_line in recipt.receipt_line:
                type_cost_centre_id = reciept_line.type_id and reciept_line.type_id.cost_centre_id and reciept_line.type_id.cost_centre_id.id
                if cost_centre_id == type_cost_centre_id:
                    amount = reciept_line.amount
                    vals = {'partner_id': reciept_line.partner_id and reciept_line.partner_id.id,
                            'fees': amount,
                            'type_id': reciept_line.type_id and reciept_line.type_id.id,
                            'attendance_id': self.id, }
                    res.append(vals)
        result = simply(res)
        for vals in result:
            self.env['od.sports.attendance.line'].create(vals)
        return True

    
    def od_delete_me(self):
        obj = self
        attendance_line = self.attendance_line
        for line in attendance_line:
            if line.tick_me:
                line.unlink()
        obj.tick_all = False
        return True

    
    def onchange_date(self, date):
        coach_ids = []
        if date:
            day_pos = datetime.strptime(date, "%Y-%m-%d").date().weekday()
            if day_pos > 6:
                day_pos = 7
            day_obj = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
            day = day_obj[day_pos]
            schedule_objs = self.env['od.scheduled'].search([('day', 'in', [day, 'all'])])
            for schedule_obj in schedule_objs:

                id = schedule_obj.coach_id and schedule_obj.coach_id.id

                if id not in coach_ids:
                    coach_ids.append(id)

            return {
                'value': {
                    'day': day_obj[day_pos] or '',
                }, 'domain': {
                    'od_scheduled': [('day', 'in', [day, 'all']), ('active', '=', True)],
                    'coach_id': [('id', 'in', coach_ids)]
                }
            }
        else:
            return {
                'value': {
                    'day': None,
                }, 'domain': {
                    'od_scheduled': '',
                    'coach_id': ''
                }
            }

    
    def onchange_coach(self, coach_id):
        ids = []
        day = None
        day_pos = None

        if coach_id:
            schedule_objs = self.env['od.scheduled'].search([('coach_id', '=', coach_id)])
            for schedule_obj in schedule_objs:
                ids.append(schedule_obj.id)
        return {
            'domain': {
                'od_scheduled': [('id', 'in', ids), ('active', '=', True)],
            }
        }



def onchange_od_scheduled(self, od_scheduled):
    if od_scheduled:
        schedule = self.env['od.scheduled'].browse(od_scheduled)
        activities_id = schedule.activities_id and schedule.activities_id.id
        # date = schedule.date
        venue_id = schedule.venue_id and schedule.venue_id.id
        coach_id = schedule.coach_id and schedule.coach_id.id
        percentage = schedule.percentage
        academy_id = schedule.academy_id and schedule.academy_id.id
        cost_centre_id = schedule.cost_centre_id and schedule.cost_centre_id.id
        date_from = schedule.date_from
        date_to = schedule.date_to
        term_id = schedule.term_id and schedule.term_id.id
        scheduled_line = schedule.scheduled_line
        line_data = []
        for line in scheduled_line:
            line_vals = {'partner_id': line.partner_id and line.partner_id.id,
                         'type_id': line.type_id and line.type_id.id,
                         'mobile_no': line.mobile_no,
                         'remarks': line.remarks,
                         'fees': line.fees,
                         'jv': line.jv
                         }
            line_data.append(line_vals)
        result = {'value': {
            'activities_id': activities_id,
            'venue_id': venue_id,
            'coach_id': coach_id,
            'percentage': percentage,
            'academy_id': academy_id,
            'cost_centre_id': cost_centre_id,
            'date_from': date_from,
            'date_to': date_to,
            'term_id': term_id,
            'attendance_line': line_data
        }}
        return result

        # return True


class od_sports_attendance_line(models.Model):
    _name = 'od.sports.attendance.line'

    @api.model
    def create(self, vals):
        if vals.get('attendance_id') or vals.get('partner_id'):
            attendance_obj = self.env['od.sports.attendance'].browse([vals.get('attendance_id')])
            program_id = attendance_obj.activities_id and attendance_obj.activities_id.id or False
            existing_record = self.env['od.registration.line'].search(
                [('activities_id', '=', program_id), ('partner_id', '=', vals.get('partner_id'))])
            mobile_no = self.env['res.partner'].browse([vals.get('partner_id')]).mobile

            # psp
            scheduled_obj = attendance_obj.od_scheduled
            for line in attendance_obj.attendance_line:
                attend_obj = None
                attend_obj = self.env['od.scheduled.line'].search(
                    [('scheduled_id', '=', scheduled_obj.id), ('partner_id', '=', line.partner_id.id),
                     ('type_id', '=', line.type_id.id)])
                if not attend_obj:
                    self.env['od.scheduled.line'].create(
                        {
                            'scheduled_id': scheduled_obj.id,
                            'mobile_no': line.mobile_no,
                            'partner_id': line.partner_id.id,
                            'type_id': line.type_id.id,
                            'fees': line.fees,
                            'jv': line.jv
                        }
                    )

            if not existing_record:
                self.env['od.registration.line'].create(
                    {'activities_id': program_id, 'partner_id': vals.get('partner_id'), 'rv_no': mobile_no})

        return super(od_sports_attendance_line, self).create(vals)

    
    def onchange_partner_id(self, partner_id):
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            return {
                'value': {
                    'mobile_no': partner.mobile or '',
                }
            }
        return {}

    
    def onchange_attendance(self, attendance):
        if not attendance:
            return {
                'value': {
                    'jv': False,
                }
            }
        return {}

    @api.onchange('type_id')
    def onchange_type_id(self):
        ids = []
        cc_id = self.attendance_id.cost_centre_id and self.attendance_id.cost_centre_id.id
        for t_id in self.attendance_id.activities_id.camp_line:
            if t_id.cost_centre_id.id == cc_id:
                ids.append(t_id.type_id.id)
        return {'domain': {'type_id': [('id', 'in', ids)]}}

    attendance_id = fields.Many2one('od.sports.attendance', string='Sports Receipt', ondelete='cascade')
    mobile_no = fields.Char(string='Mobile No', readonly=True, )
    partner_id = fields.Many2one('res.partner', string='Student', required=True)
    type_id = fields.Many2one('od.camp.type', string='Type',)
    fees = fields.Float(string='Fees')
    remarks = fields.Char(string='Remarks')
    attendance = fields.Boolean(string='Attendance')
    jv = fields.Boolean(string='JV')
    tick_me = fields.Boolean('Select')
