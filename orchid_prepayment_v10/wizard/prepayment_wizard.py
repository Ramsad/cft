# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PrepaymentWizard(models.TransientModel):
    _name = "prepayment.wizard"
    _description = "Prepayment Posting Wizard"

    date_start = fields.Date('Date From', required=True, default=fields.Date.context_today)
    date_to = fields.Date('Date To', required=True, default=fields.Date.context_today)

    def generate(self):
        self.ensure_one()
        if self.date_to < self.date_start:
            raise ValidationError(_("‘Date To’ must be on or after ‘Date From’."))
        lines = self.env['orchid.prepayment.board.history'].search([
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_to),
            ('state', 'not in', ('closed', 'cancel')),
        ])

        if not lines:
            raise UserError(_("No running prepayment lines in the selected period."))

        created_moves = self.env['account.move']
        for line in lines:
            # Only post running lines of a prepayment already in progress
            if line.prepayment_id.state != 'in_progress':
                continue

            partner = line.partner_id
            debit_account = line.debit_account_id
            credit_account = line.account_id
            journal = line.journal_id
            if not (debit_account and credit_account and journal):
                # Skip incomplete config
                continue

            # Analytic distribution: 100% to the selected analytic, if any
            analytic_distribution = False
            if line.analytic_account_id:
                analytic_distribution = {line.analytic_account_id.id: 100}

            common = {
                'name': line.prepayment_id.remark or 'Prepayment',
                'partner_id': partner.id if partner else False,
                'orchid_cc_id': line.cost_center.id if line.cost_center else False,
            }
            if analytic_distribution:
                common['analytic_distribution'] = analytic_distribution

            debit_ml = dict(common, account_id=debit_account.id, debit=line.amount, credit=0.0)
            credit_ml = dict(common, account_id=credit_account.id, debit=0.0, credit=line.amount)

            move_vals = {
                'move_type': 'entry',
                'journal_id': journal.id,
                'date': line.date,
                'ref': 'Prepayment%s' % (f" [{line.prepayment_id.move_id.name}]" if line.prepayment_id.move_id and line.prepayment_id.move_id.name else ''),
                'line_ids': [(0, 0, debit_ml), (0, 0, credit_ml)],
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            created_moves |= move

            # Close the history line
            line.state = 'closed'

            # If no more running lines on this prepayment, mark parent as done; else keep in_progress
            remaining = line.prepayment_id.line_history_ids.filtered(lambda l: l.state == 'running')
            line.prepayment_id.state = 'done' if not remaining else 'in_progress'

        # Open the created moves
        action = self.env.ref('account.action_move_journal_line').read()[0]
        action['domain'] = [('id', 'in', created_moves.ids)]
        return action
