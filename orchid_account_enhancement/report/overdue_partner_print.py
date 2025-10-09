# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models, SUPERUSER_ID, _


class ReportPartnerOverdue(models.AbstractModel):

	_name = 'report.orchid_account_enhancement.report_partner_overdue'

	
	
	def od_deduplicate(self,l):
		result = []
		for item in l :
			check = False
			# check item, is it exist in result yet (r_item)
			for r_item in result :
				if item['id'] == r_item['id'] :
					# if found, add all key to r_item ( previous record)
					check = True
					amount = item['amount'] 
					amount += r_item['amount']
					r_item['amount'] = amount
				
					
			if check == False :
				# if not found, add item to result (new record)
				result.append( item )
	
		return result
	
	
	
	def render_html(self, docids, data=None):
		model = self.env.context.get('active_model')
		docs = self.env[model].browse(self.env.context.get('active_id'))
		report_obj = self.env['report']
		all_lines = []
		dict_line = {}
		currency_name = ""
		if data['form']['currency_id']:
			currency_name = data['form']['currency_id'][1]
		for partner in data['form']['partner_ids']:
			print(partner,'**********************')
			dict_line = {}
			partner_obj = self.env['res.partner'].browse(partner)
			partner_name = partner_obj.name
			lines = self.generate_pdf_data(data['form'],partner)

			company = partner_obj.company_id and True or False
			dict_line.update({'info': lines, 'name': partner_name,'company':company,'currency':currency_name})
			if not partner_obj.company_id:
				dict_line.update({'street':partner_obj.street,'city':partner_obj.city,'zip':partner_obj.zip,})
			all_lines.append(dict_line)
			print(all_lines)
		print('all_lines',all_lines)
		date = datetime.now()
		docargs = {
			'doc_ids': self.ids,
			'doc_model': model,
			'docs': docs,
			'time': time,
			'get_overdue_lines': all_lines,
			'form_filters': data['form'],
			'date':date,
		}
		return self.env['report'].render('orchid_account_enhancement.report_partner_overdue', docargs)


	def generate_pdf_data(self,form_data,ppartner_id):
		mode = form_data['mode']
		date_from = form_data['date_from']
		date_to = form_data['date_to']
		account_type = form_data['account_type']
		currency_id = form_data['currency_id']
		currency_obj = None
		# company_currency = self.env['res.company']._company_default_get('orchid_account_enhancement').currency_id
		company_currency = self.env.user.company_id.currency_id
		print('CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC',company_currency)
		context = dict(self._context or {})
		ctx = context.copy()

		if currency_id:
			currency_obj = self.env['res.currency'].browse(currency_id[0])
		row_data = []
		print(account_type,'account_typeaccount_typeaccount_type')
		if account_type == 'recievable':
			print('inside')
			row_data = []
	#        if account_type != 'recievable':
	#            raise UserError(_('the options payable,both are under construction...'))
			custom_where_query = ""
			if date_from:
				custom_where_query = custom_where_query + " and mv.date > '" + date_from + "'"
			if date_to:
				if custom_where_query != "":
					custom_where_query = custom_where_query + " and mv.date < '" + date_to + "'"        
				
			partner_ids = []
			#partner_id = form_data.partner_id and form_data.partner_id.id 
			salesman_id = form_data['salesman_id']
			partners = [ppartner_id]#form_data['partner_ids']
			for p in partners:
				partner_ids.append(p)    
	
			if len(partner_ids) <= 0:
			
				raise UserError(_('the selection crieteria for partner invalid'))
			account_ids = form_data['account_ids']
			accts = []
			for acc in account_ids:
				accts.append(acc)
			# if len(accts) == 1:
			# 	raise UserError(_('The account wise option is under construction'))
			existing_ids = self.env['od.overdue'].search([])
			existing_ids.unlink()
			if mode == 'details':
				return self._get_details_lines(partner_ids,accts)
			#start
			partner_obj = self.env['res.partner']
			move_line_obj = self.env['account.move.line']
			
			move_lines =[]
			for part in partner_ids:
				
				partner_id=partner_obj.browse(part)
				print(partner_id)
				account_id = partner_id and partner_id.property_account_receivable_id and partner_id.property_account_receivable_id.id
# 				move_line_ids = []
# 				move_line_debit_ids = [] 
				
				move_lines+= self.env['account.move.line'].get_move_lines_for_manual_reconciliation(account_id, partner_id=partner_id.id, excluded_ids=None, str=False, offset=0, limit=None, target_currency_id=None)
				print(move_lines)
				print(currency_id and currency_id[0])
				print('YYYYYY')
			debit_lines = [] #invoices
			credit_lines = [] #payments

			
			for line in move_lines:
								
				if round(line.get('debit',0.0)) != 0.0:
					if currency_obj:
						line['balance'] = company_currency.with_context(ctx).compute(line['debit'], currency_obj)
					else:
						line['balance'] = line['debit']
					debit_lines.append(line)
				if round(line.get('credit',0.0)) != 0.0 :
					if currency_obj:
						line['balance'] = company_currency.with_context(ctx).compute(line['credit'], currency_obj)
					else:
						line['balance'] = line['credit']
					credit_lines.append(line)
			
			#iterate over invoice move lines
			for line in debit_lines:
				if date_from and date_to:
					if line.get('date') >= date_from and line.get('date') <= date_to:
						mv_line = move_line_obj.browse(line.get('id'))
						mv_name = mv_line.move_id and mv_line.move_id.name or ''
						if currency_obj:
							debit = company_currency.with_context(ctx).compute(mv_line.debit, currency_obj)
						else:
							debit = mv_line.debit
						balance = line.get('balance')
						credit = debit - balance
						
						
						vals1 = {'partner_id':line.get('partner_id'),
							'partner_name':line.get('partner_name'),
							'label':mv_line.name,
							'ref':mv_line.ref,
							'journal_code':line.get('journal_name'),
							'number':mv_name,
							'date':datetime.strptime(line.get('date'), '%Y-%m-%d'),
							'due_date':line.get('date_maturity'),
							'debit':debit,
							'credit':credit,
							'balance':debit - credit,
							'od_released':False,
							'pdc':False
							}
						row_data.append(vals1)
				else:
					mv_line = move_line_obj.browse(line.get('id'))
					mv_name = mv_line.move_id and mv_line.move_id.name or ''
					if currency_obj:
						debit = company_currency.with_context(ctx).compute(mv_line.debit, currency_obj)
					else:
						debit = mv_line.debit
					balance = line.get('balance')
					credit = debit - balance
					
					
					vals1 = {'partner_id':line.get('partner_id'),
						'partner_name':line.get('partner_name'),
						'label':mv_line.name,
						'ref':mv_line.ref,
						'journal_code':line.get('journal_name'),
						'number':mv_name,
						'date':datetime.strptime(line.get('date'), '%Y-%m-%d'),
						'due_date':line.get('date_maturity'),
						'debit':debit,
						'credit':credit,
						'balance':debit - credit,
						'od_released':False,
						'pdc':False
						}
					row_data.append(vals1)
			
			print("credit lines>>>>>>>>>>>>>>>>",credit_lines)
			
			for line in credit_lines:
				if date_from and date_to:
					if line.get('date') >= date_from and line.get('date') <= date_to:
						mv_line = move_line_obj.browse(line.get('id'))
						mv_name = mv_line.move_id and mv_line.move_id.name or ''
						ap = mv_line.payment_id
						od_released = ap and ap.od_released
						pdc = ap and  ap.is_clearing 
						balance = line.get('balance')
						
						
		# 				
						
						
						
						vals1 = {'partner_id':line.get('partner_id'),
							'partner_name':line.get('partner_name'),
							'label':mv_line.name,
							'ref':mv_line.ref,
							'journal_code':line.get('journal_name'),
							'number':mv_name,
							'date':datetime.strptime(line.get('date'), '%Y-%m-%d'),
							'due_date':line.get('date_maturity'),
							'debit':0.0,
							'credit':balance,
							'balance':balance,
							'od_released':od_released,
							'pdc':pdc,
							}
						row_data.append(vals1)
				else:
					mv_line = move_line_obj.browse(line.get('id'))
					mv_name = mv_line.move_id and mv_line.move_id.name or ''
					ap = mv_line.payment_id
					od_released = ap and ap.od_released
					pdc = ap and  ap.is_clearing 
					balance = line.get('balance')
					
					
	# 				
					
					
					
					vals1 = {'partner_id':line.get('partner_id'),
						'partner_name':line.get('partner_name'),
						'label':mv_line.name,
						'ref':mv_line.ref,
						'journal_code':line.get('journal_name'),
						'number':mv_name,
						'date':datetime.strptime(line.get('date'), '%Y-%m-%d'),
						'due_date':line.get('date_maturity'),
						'debit':0.0,
						'credit':balance,
						'balance':balance,
						'od_released':od_released,
						'pdc':pdc,
						}
					row_data.append(vals1)
				 
		if account_type == 'payable':
			row_data = []
	
			custom_where_query = ""
			if date_from:
				custom_where_query = custom_where_query + " and mv.date > '" + date_from + "'"
			if date_to:
				if custom_where_query != "":
					custom_where_query = custom_where_query + " and mv.date < '" + date_to + "'"        
				
			partner_ids = []
			#partner_id = form_data.partner_id and form_data.partner_id.id 
			salesman_id = form_data['salesman_id']
			partners = [ppartner_id]#form_data['partner_ids']
			# print form_data,'LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL'
			for p in partners:
				partner_ids.append(p)    
	
			if len(partner_ids) <= 0:
			
				raise UserError(_('the selection crieteria for partner invalid'))
			account_ids = form_data['account_ids']
			accts = []
			for acc in account_ids:
				accts.append(acc)
			# if len(accts) == 1:
			# 	raise UserError(_('The account wise option is under construction'))
			existing_ids = self.env['od.overdue'].search([])
			existing_ids.unlink()
			if mode == 'details':
				return self._get_details_lines(partner_ids,accts)
			
			partner_obj = self.env['res.partner']
			move_line_obj = self.env['account.move.line']
			
			move_lines =[]
			for part in partner_ids:
				
				partner_id=partner_obj.browse(part)
				account_id = partner_id and partner_id.property_account_payable_id and partner_id.property_account_payable_id.id
				move_line_ids = []
				move_line_debit_ids = []
				
				move_lines+= self.env['account.move.line'].get_move_lines_for_manual_reconciliation(account_id, partner_id=partner_id.id, excluded_ids=None, str=False, offset=0, limit=None, target_currency_id=None)
			debit_lines = [] #payments
			credit_lines = [] #invoices

			
			for line in move_lines:
				
				
				if round(line.get('debit',0.0)) != 0.0:
					if currency_obj:
						line['balance'] = company_currency.with_context(ctx).compute(line['debit'], currency_obj)
					else:
						line['balance'] = line['debit']
					debit_lines.append(line)
				if round(line.get('credit',0.0)) != 0.0 :
					if currency_obj:
						line['balance'] = company_currency.with_context(ctx).compute(line['credit'], currency_obj)
					else:
						line['balance'] = line['credit']
					credit_lines.append(line)
			
			#iterate over vendor bill move lines
			for line in credit_lines:
				if date_from and date_to:
					if line.get('date') >= date_from and line.get('date') <= date_to:
						mv_line = move_line_obj.browse(line.get('id'))
						mv_name = mv_line.move_id and mv_line.move_id.name or ''
						if currency_obj:
							debit = company_currency.with_context(ctx).compute(mv_line.credit, currency_obj)
						else:
							debit = mv_line.credit
						balance = line.get('balance')
						credit = debit - balance
						
						
						vals1 = {'partner_id':line.get('partner_id'),
							'partner_name':line.get('partner_name'),
							'label':mv_line.name,
							'ref':mv_line.ref,
							'journal_code':line.get('journal_name'),
							'number':mv_name,
							'date':datetime.strptime(line.get('date'), '%Y-%m-%d'),
							'due_date':line.get('date_maturity'),
							'debit':debit,
							'credit':credit,
							'balance':debit - credit,
							'od_released':False,
							'pdc':False
							}
						row_data.append(vals1)
				else:
					mv_line = move_line_obj.browse(line.get('id'))
					mv_name = mv_line.move_id and mv_line.move_id.name or ''
					if currency_obj:
						debit = company_currency.with_context(ctx).compute(mv_line.credit, currency_obj)
					else:
						debit = mv_line.credit
					balance = line.get('balance')
					credit = debit - balance
					
					
					vals1 = {'partner_id':line.get('partner_id'),
						'partner_name':line.get('partner_name'),
						'label':mv_line.name,
						'ref':mv_line.ref,
						'journal_code':line.get('journal_name'),
						'number':mv_name,
						'date':datetime.strptime(line.get('date'), '%Y-%m-%d'),
						'due_date':line.get('date_maturity'),
						'debit':debit,
						'credit':credit,
						'balance':debit - credit,
						'od_released':False,
						'pdc':False
						}
					row_data.append(vals1)					
			
			print("debt lines>>>>>>>>>>>>>>>>",debit_lines)
			
			for line in debit_lines:
				if date_from and date_to:
					if line.get('date') >= date_from and line.get('date') <= date_to:
						mv_line = move_line_obj.browse(line.get('id'))
						mv_name = mv_line.move_id and mv_line.move_id.name or ''
						ap = mv_line.payment_id
						od_released = ap and ap.od_released
						pdc = ap and  ap.is_clearing 
						balance = line.get('balance')
						
						
		# 				
						
						
						
						vals1 = {'partner_id':line.get('partner_id'),
							'partner_name':line.get('partner_name'),
							'label':mv_line.name,
							'ref':mv_line.ref,
							'journal_code':line.get('journal_name'),
							'number':mv_name,
							'date':datetime.strptime(line.get('date'), '%Y-%m-%d'),
							'due_date':line.get('date_maturity'),
							'debit':0.0,
							'credit':balance,
							'balance':balance,
							'od_released':od_released,
							'pdc':pdc,
							}
						row_data.append(vals1)
				else:
					mv_line = move_line_obj.browse(line.get('id'))
					mv_name = mv_line.move_id and mv_line.move_id.name or ''
					ap = mv_line.payment_id
					od_released = ap and ap.od_released
					pdc = ap and  ap.is_clearing 
					balance = line.get('balance')
					
					
	# 				
					
					
					
					vals1 = {'partner_id':line.get('partner_id'),
						'partner_name':line.get('partner_name'),
						'label':mv_line.name,
						'ref':mv_line.ref,
						'journal_code':line.get('journal_name'),
						'number':mv_name,
						'date':datetime.strptime(line.get('date'), '%Y-%m-%d'),
						'due_date':line.get('date_maturity'),
						'debit':0.0,
						'credit':balance,
						'balance':balance,
						'od_released':od_released,
						'pdc':pdc,
						}
					row_data.append(vals1)
				

							
		return row_data



	def _get_details_lines(self,partner_id,accts):
		raise UserError(_('the detailed report is under construction'))
		
		qry ="SELECT  mvl.partner_id,mvl.name,mvl.date_maturity,mvl.ref,mvl.invoice_id,mvl.id,mvl.debit,mvl.credit from account_move_line mvl \
					WHERE   mvl.partner_id = '"+str(partner_id)+"' and mvl.account_id in "+str(tuple(accts))+" and mvl.debit >0"+"GROUP BY mvl.id,mvl.debit,mvl.credit;" 
		exc1 = self._cr.execute(qry_without_inv)
		result_witout_inv = self._cr.fetchall()