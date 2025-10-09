# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models, SUPERUSER_ID, _


class ReportPartnerStatement(models.AbstractModel):

	_name = 'report.orchid_account_enhancement.report_od_partner_statement'

	
# keys=list(dictionary)
# list(set(keys))
# list(filter(lambda d: d['type'] in keyValList, exampleSet))	
	def generate_overdue(self, data):
		# print "dataaaaaaaaaaaaaaaaaaaaaa",data
		overdue_line = []
		partners = {}	
		for debit_line in data['debit']:
			d_obj = self.env['account.move.line'].browse(debit_line['debit_move_id'])
			# print "cccccc_obj!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",d_obj
			invoice_name = ''
			partner_id = d_obj.partner_id
			sales_person = partner_id.user_id.name or False
			# invoice_name = d_obj.move_id.name
			if d_obj.invoice_id:
				invoice_name = d_obj.move_id.name
			else:
				invoice_name = d_obj.move_id.name	
		
					
			dict_line = {}
			date = datetime.strptime(d_obj.date, '%Y-%m-%d')
			date = datetime.strftime(date, "%d/%m/%Y")
			dict_line.update({
				# 'inv_amount':round(d_obj.debit-debit_line['paid_amount'],2),
				'sales_person': sales_person,
				'inv_amount':round(d_obj.debit,2),
				'paid_amount':round(debit_line['paid_amount'],2),
				'date':date,
				'doc_type':d_obj.journal_id.code,
				'lpo_no':d_obj.name or ' ',
				'inv_name':invoice_name,
				'balance':0
				})
			if partner_id.id in partners:
				if round(d_obj.debit-debit_line['paid_amount'],2) > 0:
				# if round(d_obj.debit,2) > 0:
					# print partners[partner_id.id]
					partners[partner_id.id]['info'].append(dict_line)
			else:
				company = partner_id.company_id and True or False
				partners[partner_id.id] = {
				'name':partner_id.name or '',
				'sales_person': sales_person or '',
				'company':company,
				'accountant_name':'',
				'accountant_contact':'',
				'vat':partner_id.vat,
				'ref':partner_id.ref,
				'mobile':partner_id.mobile,
				'fax':partner_id.fax
				}
				if round(d_obj.debit-debit_line['paid_amount'],2) > 0:
					partners[partner_id.id].update({
						'info':[dict_line],
						})
					print("debit>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",debit_line['paid_amount'])
					print("debit>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",d_obj.debit)
				else:
					partners[partner_id.id].update({
						'info':[],
						})
				if not company:
					partners[partner_id.id].update({
						'street':partner_id.street,
						'city':partner_id.city,
						'zip':partner_id.zip,
						})

		for credit_line in data['credit']:
			c_obj = self.env['account.move.line'].browse(credit_line['credit_move_id'])
			# print "cccccc_obj!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",c_obj
			invoice_name = ''
			# invoice_name = d_obj.move_id.name
			partner_id = c_obj.partner_id
			sales_person = partner_id.user_id.name or False
			if c_obj.invoice_id:
				invoice_name = c_obj.move_id.name
			else:
			 	invoice_name = c_obj.move_id.name

			dict_line = {}
			# print credit_line['paid_amount']
			date = datetime.strptime(c_obj.date, '%Y-%m-%d')
			date = datetime.strftime(date, "%d/%m/%Y")
			dict_line.update({
				'sales_person':sales_person,
				'inv_amount':round(credit_line['paid_amount'],2),
				# 'paid_amount':round(c_obj.credit-credit_line['paid_amount'],2),
				'paid_amount':round(c_obj.credit,2),
				'date':date,
				'doc_type':c_obj.journal_id.code,
				'lpo_no':c_obj.name or ' ',
				'inv_name':invoice_name,
				'balance':0
				})
			# print "dict??????????????????????",dict_line
			if partner_id.id in partners:
				if round(c_obj.credit-credit_line['paid_amount'],2) > 0 :
					partners[partner_id.id]['info'].append(dict_line)
			else:
				company = partner_id.company_id and True or False
				partners[partner_id.id] = {
				'name':partner_id.name or '',
				'sales_person': sales_person or '',
				'company':company,
				'accountant_name':'',
				'accountant_contact':'',
				'vat':partner_id.vat,
				'ref':partner_id.ref,
				'mobile':partner_id.mobile,
				'fax':partner_id.fax,
				}
				if round(c_obj.credit-credit_line['paid_amount'],2) > 0:
					partners[partner_id.id].update({
						'info':[dict_line]
						})
				else:
					partners[partner_id.id].update({
						'info':[]
						})
				if not company:
					partners[partner_id.id].update({
						'street':partner_id.street,
						'city':partner_id.city,
						'zip':partner_id.zip,
						})
		for key,value in partners.items():
			# print "overrrrrrr>>>>>>>>>>>>>>>>",value
			overdue_line.append(value)
		return overdue_line
		
	
	
	
	def render_html(self, docids, data=None):
		model = self.env.context.get('active_model')
		docs = self.env[model].browse(self.env.context.get('active_id'))
		overdue_line = self.generate_overdue(data)
		# print overdue_line
		print('llllllllllllllllllllllll')
		print('llllllllllllllllllllllll')
		print('llllllllllllllllllllllll')
		print('llllllllllllllllllllllll')

		if data['filter']['currency_id']:
			currency_name = data['filter']['currency_id'][1]
			print("currency nameeeeeeeee???",currency_name)
		print("account_type................////?????",data['filter']['account_type'])	
		currency_id = data['filter']['currency_id']
		currency_obj = None
		company_currency = self.env.user.company_id.currency_id
		context = dict(self._context or {})
		ctx = context.copy()
		if currency_id:
			currency_obj = self.env['res.currency'].browse(currency_id[0])
		if currency_obj:
			for line in overdue_line:
					for amount in line['info']:
						amount['paid_amount'] = company_currency.with_context(ctx).compute(amount['paid_amount'], currency_obj)
						amount['inv_amount'] = company_currency.with_context(ctx).compute(amount['inv_amount'], currency_obj)
	
		report_obj = self.env['report']
		date = datetime.now()
		docargs = {
			'doc_ids': self.ids,
			'doc_model': model,
			'docs': docs,
			'debit': data['debit'],
			'credit': data['credit'],
			'filter': data['filter'],
			'account_type': data['filter']['account_type'],
			'date_to': data['filter']['date_to'],
			'overdue_line':overdue_line,
			'date': date,
		}
		return self.env['report'].render('orchid_account_enhancement.report_od_partner_statement', docargs)

