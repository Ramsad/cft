# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ReportAccountPayment(models.AbstractModel):

    _name = 'report.orchid_account_enhancement.report_account_payment'
    
    def _get_move_lines(self, payment_id):            
        mv_line = self.env['account.move.line']
        partial_reconcile = self.env['account.partial.reconcile']
        move_ids = mv_line.search([('payment_id','=',payment_id),('reconciled','!=',False)])
        full_move_list = []
        if move_ids:
            full_move_ids = mv_line.search([('full_reconcile_id','=',move_ids[0].full_reconcile_id.id)])            
            for fm_ids in full_move_ids:                
                full_move_list.append(fm_ids.id)
        allmove_ids =[]

        if full_move_list:
            creditmove_lines = partial_reconcile.search([('credit_move_id','in',full_move_list)])
            debitmove_lines = partial_reconcile.search([('debit_move_id','in',full_move_list)])
            for cr_line in creditmove_lines:
                if cr_line.credit_move_id.payment_id.id != payment_id:
                    allmove_ids.append(cr_line.credit_move_id)
            for dr_line in debitmove_lines:
                allmove_ids.append(dr_line.debit_move_id)
        reco_lines = list(set(allmove_ids)) 
        res = []
        for line in reco_lines:
            values = {}
            values['id'] = line.id
            values['debit'] = line.debit
            values['credit'] = line.credit
            values['payment_id'] = line.payment_id.id
            values['full_reconcile_id'] = line.full_reconcile_id.id
            values['reconciled'] = line.reconciled
            values['account_id'] = line.account_id.id
            values['ref'] = line.ref
            values['date'] = line.date
            values['name'] = line.name
            values['balance'] = line.balance
            values['number'] = line.move_id.name
            values['narration'] = line.move_id.ref
            res.append(values)
        return res

    
    def render_html(self, docids, data=None):
        obj_model = self.env['account.payment']
        docs = obj_model.browse(docids)
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('orchid_account_enhancement.report_account_payment')
        rptlines = self._get_move_lines(docids[0])
        
        docargs = {
            'doc_model':  report.model,
            'doc_ids': docids,
            'matching_lines': rptlines,
            'docs': docs,
        }
        return self.env['report'].render('orchid_account_enhancement.report_account_payment', docargs)

        
class ReportReceivablePayable(models.AbstractModel):

    _name = 'report.orchid_account_enhancement.report_receivable_payable'
    
    def _get_move_lines(self, payment_id):            
        res = []
        pay_obj = self.env['account.payment']
        pay_lines = pay_obj.search([('id','in',payment_id)])
        for pay_line in pay_lines:
            if not pay_line.od_released:
                values = {}
                values['name'] = pay_line.name
                values['type'] = pay_line.journal_id.code
                values['transaction_date'] = datetime.strptime(pay_line.payment_date, '%Y-%m-%d').strftime('%m-%d-%Y')
                # .strftime('%d-%m-%Y')
                values['party'] = pay_line.partner_id.name
                values['chq_no'] = pay_line.od_check_no
                values['chq_date'] = datetime.strptime(pay_line.od_check_date, '%Y-%m-%d').strftime('%m-%d-%Y')
                # .strftime('%d-%m-%Y')
                values['amount'] = pay_line.amount
                values['bank'] = pay_line.od_bank_account.name
                res.append(values)
        return res

    
    def render_html(self, docids, data=None):
        obj_model = self.env['account.payment']
        docs = obj_model.browse(docids)
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('orchid_account_enhancement.report_receivable_payable')
        rptlines = self._get_move_lines(docids)
        
        docargs = {
            'doc_model':  report.model,
            'doc_ids': docids,
            'matching_lines': rptlines,
            'docs': docs,
        }
        return self.env['report'].render('orchid_account_enhancement.report_receivable_payable', docargs)

        
