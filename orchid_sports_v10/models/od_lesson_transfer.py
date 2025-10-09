# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
import datetime


class od_lesson_transfer(models.Model):
    _name = 'od.lesson.transfer'
    _description = 'Lesson Transfer'
    _order = 'date desc'

    date = fields.Date(string='Date')
    name = fields.Char(string='Name', default='/')
    od_activities_id = fields.Many2one('od.activities', string="Program")
    od_term_id = fields.Many2one('od.terms', string='Term')
    lesson_line = fields.One2many('od.lesson.transfer.line', 'lesson_id', string='Lesson Transfer Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft')
    move_id = fields.Many2one('account.move', string='Journal Number', readonly=True, copy=False)

    #
    # 	# TODO:  removed in newer Odoo; refactor for recordsets
    #
    def set_to_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        move_id = self.move_id and self.move_id.id
        if move_id:
            self.move_id.button_cancel()
            self.move_id.unlink()
        self.state = 'cancel'
        return True

    def action_process(self):
        collection_obj = self.env['od.sports.receipt']
        lesson_obj = self.env['od.lesson.transfer']
        lines = []
        dic_data = {}
        self.lesson_line.unlink()
        date = self.date
        activity_id = self.od_activities_id and self.od_activities_id.id or False
        collection_ids = collection_obj.search(
            [('activities_id', '=', activity_id), ('date', '<=', date), ('state', '=', 'confirm')])
        for collection_id in collection_ids:
            for line in collection_id.receipt_line:
                partner_id = line.partner_id and line.partner_id.id or False
                type_id = line.type_id and line.type_id.id or False
                od_amount = line.amount or 0.0
                od_transportation = line.transportation or 0.0
                od_coach_commision = line.coach_commision or 0.0
                od_no_of_clases = line.no_of_clases or 0.0
                if partner_id in dic_data:
                    if type_id in dic_data[partner_id]:
                        dic_data[partner_id][type_id]['receipt_line_id'] = line.id
                        dic_data[partner_id][type_id]['od_amount'] += od_amount
                        dic_data[partner_id][type_id]['od_transportation'] += od_transportation
                        dic_data[partner_id][type_id]['od_coach_commision'] += od_coach_commision
                        dic_data[partner_id][type_id]['od_no_of_clases'] += od_no_of_clases
                        dic_data[partner_id][type_id][
                            'old_venue_id'] = collection_id.venue_id and collection_id.venue_id.id
                    else:
                        dic_data[partner_id][type_id] = {}
                        dic_data[partner_id][type_id]['receipt_line_id'] = line.id
                        dic_data[partner_id][type_id]['od_amount'] = od_amount
                        dic_data[partner_id][type_id]['od_transportation'] = od_transportation
                        dic_data[partner_id][type_id]['od_coach_commision'] = od_coach_commision
                        dic_data[partner_id][type_id]['od_no_of_clases'] = od_no_of_clases
                        dic_data[partner_id][type_id][
                            'old_venue_id'] = collection_id.venue_id and collection_id.venue_id.id
                else:
                    dic_data[partner_id] = {}
                    dic_data[partner_id][type_id] = {}
                    dic_data[partner_id][type_id]['receipt_line_id'] = line.id
                    dic_data[partner_id][type_id]['od_amount'] = od_amount
                    dic_data[partner_id][type_id]['od_transportation'] = od_transportation
                    dic_data[partner_id][type_id]['od_coach_commision'] = od_coach_commision
                    dic_data[partner_id][type_id]['od_no_of_clases'] = od_no_of_clases
                    dic_data[partner_id][type_id]['old_venue_id'] = collection_id.venue_id and collection_id.venue_id.id
        for partner_id, value in dic_data.items():
            data = {}
            for type_id, type_value in value.items():
                data = {
                    'od_partner_id': partner_id,
                    'od_type_id': type_id,
                    'od_amount': type_value['od_amount'],
                    'od_transportation': type_value['od_transportation'],
                    'od_coach_commision': type_value['od_coach_commision'],
                    'od_no_of_clases': type_value['od_no_of_clases'],
                    'receipt_line_id': type_value['receipt_line_id'],
                    'old_venue_id': type_value['old_venue_id'],
                }
                print(data)
                lines.append((0, 0, data))
        print(lines)
        self.update({'lesson_line': lines})

    def action_confirm(self):
        data_lines = []
        name = '/'
        if self.move_id:
            raise UserError(_('Entry already created!!'))
        tranfr_journal = self.od_activities_id and self.od_activities_id.transfer_journal_id and self.od_activities_id.transfer_journal_id.id
        if not tranfr_journal:
            raise UserError(_('Journal not found'))
        if self.name == '/':
            lesson_seq = self.od_activities_id.transfer_journal_id and self.od_activities_id.transfer_journal_id.sequence_id
            if not lesson_seq:
                raise UserError(_('Transfer Entry Sequence not set'))
            name = lesson_seq.with_context(ir_sequence_date=self.date).next_by_id() or '/'
            self.name = name
        else:
            name = self.name

        for line in self.lesson_line:
            if not line.od_new_activities_id:
                raise UserError(_('Some Programe is not set in line!!'))
            revenue_acc = self.od_activities_id and self.od_activities_id.nonrevenue_account_id and self.od_activities_id.nonrevenue_account_id.id
            registration_acc = self.od_activities_id and self.od_activities_id.registration_acc_id and self.od_activities_id.registration_acc_id.id
            coach_comm_exp_acc = self.od_activities_id and self.od_activities_id.coach_comm_exp_id and self.od_activities_id.coach_comm_exp_id.id
            old_coach = self.od_activities_id and self.od_activities_id.coach_id
            old_coach_acc = old_coach.property_account_payable_id and old_coach.property_account_payable_id.id
            new_coach = line.od_new_activities_id and line.od_new_activities_id.coach_id
            new_coach_acc = new_coach.property_account_payable_id and new_coach.property_account_payable_id.id
            student = line.od_partner_id
            product_id = self.od_term_id and self.od_term_id.product_id and self.od_term_id.product_id.id
            cc_id = line.od_type_id and line.od_type_id.cost_centre_id and line.od_type_id.cost_centre_id.id
            analytic_account_id = line.venue_id.analytic_acc_id and line.venue_id.analytic_acc_id.id
            old_analytic_account_id = line.old_venue_id.analytic_acc_id and line.old_venue_id.analytic_acc_id.id
            if line.od_trn_amount > 0:
                trn_amount_dr = (0, 0, {
                    'date': self.date,
                    'name': student.name,
                    'account_id': revenue_acc,
                    'debit': line.od_trn_amount,
                    'credit': 0,
                    'orchid_cc_id': cc_id or False,
                    'partner_id': old_coach and old_coach.id,
                    'product_id': product_id,
                    'analytic_account_id': old_analytic_account_id,
                })

                trn_amount_cr = (0, 0, {
                    'date': self.date,
                    'name': student.name,
                    'account_id': revenue_acc,
                    'credit': line.od_trn_amount,
                    'debit': 0,
                    'orchid_cc_id': cc_id or False,
                    'partner_id': new_coach and new_coach.id,
                    'product_id': product_id,
                    'analytic_account_id': analytic_account_id,
                })
                data_lines.append(trn_amount_dr)
                data_lines.append(trn_amount_cr)
            if line.od_trn_transportation > 0:
                trn_transp_dr = (0, 0, {

                    'date': self.date,
                    'name': student.name,
                    'account_id': registration_acc,
                    'debit': line.od_trn_transportation,
                    'credit': 0,
                    'orchid_cc_id': cc_id or False,
                    'partner_id': old_coach and old_coach.id,
                    'product_id': product_id,
                    'analytic_account_id': old_analytic_account_id,
                })

                trn_transp_cr = (0, 0, {

                    'date': self.date,
                    'name': student.name,
                    'account_id': registration_acc,
                    'credit': line.od_trn_transportation,
                    'debit': 0,
                    'orchid_cc_id': cc_id or False,
                    'partner_id': new_coach and new_coach.id,
                    'product_id': product_id,
                    'analytic_account_id': analytic_account_id,
                })
                data_lines.append(trn_transp_dr)
                data_lines.append(trn_transp_cr)

            if line.od_trn_coach_comm > 0:
                trn_coach_dr = (0, 0, {

                    'date': self.date,
                    'name': old_coach.name,
                    'account_id': old_coach_acc,
                    'debit': line.od_trn_coach_comm,
                    'credit': 0,
                    'orchid_cc_id': cc_id or False,
                    'partner_id': old_coach and old_coach.id,
                    'product_id': product_id,
                    'analytic_account_id': old_analytic_account_id,
                })
                trn_coach_cr = (0, 0, {

                    'date': self.date,
                    'name': old_coach.name,
                    'account_id': coach_comm_exp_acc,
                    'credit': line.od_trn_coach_comm,
                    'debit': 0,
                    'orchid_cc_id': cc_id or False,
                    'partner_id': old_coach and old_coach.id,
                    'product_id': product_id,
                    'analytic_account_id': old_analytic_account_id,
                })
                data_lines.append(trn_coach_dr)
                data_lines.append(trn_coach_cr)

            if line.od_new_coach_comm > 0:
                new_coach_dr = (0, 0, {

                    'date': self.date,
                    'name': new_coach.name,
                    'account_id': new_coach_acc,
                    'credit': line.od_new_coach_comm,
                    'debit': 0,
                    'orchid_cc_id': cc_id or False,
                    'partner_id': new_coach and new_coach.id,
                    'product_id': product_id,
                    'analytic_account_id': analytic_account_id,
                })
                new_coach_cr = (0, 0, {

                    'date': self.date,
                    'name': new_coach.name,
                    'account_id': coach_comm_exp_acc,
                    'debit': line.od_new_coach_comm,
                    'credit': 0,
                    'orchid_cc_id': cc_id or False,
                    'partner_id': new_coach and new_coach.id,
                    'product_id': product_id,
                    'analytic_account_id': analytic_account_id,
                })
                data_lines.append(new_coach_dr)
                data_lines.append(new_coach_cr)

        data = {
            'journal_id': tranfr_journal,
            'date': self.date,
            'state': 'draft',
            'ref': 'test',
            'name': name,
            'line_ids': data_lines
        }
        if data_lines:
            move_id = self.env['account.move'].create(data)
            move_id.post()
            self.write({'state': 'confirm', 'move_id': move_id.id})
        else:
            raise UserError(_('No Entries Found!!'))
        return True


class od_lesson_transfer_line(models.Model):
    _name = 'od.lesson.transfer.line'
    _description = 'Lesson Transfer Line'

    od_partner_id = fields.Many2one('res.partner', string='Student')
    od_type_id = fields.Many2one('od.camp.type', string='Fees Type')
    lesson_id = fields.Many2one('od.lesson.transfer', string='Lesson Transfer')
    od_amount = fields.Float(string='Fees')
    od_no_of_clases = fields.Float(string='Paid Lesson')
    od_transportation = fields.Float(string='Registration')
    venue_id = fields.Many2one('od.venue', string='Venue', )
    old_venue_id = fields.Many2one('od.venue', string='Venue', )
    od_coach_commision = fields.Float(string='Coach Comm.')
    od_trn_amount = fields.Float(string='T.Fees')
    od_trn_no_of_clases = fields.Float(string='T. Lesson No.')
    od_trn_transportation = fields.Float(string='T.Registration')
    receipt_line_id = fields.Many2one('od.sports.receipt.line', string='Collection Line')
    od_new_activities_id = fields.Many2one('od.activities', string="New Program")
    od_trn_coach_comm = fields.Float(string='T. Coach Comm.', compute='compute_trn_coach_amt', store=True)
    od_trn_coach_per = fields.Float(string='T. Coach %')
    od_new_coach_per = fields.Float(string='New Coach %')
    od_new_coach_comm = fields.Float(string='New Coach Comm', compute='compute_new_coach_amt', store=True)


    @api.depends('od_trn_coach_per', 'od_trn_amount')
    def compute_trn_coach_amt(self):
        self.od_trn_coach_comm = self.od_trn_coach_per * self.od_trn_amount / 100


    @api.depends('od_new_coach_per', 'od_trn_amount')
    def compute_new_coach_amt(self):
        self.od_new_coach_comm = self.od_new_coach_per * self.od_trn_amount / 100
