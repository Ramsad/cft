# -*- coding: utf-8 -*-
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
from dateutil.relativedelta import relativedelta


class od_activities(models.Model):
    _name = 'od.activities'
    _order = "id desc"


    name = fields.Char(string='Name', required=True, )
    venue_id = fields.Many2one('od.venue', string='Venue')
    sequence = fields.Char(string='Seq', readonly=True, default='/')
    coach_id = fields.Many2one('res.partner', string='Coach/Provider')
    coach_percentage = fields.Float(string='Percentage')
    analytic_acc_id = fields.Many2one('account.analytic.account', string='Facility')
    types = fields.Selection([
        ('camp', 'Lesson')
    ], string='Type', default='camp')
    academy_id = fields.Many2one('res.partner', string='Academy')
    academy_percentage = fields.Float(string='Percentage')
    manager_id = fields.Many2one('res.partner', string='Manager')
    customer_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='Term/Product')
    cost_centre_id = fields.Many2one('orchid.account.cost.center', string='Cost Centre')
    collection_journal_id = fields.Many2one('account.journal', string='Collection Journal')
    attendance_journal_id = fields.Many2one('account.journal', string='Attendance Revenue Journal')
    attendance_booking_journal_id = fields.Many2one('account.journal', string='Attendance Booking Journal')
    transfer_journal_id = fields.Many2one('account.journal', string='Transfer Journal')
    start_date = fields.Date(string='Start Date', required=True)
    #    od_pricelist_id = fields.Many2one('od.fee.structure.pricelist',string='PriceList')
    end_date = fields.Date(string='End Date', required=True)
    fees = fields.Float(string='Fees')
    no_of_class = fields.Integer(string='Number Of Class', default=1)

    prepaid_revenue_account_id = fields.Many2one(
        'account.account')  # ,string='Prepaid Revenue Account',domain=[('type', 'not in', ['view','consolidation','closed'])])
    prepaid_expense_account_id = fields.Many2one(
        'account.account')  # ,string='Prepaid Expense Account',domain=[('type', 'not in', ['view','consolidation','closed'])])
    income_account_id = fields.Many2one('account.account',
                                        string='Income Account')  # ,domain=[('type', 'not in', ['view','consolidation','closed'])])
    academy_commission_acc_id = fields.Many2one('account.account',
                                                string='Academy Commission Acc')  # ,domain=[('type', 'not in', ['view','consolidation','closed'])])
    provider_commission_acc_id = fields.Many2one('account.account',
                                                 string='Provider Commission Acc')  # ,domain=[('type', 'not in', ['view','consolidation','closed'])])
    registration_acc_id = fields.Many2one('account.account',
                                          string='Registration Acc')  # ,domain=[('type', 'not in', ['view','consolidation','closed'])])
    registration_fee = fields.Float(string="Registration Fee")
    collection_account_ids = fields.Many2many('account.account',
                                              string='Collection Accounts')  # ,domain=[('type', '=', 'liquidity')])
    rental_line = fields.One2many('od.activities.rental.line', 'activities_id', string='Rental Lines')
    registration_line = fields.One2many('od.registration.line', 'activities_id', copy=True, string='Registration Lines')
    camp_line = fields.One2many('od.activities.camp.line', 'activities_id', copy=True, string='Camp Lines')
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string="Status", default="draft")
    account_acdmy_comm_prov_id = fields.Many2one('account.account', string='Provision for Academy Commission')
    account_coach_comm_prov_id = fields.Many2one('account.account', string='Provision for Coach Commission')
    account_coach_comm_collected_id = fields.Many2one('account.account', string='Coach Commission Collected')
    provision_journal_id = fields.Many2one('account.journal', string='Commission Journal')
    return_journal_id = fields.Many2one('account.journal', string='Return Journal')
    revenue_account_id = fields.Many2one('account.account', string='Revenue Account')
    nonrevenue_account_id = fields.Many2one('account.account', string='Revenue Account')
    academy_comm_exp_id = fields.Many2one('account.account', string='Accademy commission Exp Acc')
    coach_comm_exp_id = fields.Many2one('account.account', string='Coach commission Exp Acc')
    attendance_pro_journal = fields.Many2one('account.journal', string='Attendance Provision Journal')
    is_non_revenue = fields.Boolean(string='Non Revenue')
    admin_incharge_id = fields.Many2one('res.partner', string='Admin Incharge')

    @api.onchange('coach_id')
    def onchange_coach_id(self):
        res = {}
        res['domain'] = {'coach_id': [('od_coach', '=', True)]}
        return res

    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('sequence', '/') == '/' and vals.get('types') == 'rental':
                vals['sequence'] = seq.next_by_code('od.activities') or '/'
        return super().create(vals_list)

    def unlink(self):
        for obj in self:
            attendance_ids = self.env['od.sports.attendance'].search([('activities_id', '=', obj.id)])
            collection_ids = self.env['od.sports.receipt'].search([('activities_id', '=', obj.id)])
            if attendance_ids or collection_ids:
                raise UserError(_('You cannot delete it, which is already used in other documents.'))
        return super(od_activities, self).unlink()

    def onchange_venue_id(self, venue_id):
        if venue_id:
            venue = self.env['od.venue'].browse(venue_id)
            analytic_acc_id = venue.analytic_acc_id and venue.analytic_acc_id.id or False
            parent_id = venue.analytic_acc_id and venue.analytic_acc_id.parent_id and venue.analytic_acc_id.parent_id.id or False
            domain = {'analytic_acc_id': [('id', 'in', (analytic_acc_id, parent_id))]}
            return {
                'value': {
                    'analytic_acc_id': venue.analytic_acc_id and venue.analytic_acc_id.id or False,
                    'academy_id': venue.management_id and venue.management_id.id or False,
                },
                'domain': domain
            }
        return {}


    def od_session_end(self):
        self.write({'state': 'done'})


    def set_to_draft(self):
        self.write({'state': 'draft'})

    def get_month_day_range(self, date):
        last_day = date + relativedelta(day=1, months=+1, days=-1)
        first_day = date + relativedelta(day=1)
        return first_day, last_day

    def od_generate_rent(self, date):
        existing_ids = []
        obj = self.env['od.activities'].browse(cr, uid, ids, context)
        types = obj.types
        fees = obj.fees
        start_date = obj.start_date
        venue_id = obj.venue_id and obj.venue_id.id
        end_date = obj.end_date
        start_date = datetime.datetime.strptime(str(start_date), "%Y-%m-%d")
        end_date = datetime.datetime.strptime(str(end_date), "%Y-%m-%d") + timedelta(days=1)
        no_of_days = (end_date - start_date).days or 1
        if no_of_days < 0:
            raise UserError(_("start_date should not be greater than end_date"))
        #        month_difference = ((end_date).month) - ((start_date).month)
        #        month_difference = math.fabs(((end_date).month) - ((start_date).month))
        month_difference = math.fabs((start_date.year - end_date.year) * 12 + start_date.month - end_date.month)
        print(":::::::::::::", month_difference)
        period_pool = self.env['account.period']
        search_periods = period_pool.find(obj.start_date)
        period_id = search_periods[0]
        period_ids = self.env['account.period'].browse(period_id)
        print("JJJJJJJJ", period_ids)
        for line in obj.rental_line:
            existing_ids.append(line.id)
        self.env['od.activities.rental.line'].unlink(existing_ids)
        if not period_id:
            raise UserError(_("there is no period defined for this date"))
        if month_difference == 0:
            diff = no_of_days
            ds = datetime.datetime.strptime(str(obj.start_date), "%Y-%m-%d")
            first_day, last_day = self.get_month_day_range(ds)
            print(":::::::::::", first_day, last_day)
            self.env['od.activities.rental.line'].create(
                {'period_id': period_ids.id, 'amount': (fees / no_of_days) * diff, 'venue_id': venue_id,
                 'activities_id': obj.id})
        if month_difference >= 1:
            ds = datetime.datetime.strptime(str(obj.start_date), "%Y-%m-%d")
            de = datetime.datetime.strptime(str(obj.end_date), "%Y-%m-%d")
            first_day_of_start_date, last_day_of_start_date = self.get_month_day_range(ds)
            first_day_of_end_date, last_day_of_end_date = self.get_month_day_range(de)
            period_for_ds_id = period_pool.find(obj.start_date)[0]
            period_for_de_id = period_pool.find(obj.end_date)[0]
            no_of_days_for_firstmonth = (last_day_of_start_date - ds).days + 1
            no_of_days_last_month = (de - first_day_of_end_date).days + 1
            self.env['od.activities.rental.line'].create(
                {'period_id': period_for_ds_id, 'amount': (fees / no_of_days) * no_of_days_for_firstmonth,
                 'venue_id': venue_id, 'activities_id': obj.id})
            next_date = last_day_of_start_date
            while next_date < last_day_of_end_date:
                next_date = next_date + relativedelta(months=1)
                first_day_of_next_date, last_day_of_next_date = self.get_month_day_range(next_date)
                if not last_day_of_next_date >= last_day_of_end_date:
                    first_day_of_next_date, last_day_of_next_date = self.get_month_day_range(next_date)
                    days_in_intermediate_month = (last_day_of_next_date - first_day_of_next_date).days + 1
                    period_days_in_intermediate_id = period_pool.find(next_date.strftime('%Y/%m/%d'))[0]
                    self.env['od.activities.rental.line'].create({'period_id': period_days_in_intermediate_id,
                                                                  'amount': (
                                                                                        fees / no_of_days) * days_in_intermediate_month,
                                                                  'venue_id': venue_id, 'activities_id': obj.id})
            self.env['od.activities.rental.line'].create(
                {'period_id': period_for_de_id, 'amount': (fees / no_of_days) * no_of_days_last_month,
                 'venue_id': venue_id, 'activities_id': obj.id})

    def onchange_types(self, types, start_date, end_date, fees):
        warning = {}
        if types == 'rental':
            start_date = self.start_date
            end_date = self.end_date
            if start_date and end_date:
                start_date = datetime.datetime.strptime(str(start_date), "%Y-%m-%d")
                end_date = datetime.datetime.strptime(str(end_date), "%Y-%m-%d") + timedelta(days=1)
                no_of_days = (end_date - start_date).days or 1
                if no_of_days < 0:
                    raise Warning(_("start_date should not be greater than end_date"))
                month_difference = ((end_date).month) - ((start_date).month)

                period_pool = self.env['account.period']
                search_periods = period_pool.find(start_date, )
                period_obj = search_periods[0]
                if not period_obj:
                    raise Warning(_("there is no period defined for this date"))

                if month_difference == 0:
                    diff = no_of_days
                    ds = datetime.datetime.strptime(str(start_date), "%Y-%m-%d")
                    first_day, last_day = self.get_month_day_range(ds)
                    self.env['od.activities.rental.line'].create(
                        {'period_id': period_obj.id, 'amount': (fees / no_of_days) * diff, })
                    # period_ids = self.env['account.period'].browse(period_id)
            return True

    def generate_invoice(self, cr, uid, ids, context):
        obj = self.browse(cr, uid, ids, context)
        customer_id = obj.customer_id and obj.customer_id.id
        product_id = obj.product_id and obj.product_id.id
        analytic_acc_id = obj.analytic_acc_id and obj.analytic_acc_id.id
        invoice_id = self.pool.get('account.move').create(cr, uid,
                                                          {'payment_type': 'cust_payment', 'partner_id': customer_id})
        return True


    def onchange_start_date(self, start_date):
        if start_date:
            return {
                'value': {
                    'types': 'camp',
                }}
        return {}


    def onchange_end_date(self, end_date):
        if end_date:
            return {
                'value': {
                    'types': 'camp',
                }}
        return {}





    @api.constrains('coach_percentage', 'academy_percentage', 'no_of_class', 'start_date', 'end_date')
    def _check_constriant(self):
        academy_percentage = self.academy_percentage
        coach_percentage = self.coach_percentage
        start_date = self.start_date
        end_date = self.end_date
        no_of_class = self.no_of_class
        if no_of_class <= 0:
            raise UserError(_("no of classes should be greater than zero"))

        if academy_percentage < 0 or coach_percentage < 0:
            raise UserError(_("percentage cannot be -ve value"))

        if academy_percentage > 100 or coach_percentage > 100:
            raise UserError(_("percentage cannot be greater than 100"))
        if start_date > end_date:
            raise UserError(_("start_date should not be greater than end_date"))


class od_activities_rental_line(models.Model):
    _name = 'od.activities.rental.line'
    activities_id = fields.Many2one('od.activities', string='Activity', ondelete='cascade')
    venue_id = fields.Many2one('od.venue', string='Venue')
    period_id = fields.Many2one('account.period', string='Period')
    amount = fields.Float(string='Amount')
    posted_flag = fields.Boolean(string='Posted')


class OdCampType(models.Model):
    _name = "od.camp.type"
    _description = "Camp Type"

    name = fields.Char(string="Name", )
    remarks = fields.Text(string="Remarks")
    cost_centre_id = fields.Many2one(
        "orchid.account.cost.center",
        string="Cost Centre",    )

class od_activities_camp_line(models.Model):
    _name = 'od.activities.camp.line'

    #
    #     def onchange_type_id(self,type_id,parent):
    #         cost_centre = ""
    #         comm = ""
    #         if parent.coach_id:
    #             partner_obj = self.env['res.partner'].browse(parent.coach_id)
    #             comm = partner_obj.od_percent
    #         if type_id:
    #             type_obj = self.env['od.camp.type'].browse(type_id)
    #             cost_centre = type_obj.cost_centre_id and type_obj.cost_centre_id.id
    #         vals = {}
    #         vals.update({'commission': comm,'cost_centre_id':cost_centre})
    #         self.write(vals)
    #         return {
    #             'value': {
    #                 'commission': comm,
    #                 'cost_centre_id':cost_centre
    #             }
    #         }
    #
    #
    #     # TODO:  removed in newer Odoo; refactor for recordsets
    # #
    #     @api.depends('no_of_class','fees','registration_fee')
    #     def _compute_total(self):
    #         total = (self.no_of_class * self.fees) + self.registration_fee
    #
    #     # TODO:  removed in newer Odoo; refactor for recordsets
    # #
    @api.depends('t1', 't1_fee', 't1_reg')
    def _compute_t1_total(self):
        for rec in self:
            rec.t1_total = (rec.t1 * rec.t1_fee) + rec.t1_reg

    #     # TODO:  removed in newer Odoo; refactor for recordsets
    # #
    #     @api.depends('t2','t2_fee','t2_reg')
    def _compute_t2_total(self):
        for rec in self:
            rec.t2_total = (rec.t2 * rec.t2_fee) + rec.t2_reg

    #     # TODO:  removed in newer Odoo; refactor for recordsets
    # #
    @api.depends('t3', 't3_fee', 't3_reg')
    def _compute_t3_total(self):
        for rec in self:
            rec.t3_total = (rec.t3 * rec.t3_fee) + rec.t3_reg

    activities_id = fields.Many2one('od.activities', string='Activity', ondelete='cascade')
    type_id = fields.Many2one('od.camp.type', string='Type')
    fees = fields.Float(string='Fees')
    product_id = fields.Many2one('product.product', string='Term/Product')
    t1 = fields.Float(string='T1 Class')
    t1_reg = fields.Float(string='T1 Reg.Fee')
    t1_fee = fields.Float(string='T1 Fee')
    t1_total = fields.Float(string='T1 Total', compute='_compute_t1_total', compute_sudo=True)
    t2 = fields.Float(string='T2 Class')
    t2_reg = fields.Float(string='T2 Reg.Fee')
    t2_fee = fields.Float(string='T2 Fee')
    t2_total = fields.Float(string='T2 Total', compute='_compute_t2_total', compute_sudo=True)
    t3 = fields.Float(string='T3 Class')

    t3_reg = fields.Float(string='T3 Reg.Fee')
    t3_fee = fields.Float(string='T3 Fee')
    t3_total = fields.Float(string='T3 Total', compute='_compute_t3_total', compute_sudo=True)
    no_of_class = fields.Float(string='No.of Class')
    registration_fee = fields.Float(string="Registration Fee")
    total_fee = fields.Float(string='Total', digits=dp.get_precision('Account'), readonly=True,
                             compute='_compute_total')
    remarks = fields.Char(string='Remarks')
    commission = fields.Float(string='Commission')
    cost_centre_id = fields.Many2one('orchid.account.cost.center', string='Cost Centre', compute='_get_cost_centre_id', compute_sudo=True)

    # _sql_constraints = [
    # ('activities_type_uniq', 'unique (activities_id,type_id)', 'Type  should be unique for Activity!')
    # ]

    def od_generate_entry(self):
        return True


    @api.depends('type_id')
    def _get_cost_centre_id(self):
        for rec in self:
            rec.update({
                'cost_centre_id': rec.type_id.cost_centre_id and rec.type_id.cost_centre_id.id or None,

            })


class od_registration_line(models.Model):
    _name = 'od.registration.line'

    #
    # def onchange_partner_id(self,partner_id):
    #     if partner_id:
    #         partner = self.env['res.partner'].browse(partner_id)
    #         return {
    #             'value': {
    #                 'rv_no': partner.mobile or '',
    #                 'email': partner.email or '',
    #                 'od_dob': partner.od_dob or '',
    #             }
    #         }
    #     return {}
    #
    #     # TODO:  removed in newer Odoo; refactor for recordsets
    # #
    @api.depends('partner_id')
    def _compute_from_partner(self):
        for rec in self:
            rec.rv_no = rec.partner_id and rec.partner_id.mobile or False
            rec.email = rec.partner_id and rec.partner_id.email or False
            rec.od_dob = rec.partner_id and rec.partner_id.od_dob or False
            rec.city = rec.partner_id and rec.partner_id.city or False
            rec.school_id = rec.partner_id and rec.partner_id.school_id and rec.partner_id.school_id.id or False

    activities_id = fields.Many2one('od.activities', string='Activity', ondelete='cascade')
    rv_no = fields.Char(string='Mobile No', readonly=True, compute='_compute_from_partner', compute_sudo=True)
    partner_id = fields.Many2one('res.partner', string='Student', required=True)
    amount = fields.Float(string='Amount')
    payment_type_account_id = fields.Many2one('account.account', string='Account',
                                              domain=[('type', 'not in', ['view', 'consolidation', 'closed'])])
    remarks = fields.Char(string='Cheque No')
    allergies = fields.Boolean(string='Allergies')
    transportation = fields.Boolean(string='Transportation')
    no_of_classes = fields.Float(string='No Of Class')
    email = fields.Char(string='Email', compute='_compute_from_partner', compute_sudo=True)
    od_dob = fields.Date(string='DOB', compute='_compute_from_partner', compute_sudo=True)
    week_ids = fields.Many2many('od.sports.date.selection', 'registration_id', 'name', string='Weeks')
    types = fields.Selection([
        ('full', 'Full'),
        ('partial', 'Partial'),
    ], string='Type', default='full')
    school_id = fields.Many2one('orchid.school', string='School', compute='_compute_from_partner', compute_sudo=True)
    city = fields.Char(string='City', compute='_compute_from_partner', compute_sudo=True)


class od_sports_date_selection(models.Model):
    _name = "od.sports.date.selection"
    _description = "Date Selection"
    name = fields.Date(string='Date', required=True)
    notes = fields.Text(string='Note')
