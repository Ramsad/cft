# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OrchidPrepaymentBoardHistory(models.Model):
    _name = 'orchid.prepayment.board.history'
    _description = 'Prepayment Board Line History'

    prepayment_id = fields.Many2one(
        'orchid.prepayment.lines', string='Prepayment',
        ondelete='cascade', readonly=True, required=True
    )
    account_id = fields.Many2one('account.account', string='Credit Account', readonly=True, required=True)
    debit_account_id = fields.Many2one('account.account', string='Debit Account', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    amount = fields.Float('Amount', readonly=True, required=True)
    date = fields.Date('Date', readonly=True, required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True, required=True)

    state = fields.Selection(
        [('running', 'Running'), ('closed', 'Closed'), ('cancel', 'Cancel')],
        string='Status', default='running', readonly=True
    )

    # Custom dims (kept as-is; posted to move lines if your modules add those fields)
    cost_center = fields.Many2one('orchid.account.cost.center', string="Cost Center")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")

    def action_prepayment_generate(self):
        """Post an amortization journal entry for each selected running line."""
        for rec in self:
            if rec.state != 'running':
                raise ValidationError(_('You can only generate entries for lines in Running state.'))

            # Build move lines
            common = {
                'date': rec.date,
                'name': 'Prepayment: %s' % (rec.prepayment_id.move_id.name or ''),
                'partner_id': rec.partner_id.id if rec.partner_id else False,
                'analytic_account_id': rec.analytic_account_id.id if rec.analytic_account_id else False,
            }
            # Optional custom dimensions (ignored if fields don’t exist on account.move.line)
            if rec._fields.get('cost_center'):
                common['cost_center'] = rec.cost_center.id if rec.cost_center else False

            debit_line = dict(common, account_id=rec.debit_account_id.id, debit=rec.amount, credit=0.0)
            credit_line = dict(common, account_id=rec.account_id.id,       debit=0.0,     credit=rec.amount)

            move_vals = {
                'move_type': 'entry',
                'journal_id': rec.journal_id.id,
                'date': rec.date,
                'ref': 'Prepayment',
                'narration': 'Prepayment amortization from %s' % (rec.prepayment_id.move_id.name or ''),
                'line_ids': [(0, 0, debit_line), (0, 0, credit_line)],
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()

            # Close this history line
            rec.state = 'closed'

            # If all lines of the parent are no longer running, advance the parent status
            remaining = rec.prepayment_id.line_history_ids.filtered(lambda l: l.state == 'running')
            if not remaining:
                # Your parent model states: draft / in_progress / done / cancel
                if rec.prepayment_id.state in ('draft', 'in_progress'):
                    rec.prepayment_id.state = 'done'
        return True
