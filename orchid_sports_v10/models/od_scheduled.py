# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


def simply(items):
    """Merge lines by partner_id and sum fees."""
    result = []
    for item in items:
        found = False
        for r in result:
            if item['partner_id'] == r['partner_id']:
                r['fees'] += item['fees']
                found = True
                break
        if not found:
            result.append(item)
    return result


class OdScheduled(models.Model):
    _name = 'od.scheduled'
    _description = 'Scheduled Session'
    _order = 'id desc'

    name = fields.Char(required=True, default='/')
    day = fields.Selection(
        [('sun', 'Sunday'), ('mon', 'Monday'), ('tue', 'Tuesday'),
         ('wed', 'Wednesday'), ('thu', 'Thursday'), ('fri', 'Friday'),
         ('sat', 'Saturday'), ('all', 'All')],
        string="Day", default='sun'
    )
    # time stored as float hours (e.g. 13.5 = 13:30)
    date_from = fields.Float(string="Time From")
    date_to = fields.Float(string="Time To")
    x_date_from = fields.Date(string="Date From")
    x_date_to = fields.Date(string="Date To")

    duration = fields.Float(string="Duration", compute="_compute_time_diff", store=False)
    activities_id = fields.Many2one('od.activities', string='Program', required=True)
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancel')],
        default='draft', string='Status'
    )
    venue_id = fields.Many2one('od.venue', string='Venue', readonly=True, states={'draft': [('readonly', False)]})
    coach_id = fields.Many2one('res.partner', string='Coach', compute='_compute_coach', store=True)
    percentage = fields.Float(string="Coach %", readonly=True, states={'draft': [('readonly', False)]})
    academy_id = fields.Many2one('res.partner', string='Academy', readonly=True)
    term_id = fields.Many2one('od.terms', string='Term')
    fees = fields.Float(string='Fees', readonly=True)
    no_of_class = fields.Integer(string='Number Of Class', readonly=True)
    scheduled_line = fields.One2many('od.scheduled.line', 'scheduled_id', copy=True, string='Scheduled Lines')
    cost_centre_id = fields.Many2one('orchid.account.cost.center', string='Cost Centre')
    tick_all = fields.Boolean('Select All')
    active = fields.Boolean(default=True)

    @api.depends('date_from', 'date_to')
    def _compute_time_diff(self):
        for rec in self:
            rec.duration = (rec.date_to or 0.0) - (rec.date_from or 0.0)

    @api.depends('activities_id')
    def _compute_coach(self):
        for rec in self:
            rec.coach_id = rec.activities_id.coach_id or False

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name or ''
            if rec.coach_id:
                name = f"{name} ({rec.coach_id.display_name})"
            res.append((rec.id, name))
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('od.scheduled') or '/'
        return super().create(vals)

    def action_confirm(self):
        for obj in self:
            # Count attended lines that are marked to create JV
            attended = sum(1 for l in obj.scheduled_line if l.jv)
            if attended == 0:
                raise UserError(_('No students attended.'))

            act = obj.activities_id
            if not act:
                raise UserError(_('Program (activities) is required.'))

            # Accounts & journal
            income_acc = act.income_account_id.id if getattr(act, 'income_account_id', False) else False
            prepaid_rev_acc = act.prepaid_revenue_account_id.id if getattr(act, 'prepaid_revenue_account_id', False) else False
            prepaid_exp_acc = act.prepaid_expense_account_id.id if getattr(act, 'prepaid_expense_account_id', False) else False
            academy_comm_acc = act.academy_commission_acc_id.id if getattr(act, 'academy_commission_acc_id', False) else False
            provider_comm_acc = act.provider_commission_acc_id.id if getattr(act, 'provider_commission_acc_id', False) else False
            journal = act.attendance_journal_id

            if not income_acc:
                raise UserError(_('Define income account in activities.'))
            if not academy_comm_acc:
                raise UserError(_('Define academy commission account in activities.'))
            if not provider_comm_acc:
                raise UserError(_('Define provider commission account in activities.'))
            if not prepaid_exp_acc:
                raise UserError(_('Define prepaid expense account in activities.'))
            if not prepaid_rev_acc:
                raise UserError(_('Define prepaid revenue account in activities.'))
            if not journal:
                raise UserError(_('Define attendance journal in activities.'))
            if not obj.coach_id:
                raise UserError(_('Define coach in the schedule/program.'))

            # Compute fees from attended types
            fees_amount = 0.0
            CampLine = self.env['od.activities.camp.line']
            for line in obj.scheduled_line:
                if not line.jv or not line.type_id:
                    continue
                fee_line = CampLine.search([
                    ('activities_id', '=', act.id),
                    ('type_id', '=', line.type_id.id),
                ], limit=1)
                if not fee_line:
                    raise UserError(_("Please check the fee structure for the selected type: %s") % line.type_id.display_name)
                unit_fee = (fee_line.fees or 0.0) / (fee_line.no_of_class or 1.0)
                fees_amount += unit_fee

            coach_perc = obj.percentage or 0.0
            academy_perc = act.academy_percentage or 0.0
            x_c = round((fees_amount * coach_perc) / 100.0, 2)
            y_a = round((fees_amount * academy_perc) / 100.0, 2)

            # Optional analytic
            analytic = getattr(obj.venue_id, 'analytic_acc_id', False)
            analytic_distribution = {analytic.id: 100} if analytic else False

            def ml(name, account_id, debit=0.0, credit=0.0, partner=False, product=False):
                vals = {
                    'name': name,
                    'account_id': account_id,
                    'debit': debit,
                    'credit': credit,
                    'partner_id': partner.id if partner else False,
                    'product_id': product.id if product else False,
                }
                if analytic_distribution:
                    vals['analytic_distribution'] = analytic_distribution
                return (0, 0, vals)

            lines = []
            # Income vs prepaid revenue (recognition placeholder)
            if coach_perc > 0 or academy_perc > 0 or (coach_perc == 0 and academy_perc == 0):
                lines.append(ml('Attendance', income_acc, debit=0.0, credit=fees_amount, product=getattr(act, 'product_id', False)))
                lines.append(ml('Attendance', prepaid_rev_acc, debit=fees_amount, credit=0.0, product=getattr(act, 'product_id', False)))

            # Provider (coach) commission
            if coach_perc > 0:
                lines.append(ml('Coach Commission', provider_comm_acc, debit=x_c, credit=0.0, partner=obj.coach_id))
                # Credit payable to coach
                coach_payable = obj.coach_id.property_account_payable_id.id
                if not coach_payable:
                    raise UserError(_("Configure payable account on coach partner: %s") % obj.coach_id.display_name)
                lines.append(ml('Coach Payable', coach_payable, debit=0.0, credit=x_c, partner=obj.coach_id))

            # Academy commission
            if academy_perc > 0:
                lines.append(ml('Academy Commission', academy_comm_acc, debit=y_a, credit=0.0, partner=act.academy_id))
                # Reverse prepaid expense (credit)
                lines.append(ml('Prepaid Expense Adjust', prepaid_exp_acc, debit=0.0, credit=y_a, partner=act.academy_id))

            move_vals = {
                'move_type': 'entry',
                'journal_id': journal.id,
                'date': fields.Date.context_today(self),
                'ref': 'Attendance Entry',
                'line_ids': lines,
            }
            move = self.env['account.move'].create(move_vals)
            # post if you want it finalized; keep draft if you prefer manual check
            # move.action_post()

            obj.write({'state': 'confirm', 'move_id': move.id})

    def action_cancel(self):
        for rec in self:
            if rec.move_id:
                # If posted, unpost before unlink (optional, depends on your flow)
                if rec.move_id.state == 'posted':
                    rec.move_id.button_draft()
                rec.move_id.unlink()
            rec.state = 'cancel'

    def set_to_draft(self):
        self.state = 'draft'

    @api.onchange('activities_id')
    def _onchange_activities_id(self):
        if self.activities_id:
            self.venue_id = self.activities_id.venue_id
            self.coach_id = self.activities_id.coach_id
            self.academy_id = self.activities_id.academy_id
            self.fees = self.activities_id.fees
            self.no_of_class = self.activities_id.no_of_class

    @api.onchange('tick_all')
    def _onchange_tick_all(self):
        if self.tick_all:
            for line in self.scheduled_line:
                line.tick_me = True

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete it; it is not in Draft.'))
        return super().unlink()

    def od_fill(self):
        for obj in self:
            obj.scheduled_line.unlink()
            activities_id = obj.activities_id.id if obj.activities_id else False
            cost_centre_id = obj.cost_centre_id.id if obj.cost_centre_id else False
            receipts = self.env['od.sports.receipt'].search([('activities_id', '=', activities_id)])
            tmp = []
            for r in receipts:
                for rl in r.receipt_line:
                    type_cc = getattr(rl.type_id, 'cost_centre_id', False)
                    type_cc_id = type_cc.id if type_cc else False
                    if cost_centre_id == type_cc_id:
                        tmp.append({
                            'partner_id': rl.partner_id.id if rl.partner_id else False,
                            'fees': rl.amount or 0.0,
                            'type_id': rl.type_id.id if rl.type_id else False,
                            'scheduled_id': obj.id,
                        })
            for vals in simply(tmp):
                self.env['od.scheduled.line'].create(vals)

    def od_delete_me(self):
        for line in self.scheduled_line:
            if line.tick_me:
                line.unlink()
        self.tick_all = False


class OdScheduledLine(models.Model):
    _name = 'od.scheduled.line'
    _description = 'Scheduled Line'

    scheduled_id = fields.Many2one('od.scheduled', string='Schedule', ondelete='cascade')
    mobile_no = fields.Char(string='Mobile No', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Student', required=True)
    type_id = fields.Many2one('od.camp.type', string='Type')
    fees = fields.Float(string='Fees')
    remarks = fields.Char(string='Remarks')
    attendance = fields.Boolean(string='Attendance')
    jv = fields.Boolean(string='JV')
    tick_me = fields.Boolean('Select')
    no_of_classes = fields.Float('No.of Classes')

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        # Ensure registration exists
        if rec.scheduled_id and rec.partner_id and rec.scheduled_id.activities_id:
            RegistrationLine = self.env['od.registration.line']
            existing = RegistrationLine.search([
                ('activities_id', '=', rec.scheduled_id.activities_id.id),
                ('partner_id', '=', rec.partner_id.id),
            ], limit=1)
            if not existing:
                RegistrationLine.create({
                    'activities_id': rec.scheduled_id.activities_id.id,
                    'partner_id': rec.partner_id.id,
                    'rv_no': rec.partner_id.mobile or '',
                })
        return rec

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.mobile_no = self.partner_id.mobile or ''

    @api.onchange('attendance')
    def _onchange_attendance(self):
        if not self.attendance:
            self.jv = False

    @api.onchange('type_id')
    def _onchange_type_id(self):
        if self.scheduled_id and self.scheduled_id.activities_id:
            ids_allowed = []
            for cl in self.scheduled_id.activities_id.camp_line:
                if cl.type_id:
                    ids_allowed.append(cl.type_id.id)
            return {'domain': {'type_id': [('id', 'in', ids_allowed)]}}
        return {}
