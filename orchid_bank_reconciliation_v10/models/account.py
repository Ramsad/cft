# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    # TODO:  removed in newer Odoo; refactor for recordsets
# 
    @api.depends('move_id','date','name','od_reconcile_date')
    def _compute_check_no(self):
       if self.move_id:
            print("0000000000000000000000000000000", end=' ')
            account_payment_ids = self.env['account.payment'].search([('move_name', '=', self.move_id.name)])
            for account_payment  in account_payment_ids:
                if account_payment:
                    self.od_check_vnumber = account_payment.od_check_no or ''

    od_reconcile_date = fields.Date(string='Bank Date',default=False,copy=False)
    od_check_vnumber = fields.Char(string='Check Number',readonly=True)


    def od_list_accounts(self, cr, uid, context=None):
        ng = dict(self.pool.get('account.journal').name_search(cr,uid,'',[('type','=','bank')]))
        journal_ids = list(ng.keys())
        account_ids = []
        for journal in self.pool.get('account.journal').browse(cr, uid, journal_ids, context=context):
            credit_acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id or ''
            debit_acc_id = journal.default_debit_account_id and journal.default_debit_account_id.id or ''
            credit_acc_id and (credit_acc_id not in account_ids) and account_ids.append(credit_acc_id)
            debit_acc_id and (debit_acc_id not in account_ids) and account_ids.append(debit_acc_id)
        print("%%%^^%^%$^%$^%$^%$",account_ids)
        return self.pool.get('account.account').name_get(cr, uid, account_ids, context=context)


    def od_list_journals(self, cr, uid, context=None):
        ng = dict(self.pool.get('account.journal').name_search(cr,uid,'',[('type','=','bank')]))
        ids = list(ng.keys())
        result = []
        for journal in self.pool.get('account.journal').browse(cr, uid, ids, context=context):
            result.append((journal.id,ng[journal.id],journal.type,
                bool(journal.currency),bool(journal.analytic_journal_id)))
        return result

#    def od_get_periods(self):
#        
#        period_pool = self.env['account.period']
#        periods = [period.id for period in period_pool.search()] 
#        return periods


#    def od_list_periods(self, cr, uid, context=None):
#        ids = self.pool.get('account.period').search(cr,uid,['|',('od_sequence','=',0),('special','=',False)])
#        return self.pool.get('account.period').name_get(cr, uid, ids, context=context)
    
    
    
    
    def od_get_query(self,query,account_id,from_date,to_date,bank=False):
       
        query_params = (account_id,)
        if to_date and not from_date:
            if bank:   
                query_params = (account_id,to_date)
                query = query+ ' AND (od_reconcile_date <= %s)'
            else:
                query_params = (account_id,to_date)
                query = query+ ' AND (date<=%s)  '
        print("query!!\n\n!!!!!!",query)
        return query,query_params

    def od_book_bank_balance(self, cr, uid,from_date,to_date, context=None):
        if context is None:
            context = {}
        from_date = False

        print("%%%%%%%%%%%%%%%\n%%%%%%%%%\n%%%%%%%%%%%%%%%%%",context)

        result = {
            'book_balance':0.0,
            'bank_balance':0.0,
            'fc_book_balance':0.0,
            'fc_bank_balance':0.0,
            'reconciled_balance':0.0,
            'unconciled_balance':0.0,
        }

#        period_ids = self.pool.get('account.period').search(cr,uid,['|',('od_sequence','=',0),('special','=',False)])

        account_id = False
        if 'account_id' in context and context.get('account_id'):
            account_id = context.get('account_id')
        if not account_id:
            return result

#book Balance

      
        qry ="SELECT (sum(debit) - sum(credit)) as book_balance FROM account_move_line WHERE account_id = %s AND move_id in (select id from account_move where state='posted')"
        query,query_params = self.od_get_query(qry, account_id,from_date, to_date)
       
        cr.execute(query,query_params)
        res = cr.fetchone()
        book = res[0] or 0.0
        if res: result['book_balance'] = book

        print("~~~~~~~~~~~~~~~~~~~~~~~book_balnace>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",book)

        qry1 = 'SELECT (sum(debit) - sum(credit)) as bank_balance FROM '+self._table+' '\
                 'WHERE account_id = %s AND od_reconcile_date is not null'
        query,query_params = self.od_get_query(qry1, account_id,from_date, to_date,bank=True)
        cr.execute(query,query_params)
        res = cr.fetchone()
        bank = res[0] or 0.0
        if res: result['bank_balance'] = bank 
##Reconciled Balance
        if bank: result['reconciled_balance'] = bank or 0.0
        result['unconciled_balance'] = book - bank

#Currency bank Balance
        print("\n\n$$$$$$$$$$",account_id)
        cr.execute('SELECT sum(amount_currency) as amount_currency_book_balance FROM '+self._table+' '\
                'WHERE account_id = %s',(str(account_id),))
        res = cr.fetchone()
        if res: result['fc_book_balance'] = res[0] or 0.0

#Currency book Balance
        cr.execute('SELECT sum(amount_currency) as amount_currency_bank_balance FROM '+self._table+' '\
                'WHERE account_id = %s AND od_reconcile_date is not null',(str(account_id),))
        res = cr.fetchone()
        if res: result['fc_bank_balance'] = res[0] or 0.0


        return result


