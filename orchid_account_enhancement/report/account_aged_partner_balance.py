# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.tools import float_is_zero
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta

class ReportAgedPartnerBalance(models.AbstractModel):

    _inherit = 'report.account.report_agedpartnerbalance'
    
    
    
    # TODO:  removed in newer Odoo; refactor for recordsets
# 
    def get_start_date(self,stop_date,day):
        from datetime import datetime
        d1 = datetime.strptime(ds, "%Y-%m-%d")
            
        stop_date = stop_date + timedelta(days=-day)
                    
        new_date = stop_date.strftime("%Y-%m-%d")
        return new_date

    def _get_partner_move_lines(self, account_type, date_from, target_move, period_length,od_period_lenght1,od_period_lenght2,od_period_lenght3,od_period_lenght4,od_period_lenght5,od_period_lenght6,od_is_slab,od_is_invoice_date,data,od_partners,od_account_id):
        periods = {}
        start = datetime.strptime(date_from, "%Y-%m-%d")
        print("periods length>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",period_length)
        for i in range(7)[::-1]:
            stop = start - relativedelta(days=period_length)
            periods[str(i)] = {
                'name': (i!=0 and (str((7-(i+1)) * period_length) + '-' + str((7-i) * period_length)) or ('+'+str(6 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        print("periods>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",periods,data)
        if od_is_slab:
            for period in periods:
                
                if period == '6':
                    periods[period]['name'] = '0-'+str(od_period_lenght1)
                    stop_date = datetime.strptime(str(periods[period]['stop']), "%Y-%m-%d")
                    stop_date = stop_date + timedelta(days=-int(od_period_lenght1))
                    new_date = stop_date.strftime("%Y-%m-%d")
                    periods[period]['start'] = new_date
                    data['6']['name']=periods[period]['name']
                
                
                if period == '5':
                    periods[period]['name'] = str(od_period_lenght1)+"-"+str(od_period_lenght2)
                    start_date = datetime.strptime(str(date_from), "%Y-%m-%d")
                    start_date = start_date + timedelta(days=-int(od_period_lenght2 +1))
                    start_date = start_date.strftime("%Y-%m-%d")                
                    stop_date = datetime.strptime(str(date_from), "%Y-%m-%d")
                    stop_date = stop_date + timedelta(days=-int(od_period_lenght1+1))
                    stop_date = stop_date.strftime("%Y-%m-%d")
                    periods[period]['start'] = start_date
                    periods[period]['stop'] = stop_date
                    data['5']['name']=periods[period]['name']                
                
                
                if period == '4':
                    periods[period]['name'] = str(od_period_lenght2)+"-"+str(od_period_lenght3)
                    start_date = datetime.strptime(str(date_from), "%Y-%m-%d")
                    start_date = start_date + timedelta(days=-int(od_period_lenght3 +2))
                    start_date = start_date.strftime("%Y-%m-%d")                
                    stop_date = datetime.strptime(str(date_from), "%Y-%m-%d")
                    stop_date = stop_date + timedelta(days=-int(od_period_lenght2+2))
                    stop_date = stop_date.strftime("%Y-%m-%d")
                    periods[period]['start'] = start_date
                    periods[period]['stop'] = stop_date
                    data['4']['name']=periods[period]['name']
                    
                    
                if period == '3':
                    periods[period]['name'] = str(od_period_lenght3)+"-"+str(od_period_lenght4)
                    start_date = datetime.strptime(str(date_from), "%Y-%m-%d")
                    start_date = start_date + timedelta(days=-int(od_period_lenght4 +3))
                    start_date = start_date.strftime("%Y-%m-%d")                
                    stop_date = datetime.strptime(str(date_from), "%Y-%m-%d")
                    stop_date = stop_date + timedelta(days=-int(od_period_lenght3+3))
                    stop_date = stop_date.strftime("%Y-%m-%d")
                    periods[period]['start'] = start_date
                    periods[period]['stop'] = stop_date
                    data['3']['name']=periods[period]['name']
                   
                    
                if period == '2':
                    periods[period]['name'] = str(od_period_lenght4)+"-"+str(od_period_lenght5)
                    start_date = datetime.strptime(str(date_from), "%Y-%m-%d")
                    start_date = start_date + timedelta(days=-int(od_period_lenght5 +4))
                    start_date = start_date.strftime("%Y-%m-%d")                
                    stop_date = datetime.strptime(str(date_from), "%Y-%m-%d")
                    stop_date = stop_date + timedelta(days=-int(od_period_lenght4+4))
                    stop_date = stop_date.strftime("%Y-%m-%d")
                    periods[period]['start'] = start_date
                    periods[period]['stop'] = stop_date
                    data['2']['name']=periods[period]['name']
                    
                    
                    
                if period == '1':
                    periods[period]['name'] = str(od_period_lenght5)+"-"+str(od_period_lenght6)
                    start_date = datetime.strptime(str(date_from), "%Y-%m-%d")
                    start_date = start_date + timedelta(days=-int(od_period_lenght6 +5))
                    start_date = start_date.strftime("%Y-%m-%d")                
                    stop_date = datetime.strptime(str(date_from), "%Y-%m-%d")
                    stop_date = stop_date + timedelta(days=-int(od_period_lenght5+5))
                    stop_date = stop_date.strftime("%Y-%m-%d")
                    periods[period]['start'] = start_date
                    periods[period]['stop'] = stop_date
                    data['1']['name']=periods[period]['name']
                    
                    
                if period == '0':
                    periods[period]['name'] = "+"+str(od_period_lenght6)
                            
                    stop_date = datetime.strptime(str(date_from), "%Y-%m-%d")
                    stop_date = stop_date + timedelta(days=-int(od_period_lenght6+6))
                    stop_date = stop_date.strftime("%Y-%m-%d")
                    periods[period]['stop'] = stop_date
                    data['0']['name']=periods[period]['name']   
        print("periods after>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",periods)
        res = []
        total = []
        cr = self.env.cr
        user_company = self.env.user.company_id.id
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type))
        #build the reconciliation clause to see what partner needs to be printed
        reconciliation_clause = '(l.reconciled IS FALSE)'
        cr.execute('SELECT debit_move_id, credit_move_id FROM account_partial_reconcile where create_date > %s', (date_from,))
        reconciled_after_date = []
        for row in cr.fetchall():
            reconciled_after_date += [row[0], row[1]]
        if reconciled_after_date:
            reconciliation_clause = '(l.reconciled IS FALSE OR l.id IN %s)'
            arg_list += (tuple(reconciled_after_date),)
        arg_list += (date_from, user_company)
        query = '''
            SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
            FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
            WHERE (l.account_id = account_account.id)
                AND (l.move_id = am.id)
                AND (am.state IN %s)
                AND (account_account.internal_type IN %s)
                AND ''' + reconciliation_clause + '''
                AND (l.date <= %s)
                AND l.company_id = %s
            ORDER BY UPPER(res_partner.name)'''
        cr.execute(query, arg_list)

        partners = cr.dictfetchall()
        
        # put a total of 0
        for i in range(9):
            total.append(0)

        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
        if od_partners:
            partner_ids = od_partners
            
        lines = dict((partner['partner_id'] or False, []) for partner in partners)
        if not partner_ids:
            return [], [], []

        # This dictionary will store the not due amount of all partners
        undue_amounts = {}
        query = ''' '''
        if od_is_invoice_date:
            
            query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND (COALESCE(l.date,l.date) > %s)\
                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                AND (l.date <= %s)
                AND l.company_id = %s'''
                
        else:
        
        
            query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND (COALESCE(l.date_maturity,l.date) > %s)\
                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                AND (l.date <= %s)
                AND l.company_id = %s'''
       
        cr.execute(query, (tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from, user_company))
        if od_account_id:
            query = query +' AND l.account_id =%s'
            cr.execute(query, (tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from, user_company,od_account_id))
            print("exccutinng trade debtor only>>>>>>>>>>>>>>>>>>>")
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        for line in self.env['account.move.line'].browse(aml_ids):
            partner_id = line.partner_id.id or False
            if partner_id not in undue_amounts:
                undue_amounts[partner_id] = 0.0
            line_amount = line.balance
            if line.balance == 0:
                continue
            for partial_line in line.matched_debit_ids:
                if partial_line.create_date[:10] <= date_from:
                    line_amount += partial_line.amount
            for partial_line in line.matched_credit_ids:
                if partial_line.create_date[:10] <= date_from:
                    line_amount -= partial_line.amount
            if not self.env.user.company_id.currency_id.is_zero(line_amount):
                undue_amounts[partner_id] += line_amount
                lines[partner_id].append({
                    'line': line,
                    'amount': line_amount,
                    'period': 8,
                })

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(7):
            args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
            dates_query = ''
            if od_is_invoice_date:
                dates_query = '(COALESCE(l.date,l.date)'
                
            else:
                dates_query = '(COALESCE(l.date_maturity,l.date)'

            if periods[str(i)]['start'] and periods[str(i)]['stop']:

                dates_query += ' BETWEEN %s AND %s)'
                args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
            elif periods[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (periods[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (periods[str(i)]['stop'],)
            args_list += (date_from, user_company)
            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    AND l.company_id = %s'''
            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids):
                partner_id = line.partner_id.id or False
                if partner_id not in partners_amount:
                    partners_amount[partner_id] = 0.0
                line_amount = line.balance
                if line.balance == 0:
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.create_date[:10] <= date_from:
                        line_amount += partial_line.amount
                for partial_line in line.matched_credit_ids:
                    if partial_line.create_date[:10] <= date_from:
                        line_amount -= partial_line.amount

                if not self.env.user.company_id.currency_id.is_zero(line_amount):
                    partners_amount[partner_id] += line_amount
                    lines[partner_id].append({
                        'line': line,
                        'amount': line_amount,
                        'period': i + 1,
                        })
            history.append(partners_amount)

        for partner in partners:
            if partner['partner_id'] is None:
                partner['partner_id'] = False
            at_least_one_amount = False
            values = {}
            undue_amt = 0.0
            if partner['partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
                undue_amt = undue_amounts[partner['partner_id']]

            total[8] = total[8] + undue_amt
            values['direction'] = undue_amt
            if not float_is_zero(values['direction'], precision_rounding=self.env.user.company_id.currency_id.rounding):
                at_least_one_amount = True

            for i in range(7):
                during = False
                if partner['partner_id'] in history[i]:
                    during = [history[i][partner['partner_id']]]
                # Adding counter
                total[(i)] = total[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
                if not float_is_zero(values[str(i)], precision_rounding=self.env.user.company_id.currency_id.rounding):
                    at_least_one_amount = True
            values['total'] = sum([values['direction']] + [values[str(i)] for i in range(7)])
            ## Add for total
            total[(i + 1)] += values['total']
            values['partner_id'] = partner['partner_id']
            if partner['partner_id']:
                browsed_partner = self.env['res.partner'].browse(partner['partner_id'])
                values['name'] = browsed_partner.name and len(browsed_partner.name) >= 45 and browsed_partner.name[0:40] + '...' or browsed_partner.name
                values['trust'] = browsed_partner.trust
            else:
                values['name'] = _('Unknown Partner')
                values['trust'] = False

            if at_least_one_amount:
                res.append(values)

        return res, total, lines

    
    def render_html(self, docids, data=None):
        total = []
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        od_period_lenght1 = data['form']['od_period_lenght1']
        od_period_lenght2 = data['form']['od_period_lenght2']
        od_period_lenght3 = data['form']['od_period_lenght3']
        od_period_lenght4 = data['form']['od_period_lenght4']
        od_period_lenght5 =data['form']['od_period_lenght5']
        od_period_lenght6 = data['form']['od_period_lenght6']
        
        
        od_is_invoice_date = data['form']['od_is_invoice_date']
        od_is_slab = data['form']['od_is_slab']
        od_account_id =data['form']['od_account_id']
        print("od_account_id>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",od_account_id)
        if od_account_id:
            od_account_id = od_account_id[0]
        print("od account id sce>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",od_account_id)
        target_move = data['form'].get('target_move', 'all')
        print("11111111111111111111111111111111111111",target_move)
        date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))

        if data['form']['result_selection'] == 'customer':
            account_type = ['receivable']
        elif data['form']['result_selection'] == 'supplier':
            account_type = ['payable']
        else:
            account_type = ['payable', 'receivable']
        partner = data['form']['partner']
        print("data>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>form>>>>>>>>>>>>>>>>>>>>>>>>",data['form'])
        data['form']['5'] = {'name':5}
        data['form']['6'] = {'name':6}
        movelines, total, dummy = self._get_partner_move_lines(account_type, date_from, target_move, data['form']['period_length'],
                                                               od_period_lenght1,od_period_lenght2,od_period_lenght3,od_period_lenght4,
                                                               od_period_lenght5,od_period_lenght6,
                                                               od_is_slab,od_is_invoice_date,data['form'],partner,od_account_id)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_partner_lines': movelines,
            'get_direction': total,
        }
        return self.env['report'].render('account.report_agedpartnerbalance', docargs)
