# -*- coding: utf-8 -*-
# todo remove , use default
import time
from odoo import api, models
import pandas as pd


class ReportGeneralLedger(models.AbstractModel):
	_inherit = 'report.account.report_generalledger'

	def _get_account_move_entry(self, accounts, init_balance, sortby, display_account,od_move_lines,search_cond,od_template):
		print("1st_deffffffffffffffffffffffffffffffffffffff")
		print("1st_deffffffffffffffffffffffffffffffffffffff")
		print("1st_deffffffffffffffffffffffffffffffffffffff")
		print("1st_deffffffffffffffffffffffffffffffffffffff")
		print("1st_deffffffffffffffffffffffffffffffffffffff")
		print("1st_deffffffffffffffffffffffffffffffffffffff")
		print("1st_deffffffffffffffffffffffffffffffffffffff")
		print("1st_deffffffffffffffffffffffffffffffffffffff")
		print("1st_deffffffffffffffffffffffffffffffffffffff")
		print("1st_deffffffffffffffffffffffffffffffffffffff")
		print("1st_deffffffffffffffffffffffffffffffffffffff")
		"""
		:param:
				accounts: the recordset of accounts
				init_balance: boolean value of initial_balance
				sortby: sorting by date or partner and journal
				display_account: type of account(receivable, payable and both)

		Returns a dictionary of accounts with following key and value {
				'code': account code,
				'name': account name,
				'debit': sum of total debit amount,
				'credit': sum of total credit amount,
				'balance': total balance,
				'amount_currency': sum of amount_currency,
				'move_lines': list of move line
		}
		"""
		cr = self.env.cr
		context=self.env.context
		MoveLine = self.env['account.move.line']
		move_lines = dict([(x, []) for x in accounts.ids])

		# Prepare initial sql query and Get the initial move lines
		if init_balance:
			print("222222222222222222222222222222")
			print("222222222222222222222222222222")
			print("222222222222222222222222222222")
			print("222222222222222222222222222222")
			init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()
			init_wheres = [""]
			if init_where_clause.strip():
				init_wheres.append(init_where_clause.strip())
			init_filters = " AND ".join(init_wheres)
			filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
			sql = ("""SELECT 0 AS lid, cc.name AS cost_center, l.account_id AS account_id, '' AS ldate, '' AS lcode, NULL AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id, '' AS lproduct_id,\
				'' AS move_name, '' AS mmove_id, '' AS currency_code,\
				NULL AS currency_id,\
				'' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
				'' AS partner_name\
				FROM account_move_line l\
				LEFT JOIN account_move m ON (l.move_id=m.id)\
				LEFT JOIN orchid_account_cost_center cc ON (l.orchid_cc_id=cc.id)\
				LEFT JOIN res_currency c ON (l.currency_id=c.id)\
				LEFT JOIN res_partner p ON (l.partner_id=p.id)\
				LEFT JOIN product_template pr ON (l.product_id=pr.id)\
				LEFT JOIN account_invoice i ON (m.id =i.move_id)\
				JOIN account_journal j ON (l.journal_id=j.id)\
				WHERE l.account_id IN %s """ + search_cond + filters + ' GROUP BY l.account_id,l.partner_id,cc.name,l.product_id')
			params = ()
			if od_move_lines:
				params = (tuple(accounts.ids),tuple(od_move_lines.ids),) + tuple(init_where_params)
			else:
				params = (tuple(accounts.ids),) + tuple(init_where_params)
				
				
			
			cr.execute(sql, params)
			for row in cr.dictfetchall():
				if move_lines[row['account_id']]:
					move_lines[row['account_id']][0]['credit'] = move_lines[row['account_id']][0]['credit'] + row['credit']
					move_lines[row['account_id']][0]['debit'] = move_lines[row['account_id']][0]['debit'] + row['debit']
					move_lines[row['account_id']][0]['balance'] = move_lines[row['account_id']][0]['balance'] + row['balance']
				else:
					move_lines[row.pop('account_id')].append(row)

		sql_sort = 'l.date, l.move_id'
		if sortby == 'sort_journal_partner':
			sql_sort = 'j.code, p.name, l.move_id'

		# Prepare sql query base on selected parameters from wizard
		tables, where_clause, where_params = MoveLine._query_get()
		
		wheres = [""]
		if where_clause.strip():
			wheres.append(where_clause.strip())
		filters = " AND ".join(wheres)
		filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

		# Get move lines base on sql query and Calculate the total balance of move lines
		sql = ('''SELECT l.id AS lid, cc.name AS cost_center, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, aac.name as lanalytic_account_name, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
			m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name, pr.name AS product_name \
			FROM account_move_line l\
			JOIN account_move m ON (l.move_id=m.id)\
			LEFT JOIN orchid_account_cost_center cc ON (l.orchid_cc_id=cc.id)\
			LEFT JOIN res_currency c ON (l.currency_id=c.id)\
			LEFT JOIN res_partner p ON (l.partner_id=p.id)\
			LEFT JOIN product_template pr ON (l.product_id=pr.id)\
			LEFT JOIN account_analytic_account aac ON (l.analytic_account_id=aac.id)\
			JOIN account_journal j ON (l.journal_id=j.id)\
			JOIN account_account acc ON (l.account_id = acc.id) \
			WHERE l.account_id IN %s ''' + search_cond + filters + ''' GROUP BY l.id,l.product_id, l.partner_id,l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name, cc.name,pr.name,aac.name ORDER BY ''' + sql_sort)
		params = ()
		print("333333333333333333333333333333333333333333333")
		print("333333333333333333333333333333333333333333333")
		print("333333333333333333333333333333333333333333333")
		print("333333333333333333333333333333333333333333333")
		print(sql)
		# print "where params>>>>>>>>>>>>>>>>>>>>>>>",where_params
		if od_move_lines:
			params = (tuple(accounts.ids),tuple(od_move_lines.ids),) + tuple(where_params)  
		else:
			params = (tuple(accounts.ids),) + tuple(where_params)
		dt_context = context.get('dt_cont',{})
		date_from ,date_to = self.env.context.get('date_from',False),self.env.context.get('date_to',False)  
		print("datessssssssssssssssssssssssssssssssssssssss")
		print("datessssssssssssssssssssssssssssssssssssssss")
		print("datessssssssssssssssssssssssssssssssssssssss")
		print("date_frommmmmmmmmmmmmmmm",date_from)
		print("date_toooooooooooooooooo",date_to)
		if date_from and not date_to:
			print("44444444444444444444444444444444444444444444444444")
			print("44444444444444444444444444444444444444444444444444")
			print("44444444444444444444444444444444444444444444444444")
			print("44444444444444444444444444444444444444444444444444")
			print("44444444444444444444444444444444444444444444444444")
			sql = ('''SELECT l.id AS lid, cc.name AS cost_center, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname,aac.name as lanalytic_account_name, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
			m.name AS move_name, pr.name AS product_name, c.symbol AS currency_code, p.name AS partner_name \
			FROM account_move_line l\
			JOIN account_move m ON (l.move_id=m.id)\
			LEFT JOIN orchid_account_cost_center cc ON (l.orchid_cc_id=cc.id)\
			LEFT JOIN res_currency c ON (l.currency_id=c.id)\
			LEFT JOIN res_partner p ON (l.partner_id=p.id)\
			LEFT JOIN product_template pr ON (l.product_id=pr.id)\
			LEFT JOIN account_analytic_account aac ON (l.analytic_account_id=aac.id)\
			JOIN account_journal j ON (l.journal_id=j.id)\
			JOIN account_account acc ON (l.account_id = acc.id) \
			WHERE l.date >= %s and l.account_id IN %s ''' + search_cond + filters + ''' GROUP BY l.id, l.product_id , l.partner_id,l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, pr.name, aac.name, c.symbol, p.name, cc.name ORDER BY ''' + sql_sort)
			params = (date_from,) + params
			
		if date_to and not date_from:
			print("5555555555555555555555555555555555555555555555555555555")
			print("5555555555555555555555555555555555555555555555555555555")
			print("5555555555555555555555555555555555555555555555555555555")
			print("5555555555555555555555555555555555555555555555555555555")
			print("5555555555555555555555555555555555555555555555555555555")
			sql = ('''SELECT l.id AS lid, cc.name AS cost_center, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname,aac.name as lanalytic_account_name, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
			m.name AS move_name, pr.name AS product_name, c.symbol AS currency_code, p.name AS partner_name  \
			FROM account_move_line l\
			JOIN account_move m ON (l.move_id=m.id)\
			LEFT JOIN orchid_account_cost_center cc ON (l.orchid_cc_id=cc.id)\
			LEFT JOIN res_currency c ON (l.currency_id=c.id)\
			LEFT JOIN res_partner p ON (l.partner_id=p.id)\
			LEFT JOIN product_template pr ON (l.product_id=pr.id)\
			LEFT JOIN account_analytic_account aac ON (l.analytic_account_id=aac.id)\
			JOIN account_journal j ON (l.journal_id=j.id)\
			JOIN account_account acc ON (l.account_id = acc.id) \
			WHERE l.date <= %s and l.account_id IN %s ''' + search_cond + filters + ''' GROUP BY l.id, l.product_id, l.partner_id,l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name, pr.name, aac.name, cc.name ORDER BY ''' + sql_sort)
			params = (date_to,) + params
			
		if date_from and date_to:
			print("666666666666666666666666666666666666666666666666666666666")
			print("666666666666666666666666666666666666666666666666666666666")
			print("666666666666666666666666666666666666666666666666666666666")
			print("666666666666666666666666666666666666666666666666666666666")
			sql = ('''SELECT l.id AS lid, cc.name AS cost_center, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname,aac.name as lanalytic_account_name, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
			m.name AS move_name, pr.name AS product_name, c.symbol AS currency_code, p.name AS partner_name\
			FROM account_move_line l\
			JOIN account_move m ON (l.move_id=m.id)\
			LEFT JOIN orchid_account_cost_center cc ON (l.orchid_cc_id=cc.id)\
			LEFT JOIN res_currency c ON (l.currency_id=c.id)\
			LEFT JOIN res_partner p ON (l.partner_id=p.id)\
			LEFT JOIN account_analytic_account aac ON (l.analytic_account_id=aac.id)\
			LEFT JOIN product_template pr ON (l.product_id=pr.id)\
			JOIN account_journal j ON (l.journal_id=j.id)\
			JOIN account_account acc ON (l.account_id = acc.id) \
			WHERE l.date>=%s and l.date <= %s and l.account_id IN %s ''' + search_cond + filters + ''' GROUP BY l.id, l.product_id, l.partner_id,l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, pr.name, aac.name, c.symbol, p.name, cc.name ORDER BY ''' + sql_sort)
			params = (date_from,date_to,) + params
			print("vbt-sqlllllllllllllllllllllllllllllllllllllllllllllllllll")
			print("vbt-sqlllllllllllllllllllllllllllllllllllllllllllllllllll")
			print("vbt-sqlllllllllllllllllllllllllllllllllllllllllllllllllll")
			print("vbt-sqlllllllllllllllllllllllllllllllllllllllllllllllllll")
			print(sql)
			

			
			
		cr.execute(sql, params)

		for row in cr.dictfetchall():
			balance = 0
			for line in move_lines.get(row['account_id']):
				balance += line['debit'] - line['credit']
			row['balance'] += balance
			move_lines[row.pop('account_id')].append(row)

		# Calculate the debit, credit and balance for Accounts
		account_res = []
		for account in accounts:
			currency = account.currency_id and account.currency_id or account.company_id.currency_id
			res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
			res['code'] = account.code
			res['name'] = account.name
			res['move_lines'] = move_lines[account.id]
			for line in res.get('move_lines'):
				res['debit'] += line['debit']
				res['credit'] += line['credit']
				res['balance'] = line['balance']
			if display_account == 'all':
				account_res.append(res)
			if display_account == 'movement' and res.get('move_lines'):
				account_res.append(res)
			if display_account == 'not_zero' and not currency.is_zero(res['balance']):
				account_res.append(res)

		if od_template:
			template_res = []
			for line in account_res:
				result = {}
				acc_df = pd.DataFrame(line['move_lines'])
				if od_template=='daily':
					acc_grp = acc_df.groupby(['ldate']).sum()
				if od_template=='monthly':
					acc_df['yearmonth']=acc_df['ldate'].apply(lambda x: self.getYearMonth(x))
					acc_grp=acc_df.groupby(['yearmonth']).sum()					
				template_dict = dict()
				template_dict['move_lines'] = []
				template_dict['debit'] = 0
				template_dict['credit'] = 0
				template_dict['balance'] = 0
				template_dict['code'] = line['code']
				template_dict['name'] = line['name']
				for index,row in acc_grp.iterrows():
					result = {}
					balance=0
					row.balance=row.debit.item()-row.credit.item()
					result['ldate']=row.name
					result['debit']=row.debit.item()
					result['credit']=row.credit.item()
					result['balance']=row.balance
					template_dict['debit'] += row.debit.item()
					template_dict['credit'] += row.credit.item()
					template_dict['balance'] += row.balance
					template_dict['move_lines'].append(result)
				template_res.append(template_dict)

		if od_template:
			return template_res
		else:
			return account_res

	
	def render_html(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
		init_balance = data['form'].get('initial_balance', True)
		sortby = data['form'].get('sortby', 'sort_date')
		display_account = data['form']['display_account']
		od_template = data['form']['od_template']

		codes = []
		cost_centers = []
		
		od_move_lines = data['od_move_lines']
		od_move_lines = self.env['account.move.line'].browse(od_move_lines)
		search_cond = ''' '''
		if od_move_lines:
			search_cond = search_cond + ''' and l.id in %s '''
			
		if data['form'].get('journal_ids', False):
			codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]

		for cc in data['form']['cost_center_ids']:
			cc_name = self.env['orchid.account.cost.center'].browse(cc).name
			cost_centers.append(cc_name)

		accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])

		accounts_res = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry(accounts, init_balance, sortby, display_account,od_move_lines,search_cond,od_template)

		docargs = {
			'doc_ids': docids,
			'doc_model': self.model,
			'data': data['form'],
			'docs': docs,
			'time': time,
			'Accounts': accounts_res,
			'print_journal': codes,
			'cost_center': cost_centers,
		}
		return self.env['report'].render('account.report_generalledger', docargs)

	def getYearMonth(self,s):
		return s.split("-")[0]+"-"+s.split("-")[1]
