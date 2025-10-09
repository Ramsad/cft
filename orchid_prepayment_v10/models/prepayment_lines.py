# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime as dt, date as ddate, timedelta
from dateutil.relativedelta import relativedelta


class OrchidPrepaymentLine(models.Model):
    _name = 'orchid.prepayment.lines'
    _description = 'Prepayment'

    account_id = fields.Many2one('account.account', string='Account')
    name = fields.Char(string='Name')
    move_id = fields.Many2one('account.move', string='Journal Entry', required=True, readonly=True)
    date = fields.Date(related='move_id.date', string='Date', readonly=True, store=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    debit = fields.Float(string="Debit", readonly=True)
    credit = fields.Float(string="Credit", readonly=True)

    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")

    expense_account_id = fields.Many2one('account.account', string="Expense Account")
    journal_id = fields.Many2one('account.journal', string="Journal")
    remark = fields.Char(string="Remark")
    cost_center = fields.Many2one('orchid.account.cost.center', string="Cost Center")
    linked_partner_id = fields.Many2one('res.partner', string='Expense Partner')
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")

    state = fields.Selection(
        [('draft', 'Draft'), ('in_progress', 'In progress'), ('done', 'Done'), ('cancel', 'Cancel')],
        string='Status', required=True, readonly=True, default='draft'
    )

    line_history_ids = fields.One2many(
        'orchid.prepayment.board.history', 'prepayment_id',
        string='History', copy=False
    )

    # ----------------------------------------------------------------------
    # Actions
    # ----------------------------------------------------------------------
    def load_prepayment_line(self):
        """Scan posted moves on prepaid accounts and create missing prepayment records."""
        self.ensure_one()
        # Existing move_ids to avoid duplicates
        existing_move_ids = set(self.search([]).mapped('move_id').ids)

        prepaid_accounts = self.env['account.account'].search([('od_prepaid_account', '=', True)])
        if not prepaid_accounts:
            raise ValidationError(_('No accounts are marked as "Prepaid Account".'))

        move_lines = self.env['account.move.line'].search([('account_id', 'in', prepaid_accounts.ids)])
        for ml in move_lines:
            if ml.move_id.state == 'draft':
                continue
            if ml.move_id.id in existing_move_ids:
                continue
            # Only create for debit balance on prepaid (typical capitalization)
            if ml.debit <= 0:
                continue
            vals = {
                'account_id': ml.account_id.id,
                'move_id': ml.move_id.id,
                'partner_id': ml.partner_id.id if ml.partner_id else False,
                'debit': ml.debit,
                'credit': ml.credit,
                'date_start': ml.date,
                'remark': 'Prepayment Line',
                'state': 'draft',
            }
            self.create(vals)

        # Open the prepayment tree/view filtered on this move (if you prefer a global view, remove domain)
        action = self.env.ref('orchid_prepayment_v18.action_orchid_prepayment').read()[0]
        action['domain'] = [('move_id', '=', self.move_id.id)]
        return action

    def generate_prepayment_board(self):
        """Validate and generate monthly board history lines across the given date range."""
        self.ensure_one()
        self._validate_and_build_board()
        return True

    def button_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            for li in rec.line_history_ids:
                if li.state == 'running':
                    li.state = 'cancel'

    def button_confirm(self):
        self.ensure_one()
        if not self.line_history_ids:
            raise ValidationError(_('No board history lines found.'))
        self.state = 'in_progress'
        return True

    # ----------------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------------
    @staticmethod
    def _month_day_range(date_obj: ddate):
        """Return (first_day, last_day) for the month of date_obj (date)."""
        first_day = date_obj.replace(day=1)
        last_day = (first_day + relativedelta(months=+1)) - timedelta(days=1)
        return first_day, last_day

    def _validate_and_build_board(self):
        """Validate inputs and create orchid.prepayment.board.history rows."""
        rec = self
        if rec.line_history_ids:
            raise ValidationError(_('Board already generated for this prepayment.'))

        if not (rec.date_start and rec.date_end and rec.expense_account_id and rec.journal_id):
            raise ValidationError(_('Please set Start/End dates, Expense Account and Journal.'))

        if rec.state != 'draft':
            raise ValidationError(_('Payment board already generated!'))

        move = rec.move_id
        if not move:
            raise ValidationError(_('Missing Journal Entry.'))
        if not move.line_ids:
            raise ValidationError(_('The Journal Entry has no lines.'))

        voucher_date = move.date
        if rec.date_start < voucher_date:
            raise ValidationError(_('Start Date must be on or after the move date.'))

        if rec.date_end < rec.date_start:
            raise ValidationError(_('End Date must be on or after Start Date.'))

        # Identify prepaid account used on the move (debit/credit both supported)
        prepaid_acc_ids = []
        credit_side_acc_ids = []
        debit_side_acc_ids = []
        for ml in move.line_ids:
            if ml.account_id.od_prepaid_account:
                prepaid_acc_ids.append(ml.account_id.id)
                if ml.debit > 0:
                    debit_side_acc_ids.append(ml.account_id.id)
                if ml.credit > 0:
                    credit_side_acc_ids.append(ml.account_id.id)

        if not prepaid_acc_ids:
            raise ValidationError(_('The move does not use a Prepaid Account.'))

        # Total capitalized value to amortize (use the prepayment line’s debit/credit snapshot)
        max_value = rec.debit or rec.credit
        if not max_value:
            # fallback: sum debits on prepaid accounts in the move (common case)
            max_value = sum(move.line_ids.filtered(lambda l: l.account_id.od_prepaid_account).mapped('debit'))

        # Amount per day across the entire window
        ds = dt.strptime(str(rec.date_start), "%Y-%m-%d").date()
        de = dt.strptime(str(rec.date_end), "%Y-%m-%d").date()
        total_days = ((de - ds).days + 1) or 1
        per_day = max_value / total_days

        # Post to expense (debit) and credit the prepaid account used on the move (first found)
        credit_account_id = (credit_side_acc_ids[0] if credit_side_acc_ids
                             else (prepaid_acc_ids[0] if prepaid_acc_ids else rec.account_id.id))
        debit_account_id = rec.expense_account_id.id
        analytic_id = rec.analytic_account_id.id if rec.analytic_account_id else False
        cc_id = rec.cost_center.id if rec.cost_center else False
        partner_id = rec.linked_partner_id.id if rec.linked_partner_id else False

        # Build monthly slices: first month (partial), middle full months, last month (partial)
        # First month
        first_day, last_day = self._month_day_range(ds)
        days_first = (last_day - ds).days + 1
        self.env['orchid.prepayment.board.history'].create({
            'amount': per_day * days_first,
            'prepayment_id': rec.id,
            'date': str(last_day),
            'journal_id': rec.journal_id.id,
            'account_id': credit_account_id or rec.account_id.id,
            'debit_account_id': debit_account_id,
            'cost_center': cc_id,
            'analytic_account_id': analytic_id,
            'partner_id': partner_id,
            'state': 'running',
        })

        # Middle months (if any)
        cursor = last_day
        last_day_of_end_month = self._month_day_range(de)[1]
        while cursor < last_day_of_end_month:
            cursor = (cursor + relativedelta(months=1))
            m_first, m_last = self._month_day_range(cursor)
            if m_last >= last_day_of_end_month:
                break  # last month handled below
            days_mid = (m_last - m_first).days + 1
            self.env['orchid.prepayment.board.history'].create({
                'amount': per_day * days_mid,
                'prepayment_id': rec.id,
                'date': str(m_last),
                'journal_id': rec.journal_id.id,
                'account_id': credit_account_id or rec.account_id.id,
                'debit_account_id': debit_account_id,
                'cost_center': cc_id,
                'analytic_account_id': analytic_id,
                'partner_id': partner_id,
                'state': 'running',
            })

        # Last month
        _, end_last = self._month_day_range(de)
        days_last = (de - end_last.replace(day=1)).days + 1
        # If ds and de are in same month, the “first” slice already covered; skip duplicate
        if de.month != ds.month or de.year != ds.year:
            self.env['orchid.prepayment.board.history'].create({
                'amount': per_day * days_last,
                'prepayment_id': rec.id,
                'date': str(end_last),
                'journal_id': rec.journal_id.id,
                'account_id': credit_account_id or rec.account_id.id,
                'debit_account_id': debit_account_id,
                'cost_center': cc_id,
                'analytic_account_id': analytic_id,
                'partner_id': partner_id,
                'state': 'running',
            })
        return True


# ----------------------------------------------------------------------
# Extensions
# ----------------------------------------------------------------------
class AccountAccount(models.Model):
    _inherit = 'account.account'

    od_prepaid_account = fields.Boolean('Prepaid Account')


class AccountMove(models.Model):
    _inherit = 'account.move'

    od_is_prepayment = fields.Boolean(
        string="Prepayment Entry",
        store=True,
        compute="_compute_is_prepayment",
        default=False
    )

    @api.depends('line_ids.account_id', 'line_ids.debit')
    def _compute_is_prepayment(self):
        for move in self:
            move.od_is_prepayment = any(
                l.account_id.od_prepaid_account and l.debit > 0 for l in move.line_ids
            )

    def open_prepayment_view(self):
        """Open the prepayment list and auto-load a record for this move if needed."""
        self.ensure_one()
        # Create/load record bound to this move
        prepay = self.env['orchid.prepayment.lines'].search([('move_id', '=', self.id)], limit=1)
        if not prepay:
            prepay = self.env['orchid.prepayment.lines'].create({
                'move_id': self.id,
                'account_id': self.line_ids[:1].account_id.id if self.line_ids else False,
                'partner_id': self.partner_id.id if self.partner_id else False,
                'debit': sum(self.line_ids.mapped('debit')),
                'credit': sum(self.line_ids.mapped('credit')),
                'remark': 'Prepayment Line',
            })
        action = self.env.ref('orchid_prepayment_v18.action_orchid_prepayment').read()[0]
        action['domain'] = [('move_id', '=', self.id)]
        return action

    def button_draft(self):
        """When unposting, ensure prepayment lines are not left inconsistent."""
        res = super().button_draft()
        for move in self:
            prepayments = self.env['orchid.prepayment.lines'].search([('move_id', '=', move.id)])
            for pre in prepayments:
                if pre.state == 'draft':
                    pre.unlink()
                else:
                    # Prevent unpost if amortization has already started
                    raise ValidationError(_('There are generated prepayment lines for this move.'))
        return res
