# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo import tools


class OrchidPrepaidAnalysis(models.Model):
    _name = "orchid.prepaid.report"
    _description = "Orchid Prepaid Analysis"
    _auto = False
    _order = "date_start, id"

    prepayment_id = fields.Many2one('orchid.prepayment.lines', string='Prepayments', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    allocation_date = fields.Date(string='Allocation Date', readonly=True)

    state = fields.Selection(
        [('cancel', 'Cancel'), ('running', 'Unposted'), ('closed', 'Posted')],
        string='State',
        readonly=True,
    )

    debit = fields.Float(string='Value', default=0.0, readonly=True)

    account_id = fields.Many2one('account.account', string='Prepaid Account', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', readonly=True)

    expense_analytic_account_id = fields.Many2one('account.analytic.account', string='Expense Analytic Account', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Prepaid Partner', ondelete='restrict', readonly=True)

    cost_center = fields.Many2one('orchid.account.cost.center', string='Cost Center', readonly=True)
    expense_cost_center = fields.Many2one('orchid.account.cost.center', string='Expense Cost Center', readonly=True)

    move_id = fields.Many2one('account.move', string="Journal Entry", readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True)

    date_start = fields.Date(readonly=True)
    date_end = fields.Date(readonly=True)

    linked_partner_id = fields.Many2one('res.partner', string='Expense Partner', ondelete='restrict', readonly=True)
    expense_account_id = fields.Many2one('account.account', string='Expense Account', readonly=True)

    posted_value = fields.Float(string='Posted Amount', readonly=True)
    unposted_value = fields.Float(string='Unposted Amount', readonly=True)

    remark = fields.Char(string='Remarks', readonly=True)

    def init(self):
        """Create or replace SQL view for prepaid analysis."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    a.date_start,
                    a.date_end,
                    MIN(dl.id) AS id,
                    dl.state AS state,
                    a.account_id,
                    a.analytic_account_id,
                    a.partner_id,
                    a.cost_center,
                    a.move_id,
                    a.journal_id,
                    a.remark,
                    a.expense_account_id,
                    a.linked_partner_id,
                    mve.date AS date,
                    CASE WHEN dl.state = 'closed'  THEN dl.amount ELSE 0 END AS posted_value,
                    CASE WHEN dl.state = 'running' THEN dl.amount ELSE 0 END AS unposted_value,
                    CASE WHEN dlmin.id = MIN(dl.id) THEN a.debit ELSE 0 END AS debit,
                    dl.cost_center AS expense_cost_center,
                    dl.analytic_account_id AS expense_analytic_account_id,
                    dl.date AS allocation_date
                FROM orchid_prepayment_board_history dl
                LEFT JOIN orchid_prepayment_lines a
                    ON (dl.prepayment_id = a.id)
                LEFT JOIN account_move mve
                    ON (a.move_id = mve.id)
                LEFT JOIN (
                    SELECT MIN(d.id) AS id, ac.id AS ac_id
                    FROM orchid_prepayment_board_history d
                    INNER JOIN orchid_prepayment_lines ac ON (ac.id = d.prepayment_id)
                    GROUP BY ac.id
                ) AS dlmin
                    ON dlmin.ac_id = a.id
                GROUP BY
                    dl.prepayment_id,
                    mve.date,
                    dl.amount,
                    dlmin.id,
                    dl.cost_center,
                    dl.analytic_account_id,
                    dl.date,
                    a.debit,
                    a.linked_partner_id,
                    a.date_start,
                    a.date_end,
                    dl.state,
                    a.account_id,
                    a.analytic_account_id,
                    a.partner_id,
                    a.cost_center,
                    a.move_id,
                    a.journal_id,
                    a.remark,
                    a.expense_account_id
            )
        """)
