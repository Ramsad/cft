# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo import api, fields, models, _


class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.report.partner.ledger"

    partner_id = fields.Many2one('res.partner',string='Partner')
    
    def check_report(self):
        print('BBBBB')
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move','partner_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        return self._print_report(data)



    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency})
        return self.env['report'].get_action(self, 'account.report_partnerledger', data=data)
