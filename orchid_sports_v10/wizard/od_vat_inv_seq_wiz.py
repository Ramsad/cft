# -*- coding: utf-8 -*-
##############################################################################

from odoo import fields,models,api,_
from odoo.tools.translate import _
from odoo.exceptions import UserError, AccessError



class ReportOrchidVatInvSeq(models.Model):

    _name = 'report.orchid.vat_inv_seq'
    _order = 'inv_no asc'

    inv_no = fields.Char(string='Invoice No.')
    partner_id = fields.Many2one('res.partner', string='Partner')
    date = fields.Date(string='Date')
    amount = fields.Float(string='Amount')
    vat = fields.Float(string='Vat Amount')
    total = fields.Float(string='Total Amount')





class orchid_vatinvseq_wizard(models.TransientModel):
    _name = "orchid.vatinvseq.wizard"
    _description = "Vat Invoice Sequence Wizard"

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    journal_id = fields.Many2many('account.journal',string='Journal')


    def generate_report(self):
        inv_seq_report = self.env['report.orchid.vat_inv_seq']
        inv_seq_report.search([]).unlink()
        col_obj = self.env['od.sports.receipt']
        col_line_obj = self.env['od.sports.receipt.line']
        inv_obj = self.env['account.move']
        from_date = self.date_from
        to_date = self.date_to
        journal_ids = [journal.id for journal in self.journal_id]
        journal_types = [journal.type for journal in self.journal_id]
        print(journal_ids)
        if not journal_ids:
            raise UserError(_('No journal selected!!'))
        row_data = []
        if 'sale' in journal_types:
            col_datas = col_obj.search([('date','>=',from_date),('date','<=',to_date)])
            for col_data in col_datas:
                for line in col_data.receipt_line:
                    data = {
                    'inv_no':line.od_invoice_no,
                    'partner_id':line.partner_id.id,
                    'date':col_data.date,
                    'amount':line.total,
                    'vat':line.od_vat_amount,
                    'total':line.grand_total,
                    }
                    row_data.append(data)
        invoice_datas = inv_obj.search([('journal_id','in',journal_ids),('date_invoice','>=',from_date),('date_invoice','<=',to_date)])
        for invoice_data in invoice_datas:
            data = {
                'inv_no':invoice_data.number,
                'partner_id':invoice_data.partner_id.id,
                'date':invoice_data.date_invoice,
                'amount':invoice_data.amount_untaxed,
                'vat':invoice_data.amount_tax,
                'total':invoice_data.amount_total,
                }
            row_data.append(data)
        row_data = sorted(row_data, key=lambda k: (k['inv_no']))
        for dt in row_data:
            inv_seq_report.create(dt)
        action = self.env.ref('orchid_sports_v10.action_orchid_vatinvseq_report_tree')
        result = action.read()[0]
        print(result)
        return result
