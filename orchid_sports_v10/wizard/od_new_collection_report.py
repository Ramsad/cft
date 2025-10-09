# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class OdNewCollectionReportWiz(models.TransientModel):
    _name = "od.new.collection.report.wiz"
    _description = "New Collection Report Wizard"

    from_date = fields.Date(string='From Date', required=True)
    to_date   = fields.Date(string='To Date', required=True)

    @api.constrains('from_date', 'to_date')
    def _check_dates(self):
        for rec in self:
            if rec.from_date and rec.to_date and rec.to_date < rec.from_date:
                raise ValidationError(_("To Date must be on or after From Date."))

    def generate_print(self):
        self.ensure_one()
        domain = [
            ('date', '>=', self.from_date),
            ('date', '<=', self.to_date),
        ]
        receipts = self.env['od.sports.receipt'].search(domain)
        if not receipts:
            raise UserError(_('No data found for the selected period.'))

        data = {
            'from_date': str(self.from_date),
            'to_date': str(self.to_date),
            'receipt_ids': receipts.ids,
        }

        return self.env.ref('orchid_sports_v10.report_collect_summary').report_action(receipts, data=data)
