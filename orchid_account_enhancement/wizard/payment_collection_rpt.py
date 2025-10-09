# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime

import xlwt
from io import StringIO
import base64


class PaymentCollectionReport(models.TransientModel):
    _name = 'od.payment.collection.report.wizard'
    _description = 'Collection Register'
    journal_id = fields.Many2one('account.journal','Journal')
    salesman_id = fields.Many2one('res.users','Salesman')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    excel_file=fields.Binary('Report',readonly=True)
    file_name = fields.Char('Excel File', size=64,readonly=True)

    def get_data(self):
        domain =[('payment_type','=','inbound')]
        payment = self.env['account.payment']
        customer_domain = []
        customer = self.env['res.partner']
        date_from = self.date_from
        journal_id = self.journal_id and self.journal_id.id or False
        if journal_id:
            domain += [('journal_id','=',journal_id)]
        if date_from:
            domain += [('date','>=',date_from)]
        date_to  = self.date_to
        if date_to:
            domain += [('date','<=',date_to)]

        user_id = self.salesman_id and self.salesman_id.id or False
        if user_id:
            customer_domain +=[('user_id','=',user_id)]
        customer_ids = [cust.id for cust in customer.search(customer_domain)]
        if customer_ids:
            domain += [('partner_id','in',customer_ids)]
        payment_ob = payment.search(domain)
        data = [{'Salesman':pay.partner_id and pay.partner_id.user_id and pay.partner_id.user_id.name or '',
                 'PaymentDate':pay.date,'Customer':pay.partner_id.name,'Amount':pay.amount,'CheckDate':pay.od_check_date,
                 'Journal':pay.journal_id.name,
                 'group_pay':pay.is_group} for pay in payment_ob if not pay.is_group]
        group_pay_data =[]
        for pay in payment_ob:
            if pay.is_group:
                for ch in pay.group_line:
                    vals ={'Customer':ch.child_partner_id and ch.child_partner_id.name or '','Amount':ch.pay_amount,
                           'Salesman':ch.child_partner_id.user_id.name,
                           'PaymentDate':pay.date,
                           'CheckDate':pay.od_check_date,
                            'Journal':pay.journal_id.name,
                             'group_pay':pay.is_group
                           }
                    group_pay_data.append(vals)

        result = data + group_pay_data
        return result

    def print_excel_report(self):

        result = self.get_data()
        dataframe= pd.DataFrame(result,columns=["PaymentDate","Customer","Salesman","Amount","CheckDate",'Journal','group_pay']    )
        dataframe.sort_values(by='PaymentDate')
        filename ='CollectionReport.xlsx'
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        fp = StringIO()
        writer.book.filename = fp
        dataframe.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        excel_file = base64.encodestring(fp.getvalue())
        self.write({'excel_file':excel_file,'file_name':filename})
        fp.close()
        return {
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'od.payment.collection.report.wizard',
              'res_id': self.id,
              'type': 'ir.actions.act_window',
              'target': 'new'
              }



    def _print_report(self, data):
        return self.env['report'].with_context(landscape=True).get_action(self, 'orchid_account_enhancement.report_payment_collection', data=data)
    def print_pdf(self):
        result =self.get_data()
        data ={'lines':result}
        return self._print_report(data)
