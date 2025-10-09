# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class OdRefundEntry(models.Model):
    _name = 'od.refund.entry'
    _description = 'Refund Entry'
    _order = 'date desc'

    od_activities_id = fields.Many2one('od.activities', string="Program")
    partner_id = fields.Many2one('res.partner', string="Student")
    od_term_id = fields.Many2one('od.terms', string='Term')
    refund_line = fields.One2many('od.refund.entry.line', 'refund_id', string='Refund Lines')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    reason = fields.Char(string='Reason')
    name = fields.Char(string='Name', default='/', copy=False)
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft')

    total_amount = fields.Float(string='Total Amount', compute='compute_total', compute_sudo=True, store=False)
    total_refund_amt = fields.Float(string='Refund Amount', compute='compute_total', compute_sudo=True, store=False)
    total_reg_amount = fields.Float(string='Reg Amount', compute='compute_total', compute_sudo=True, store=False)
    total_vat_amount = fields.Float(string='Vat', compute='compute_total', compute_sudo=True, store=False)
    total_coach_comm = fields.Float(string='Coach Commission', compute='compute_total', compute_sudo=True, store=False)
    total_venue_comm = fields.Float(string='Venue Commission', compute='compute_total', compute_sudo=True, store=False)
    subtotal = fields.Float(string='Subtotal', compute='compute_total', compute_sudo=True, store=False)

    od_payment_return_account_id = fields.Many2one('account.account', string='Refund Payment Account')

    # --------------------------
    # State actions
    # --------------------------
    def set_to_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        for rec in self:
            if rec.move_id:
                if rec.move_id.state == 'posted':
                    rec.move_id.button_draft()
                rec.move_id.unlink()
            rec.state = 'cancel'

        # --------------------------
        # Helpers
        # --------------------------
    def _next_name_from_journal(self, journal):
        """Return next sequence name for this refund doc.

        Supports both journal.sequence_id (v14+ core) and journal.sequence (your DB),
        and finally falls back to an ir.sequence code.
        """
        if not journal:
            return '/'

        # date-aware numbering
        seq_ctx = {'ir_sequence_date': self.date or fields.Date.context_today(self)}

        # 1) Preferred: sequence_id (Odoo 14+)
        seq = getattr(journal, 'sequence_id', False)
        if seq:
            return seq.with_context(seq_ctx).next_by_id() or '/'

        # 2) Alternate: sequence (your environment)
        seq_alt = getattr(journal, 'sequence', False)
        if seq_alt:
            # if it's a Many2one to ir.sequence this works:
            if hasattr(seq_alt, 'next_by_id'):
                return seq_alt.with_context(seq_ctx).next_by_id() or '/'
            # if it's a code string, try next_by_code:
            if isinstance(seq_alt, str):
                return self.env['ir.sequence'].with_context(seq_ctx).next_by_code(seq_alt) or '/'

        # 3) Fallback to a dedicated code for this model (optional: create this sequence in data)
        return self.env['ir.sequence'].with_context(seq_ctx).next_by_code('od.refund.entry') or '/'

    # --------------------------
    # Main flow
    # --------------------------
    def _get_tax_refund_account(self, tax):
        """Pick the correct tax account for refunds in v18.

        - Tries refund repartition lines first, then invoice lines.
        - Handles group taxes by recursing into children.
        - Returns the first 'tax' repartition line with an account.
        """
        if not tax:
            return False

        company = self.env.company

        def pick_from_single(_tax):
            # Prefer refund lines; fallback to invoice lines
            lines = (_tax.refund_repartition_line_ids or _tax.invoice_repartition_line_ids).filtered(
                lambda l: l.repartition_type == 'tax'
                          and l.account_id
                          and (not l.company_id or l.company_id == company)
            )
            return lines[:1].account_id.id if lines else False

        # 1) Direct on this tax
        acc_id = pick_from_single(tax)
        if acc_id:
            return acc_id

        # 2) If it's a group tax, try children recursively
        if getattr(tax, 'children_tax_ids', False):
            for child in tax.children_tax_ids:
                acc_id = pick_from_single(child) or self._get_tax_refund_account(child)
                if acc_id:
                    return acc_id

        # 3) Nothing found
        return False


    def action_generate(self):
        """Load refundable collection lines for selected program/term/student into refund_line."""
        self.ensure_one()
        activities_id = self.od_activities_id.id or False
        term_id = self.od_term_id.id or False
        partner_id = self.partner_id.id or False
        self.refund_line.unlink()

        if not (activities_id and term_id and partner_id):
            return

        receipts = self.env['od.sports.receipt'].search([
            ('activities_id', '=', activities_id),
            ('term_id', '=', term_id),
        ])
        if not receipts:
            return

        lines = self.env['od.sports.receipt.line'].search([
            ('partner_id', '=', partner_id),
            ('receipt_id', 'in', receipts.ids),
        ])

        data = []
        for cl in lines:
            data.append((0, 0, {
                'od_rv_no': cl.rv_no,
                'od_partner_id': cl.partner_id.id,
                'od_payment_type_account_id': cl.payment_type_account_id.id if cl.payment_type_account_id else False,
                'od_type_id': cl.type_id.id if cl.type_id else False,
                'od_remarks': cl.remarks,
                'od_date': cl.date,
                'od_amount': cl.amount,
                'od_coach_commision': cl.coach_commision,
                'od_no_of_clases': cl.no_of_clases,
                'od_transportation': cl.transportation,
                'od_total': cl.total,
                'od_vat_id': cl.od_vat_id.id if cl.od_vat_id else False,
                'od_vat_amount': cl.od_vat_amount,
                'od_grand_total': cl.grand_total,
                'od_venue_commission': cl.od_venue_commission,
                'od_collection_id': cl.receipt_id.id if cl.receipt_id else False,
                'od_collection_line_id': cl.id,
            }))

        if data:
            self.update({'refund_line': data})

    def _analytic_dist(self,analytic):
        """Return v18 analytic_distribution for a single analytic account."""
        return {str(analytic): 100} if analytic else False


    def action_confirm(self):
        self.ensure_one()
        if self.move_id:
            raise UserError(_('Entry already created.'))

        act = self.od_activities_id
        if not act:
            raise UserError(_('Select a Program.'))

        product = self.od_term_id.product_id if self.od_term_id else False
        journal = act.return_journal_id
        if not journal:
            raise UserError(_('Define a Return Journal on the Program.'))

        # Generate document name if needed
        if self.name == '/':
            self.name = self._next_name_from_journal(journal)

        # Accounts
        nonrevenue_account = act.nonrevenue_account_id.id if getattr(act, 'nonrevenue_account_id', False) else False
        if not nonrevenue_account:
            raise UserError(_('Revenue (nonrevenue) account not set on Program.'))

        registration_acc = act.registration_acc_id.id if getattr(act, 'registration_acc_id', False) else False
        if not registration_acc:
            raise UserError(_('Registration account not set on Program.'))

        coach_payable = (act.coach_id.property_account_payable_id.id
                         if (act.coach_id and act.coach_id.property_account_payable_id) else False)
        if not coach_payable:
            raise UserError(_('Coach partner payable account not set.'))

        academy_comm_exp = act.academy_comm_exp_id.id if getattr(act, 'academy_comm_exp_id', False) else False
        if not academy_comm_exp:
            raise UserError(_('Academy commission expense account not set.'))

        coach_comm_exp = act.coach_comm_exp_id.id if getattr(act, 'coach_comm_exp_id', False) else False
        if not coach_comm_exp:
            raise UserError(_('Coach commission expense account not set.'))

        pay_return_acc = self.od_payment_return_account_id.id if self.od_payment_return_account_id else False
        if not pay_return_acc:
            raise UserError(_('Select the Refund Payment Account.'))

        if not self.refund_line:
            raise UserError(_('No refund lines.'))

        # Build move lines
        aml = []
        move_date = self.date or fields.Date.context_today(self)
        nm = self.name
        analytic_account_id = False  # will be set per-line when available

        # venue management payable (same for all lines, derived from the first line/receipt venue)
        venue_mgmt_payable = False
        venue_mgmt_partner = False
        first_receipt = self.refund_line[:1].od_collection_id
        if first_receipt and first_receipt.venue_id and first_receipt.venue_id.management_id:
            mgmt_partner = first_receipt.venue_id.management_id
            venue_mgmt_partner = mgmt_partner.id
            venue_mgmt_payable = mgmt_partner.property_account_payable_id.id if mgmt_partner.property_account_payable_id else False
        if not venue_mgmt_payable:
            # Only needed if any venue commission is present; we’ll re-check later
            pass

        total_vat = 0.0

        for ln in self.refund_line:
            cost_centre_id = getattr(ln.od_type_id, 'cost_centre_id', False)
            cost_centre_id = cost_centre_id.id if cost_centre_id else False
            analytic_account_id = (ln.od_collection_id.venue_id.analytic_acc_id.id
                                   if (ln.od_collection_id and ln.od_collection_id.venue_id
                                       and ln.od_collection_id.venue_id.analytic_acc_id) else False)

            vat_acc_id = self._get_tax_refund_account(ln.od_vat_id)

            if ln.od_refund_vat_amount and not vat_acc_id:
                raise UserError(_('No tax account found on tax repartition lines for: %s') % (ln.od_vat_id.display_name,))
            if ln.od_refund_vat_amount and not vat_acc_id:
                raise UserError(_('Refund VAT account is missing on the selected VAT: %s') % (ln.od_vat_id.display_name if ln.od_vat_id else ''))

            # Debit refund of fees (nonrevenue) and registration (registration_acc)
            if ln.od_refund_amount > 0:
                aml.append((0, 0, {
                    'date': move_date,
                    'name': nm,
                    'account_id': nonrevenue_account,
                    'debit': ln.od_refund_amount,
                    'credit': 0.0,
                    'orchid_cc_id': cost_centre_id,
                    'partner_id': act.coach_id.id if act.coach_id else False,
                    'product_id': product.id if product else False,
                    "analytic_distribution": self._analytic_dist(analytic_account_id),
                }))

            if ln.od_reg_refund_amount > 0:
                aml.append((0, 0, {
                    'date': move_date,
                    'name': nm,
                    'account_id': registration_acc,
                    'debit': ln.od_reg_refund_amount,
                    'credit': 0.0,
                    'orchid_cc_id': cost_centre_id,
                    'partner_id': act.coach_id.id if act.coach_id else False,
                    'product_id': product.id if product else False,
                    "analytic_distribution": self._analytic_dist(analytic_account_id),
                }))

            # Coach commission reversal: debit coach payable, credit coach commission expense
            if ln.od_refund_coach_comm > 0:
                aml.append((0, 0, {
                    'date': move_date,
                    'name': nm,
                    'account_id': coach_payable,
                    'debit': ln.od_refund_coach_comm,
                    'credit': 0.0,
                    'orchid_cc_id': cost_centre_id,
                    'partner_id': act.coach_id.id if act.coach_id else False,
                    'product_id': product.id if product else False,
                    "analytic_distribution": self._analytic_dist(analytic_account_id),
                }))
                aml.append((0, 0, {
                    'date': move_date,
                    'name': nm,
                    'account_id': coach_comm_exp,
                    'debit': 0.0,
                    'credit': ln.od_refund_coach_comm,
                    'orchid_cc_id': cost_centre_id,
                    'partner_id': act.coach_id.id if act.coach_id else False,
                    'product_id': product.id if product else False,
                    "analytic_distribution": self._analytic_dist(analytic_account_id),
                }))

            # Venue commission reversal: debit venue mgmt payable, credit academy commission expense
            if ln.od_refund_venue_comm > 0:
                if not venue_mgmt_payable:
                    raise UserError(_('Venue management payable account not set on the venue’s management partner.'))
                aml.append((0, 0, {
                    'date': move_date,
                    'name': nm,
                    'account_id': venue_mgmt_payable,
                    'debit': ln.od_refund_venue_comm,
                    'credit': 0.0,
                    'orchid_cc_id': cost_centre_id,
                    'partner_id': venue_mgmt_partner,
                    'product_id': product.id if product else False,
                    "analytic_distribution": self._analytic_dist(analytic_account_id),
                }))
                aml.append((0, 0, {
                    'date': move_date,
                    'name': nm,
                    'account_id': academy_comm_exp,
                    'debit': 0.0,
                    'credit': ln.od_refund_venue_comm,
                    'orchid_cc_id': cost_centre_id,
                    'partner_id': venue_mgmt_partner,
                    'product_id': product.id if product else False,
                    "analytic_distribution": self._analytic_dist(analytic_account_id),
                }))

            # VAT refund (debit VAT refund account)
            if ln.od_refund_vat_amount > 0:
                total_vat += ln.od_refund_vat_amount
                aml.append((0, 0, {
                    'date': move_date,
                    'name': nm,
                    'account_id': vat_acc_id,
                    'debit': ln.od_refund_vat_amount,
                    'credit': 0.0,
                    'partner_id': self.partner_id.id if self.partner_id else False,
                    'product_id': product.id if product else False,
                    "analytic_distribution": self._analytic_dist(analytic_account_id),
                }))

        # Credit the outbound refund payment/clearing account for the grand total
        total_credit = self.total_amount
        if total_credit <= 0:
            raise UserError(_('Nothing to post.'))

        aml.append((0, 0, {
            'date': move_date,
            'name': nm,
            'account_id': pay_return_acc,
            'debit': 0.0,
            'credit': total_credit,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'product_id': product.id if product else False,
            "analytic_distribution": self._analytic_dist(analytic_account_id),
        }))

        move_vals = {
            'move_type': 'entry',
            'journal_id': journal.id,
            'date': move_date,
            'ref': self.name,
            'line_ids': aml,
        }
        move = self.env['account.move'].create(move_vals)
        move.action_post()

        self.write({'state': 'confirm', 'move_id': move.id})

    # --------------------------
    # Onchange
    # --------------------------
    @api.onchange('od_activities_id', 'od_term_id')
    def onchange_activity(self):
        if self.od_activities_id and self.od_term_id:
            receipts = self.env['od.sports.receipt'].search([
                ('activities_id', '=', self.od_activities_id.id),
                ('term_id', '=', self.od_term_id.id)
            ])
            if receipts:
                clines = self.env['od.sports.receipt.line'].search([('receipt_id', 'in', receipts.ids)])
                return {'domain': {'partner_id': [('id', 'in', clines.mapped('partner_id').ids)]}}

    # --------------------------
    # Totals
    # --------------------------
    @api.depends('refund_line.od_refund_amount',
                 'refund_line.od_refund_vat_amount',
                 'refund_line.od_refund_coach_comm',
                 'refund_line.od_refund_venue_comm',
                 'refund_line.od_reg_refund_amount',
                 'refund_line.od_refund_total')
    def compute_total(self):
        for rec in self:
            subtotal = sum(rec.refund_line.mapped('od_refund_total'))
            total_refund_amt = sum(rec.refund_line.mapped('od_refund_amount'))
            total_reg_amount = sum(rec.refund_line.mapped('od_reg_refund_amount'))
            total_vat_amount = sum(rec.refund_line.mapped('od_refund_vat_amount'))
            total_coach_comm = sum(rec.refund_line.mapped('od_refund_coach_comm'))
            total_venue_comm = sum(rec.refund_line.mapped('od_refund_venue_comm'))

            rec.subtotal = subtotal
            rec.total_refund_amt = total_refund_amt
            rec.total_reg_amount = total_reg_amount
            rec.total_vat_amount = total_vat_amount
            rec.total_amount = subtotal + total_vat_amount
            rec.total_coach_comm = total_coach_comm
            rec.total_venue_comm = total_venue_comm


class OdRefundEntryLine(models.Model):
    _name = 'od.refund.entry.line'
    _description = 'Refund Entry Line'

    refund_id = fields.Many2one('od.refund.entry', string='Sports Refund', ondelete='cascade')
    od_rv_no = fields.Char(string='RV/Number')
    od_partner_id = fields.Many2one('res.partner', string='Student')
    od_payment_type_account_id = fields.Many2one('account.account', string='Account')
    od_type_id = fields.Many2one('od.camp.type', string='Type', required=True)
    od_remarks = fields.Char(string='Cheque No')
    od_date = fields.Date(string="Cheque Date")
    od_amount = fields.Float(string='Fees')
    od_coach_commision = fields.Float(string='Coach Commission Amount')
    od_no_of_clases = fields.Float(string='No Of Classes')
    od_transportation = fields.Float(string='Registration')
    od_total = fields.Float(string='Amount')
    od_vat_id = fields.Many2one('account.tax', string='Vat')
    od_vat_amount = fields.Float(string='Vat Amount')
    od_grand_total = fields.Float(string='Total')
    od_venue_commission = fields.Float(string='Venue Commission')
    od_collection_line_id = fields.Many2one('od.sports.receipt.line', string='Collection line')
    od_collection_id = fields.Many2one('od.sports.receipt', string='Collection')

    od_refund_amount = fields.Float(string='Refund Amount')
    od_reg_refund_amount = fields.Float(string='Reg. Refund')

    od_refund_total = fields.Float('Sub Total', compute="compute_total", store=True)
    od_refund_vat_amount = fields.Float(string='Refund Vat', compute="compute_vat", store=True)
    od_refund_subtotal = fields.Float(string='Total', compute="compute_vat", store=True)

    od_refund_coach_comm = fields.Float(string='Coach Refund', compute="compute_commission", store=True)
    od_refund_venue_comm = fields.Float(string='Venue Refund', compute="compute_commission", store=True)

    # --------------------------
    # Computes
    # --------------------------
    @api.depends('od_refund_amount', 'od_reg_refund_amount')
    def compute_total(self):
        for rec in self:
            rec.od_refund_total = (rec.od_refund_amount or 0.0) + (rec.od_reg_refund_amount or 0.0)

    @api.depends('od_refund_total', 'od_vat_id')
    def compute_vat(self):
        for rec in self:
            rate = (rec.od_vat_id.amount or 0.0) / 100.0 if rec.od_vat_id else 0.0
            rec.od_refund_vat_amount = (rec.od_refund_total or 0.0) * rate
            rec.od_refund_subtotal = (rec.od_refund_total or 0.0) + rec.od_refund_vat_amount

    @api.depends('od_refund_amount', 'od_refund_total', 'od_collection_id')
    def compute_commission(self):
        for rec in self:
            comm_perc = getattr(rec.od_collection_id, 'od_commission_perc', 0.0) or 0.0
            venue_comm_perc = getattr(rec.od_collection_id, 'venue_comm', 0.0) or 0.0
            rec.od_refund_coach_comm = (rec.od_refund_amount or 0.0) * (comm_perc / 100.0)
            rec.od_refund_venue_comm = (rec.od_refund_total or 0.0) * (venue_comm_perc / 100.0)

    # --------------------------
    # Constraints (optional but helpful)
    # --------------------------
    @api.constrains('od_refund_amount', 'od_reg_refund_amount', 'od_refund_vat_amount')
    def _check_non_negative(self):
        for rec in self:
            for val in [rec.od_refund_amount, rec.od_reg_refund_amount, rec.od_refund_vat_amount]:
                if (val or 0.0) < 0:
                    raise ValidationError(_("Refund amounts cannot be negative."))
