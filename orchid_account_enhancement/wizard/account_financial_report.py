# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class AccountingReport(models.TransientModel):
    _inherit = "accounting.report"

    detail_report = fields.Boolean(string='Detailed Report')


    def _build_detailed_report_context(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        date_from = data['form']['date_from']
        if date_from:
            date_from = date_from[:5] + "01-01"
        result['date_from'] = date_from
        result['date_to'] = data['form']['date_from']
        return result


    
    def check_report(self):
        res = super(AccountingReport, self).check_report()
        data = {}
        data['form'] = self.read(['account_report_id', 'date_from', 'date_to', 'journal_ids', 'detail_report', 'target_move'])[0]
        if data['form']['detail_report']:
            if not data['form']['date_to']:
                raise UserError(_("Date field cannot be null!!"))
            detailed_report_context = self._build_detailed_report_context(data)
            res['data']['form']['detailed_report_context'] = detailed_report_context
        return res


    def _print_report(self, data):
        res = super(AccountingReport, self)._print_report(data)
        data['form'].update(self.read(['detail_report'])[0])
        return self.env['report'].get_action(self, 'account.report_financial', data=data)
