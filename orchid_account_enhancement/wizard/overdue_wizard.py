# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
import xlwt
from io import StringIO
import base64

class ODoverdue(models.TransientModel):
	_name = 'od.overdue.wizard'
	_description = 'Overdue Wizard'
	partner_id = fields.Many2one('res.partner','Partner')
	salesman_id = fields.Many2one('res.users','Salesman')
	date_from = fields.Date(string='Date From')
	date_to = fields.Date(string='Date To')
	account_ids = fields.Many2many('account.account',string='Accounts')
	partner_ids = fields.Many2many('res.partner',string='Partner')
	account_type = fields.Selection([
		('receivable', 'Recievable'),
		('payable', 'Payable'),
		], string='What do you want?',default='receivable')
	mode = fields.Selection([
		# ('details', 'Details'),
		('outstanding', 'Outstanding'),
		], string='Mode',default='outstanding')
	currency_id = fields.Many2one('res.currency', string='Account Currency')
	excel_file = fields.Binary(string='Dowload Report Excel',readonly=True)
	file_name = fields.Char(string='Excel File',readonly=True)

	def _build_contexts(self, data):
		result = {}
		result['account_ids'] = 'account_ids' in data['form'] and data['form']['account_ids'] or False
		result['date_from'] = data['form']['date_from'] or False
		result['date_to'] = data['form']['date_to'] or False
		result['partner_ids'] = data['form']['partner_ids'] or False
		result['mode'] = data['form']['mode'] or False
		result['account_type'] = data['form']['account_type'] or False
		result['salesman_id'] = data['form']['salesman_id'] or False
	
		if result['partner_ids'] and len(result['partner_ids']) < 1:
			raise UserError(_('no partner defined'))
		# if len(result['account_ids']) == 1:
		#     raise UserError(_('The account wise option is under construction'))
			
#        if result['account_type'] !='receivable':
##            raise UserError(_('the options payable,both are under construction...'))
			
		return result

	
	def check_report(self):
		self.ensure_one()
		data = {}
		data['ids'] = self.env.context.get('active_ids', [])
		data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(['date_from', 'date_to', 'account_ids', 'partner_ids','mode','account_type','salesman_id','currency_id'])[0]
		used_context = self._build_contexts(data)
		data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
		return self._print_report(data)        
	def _print_report(self, data):
		return self.env['report'].with_context(landscape=True).get_action(self, 'orchid_account_enhancement.report_partner_overdue', data=data)
	
	
	def generate(self):
		if not self.account_ids:
			raise UserError(('Select accounts!!'))
		mode = self.mode
		date_from = self.date_from
		date_to = self.date_to
		account_type = self.account_type
#        if account_type != 'receivable':
#            raise UserError(_('the options payable,both are under construction...'))
		custom_where_query = ""
		if date_from:
			custom_where_query = custom_where_query + " and mv.date > '" + date_from + "'"
		if date_to:
			if custom_where_query != "":
				custom_where_query = custom_where_query + " and mv.date < '" + date_to + "'"        
			
		partner_ids = []
		#partner_id = self.partner_id and self.partner_id.id 
		# od_area_id = self.od_area_id and self.od_area_id.id 
		# od_group_id = self.od_group_id and self.od_group_id.id 
		# od_sub_group_id = self.od_sub_group_id and self.od_sub_group_id.id       
		salesman_id = self.salesman_id and self.salesman_id.id       
		partners = self.partner_ids
		for p in partners:
			partner_ids.append(p.id)    

		if len(partner_ids) <= 0:
		
			raise UserError(_('the selection crieteria for partner invalid'))
		account_ids = self.account_ids
		accts = []
		for acc in account_ids:
			accts.append(acc and acc.id)
		# if len(accts) == 1:
		#     raise UserError(_('The account wise option is under construction'))
		existing_ids = self.env['od.overdue'].search([])
		existing_ids.unlink()
		if mode == 'details':
			return self._get_details_lines(partner_ids,accts)
		for part in partner_ids:
			move_line_ids = []
			move_line_debit_ids = []
		
			qry_inv ="SELECT  mvl.partner_id,\
		mvl.name,\
		mvl.date_maturity,\
		mvl.ref,\
		mvl.invoice_id,\
		mvl.id,\
		mvl.debit,\
		mvl.credit,\
		sum(reco.amount),\
		mv.name,\
		mv.ref,\
		mv.date,\
		mvl.journal_id\
		from account_move_line mvl \
			LEFT JOin account_partial_reconcile reco on mvl.id = reco.debit_move_id \
			LEFT JOin account_move mv on mvl.move_id = mv.id \
					WHERE   mvl.partner_id = '"+str(part)+"' and mvl.account_id in "+str(tuple(accts))+" and mvl.debit >0"+custom_where_query+"GROUP BY mvl.id,mvl.debit,mvl.credit,mv.name,mv.ref,mv.date order by mv.date asc;"
					
			exc = self._cr.execute(qry_inv)
			result = self._cr.fetchall()                    
			qry_new ="SELECT  mvl.partner_id,\
		mvl.name,\
		mvl.date_maturity,\
		mvl.invoice_id,\
		mvl.id,\
		mvl.debit,\
		mvl.credit,\
		mv.name,\
		mv.date,\
		mv.ref,\
		mvl.journal_id\
		from account_move_line mvl \
LEFT JOin account_move mv on mvl.move_id = mv.id \
					WHERE   mvl.partner_id = '"+str(part)+"' and mvl.account_id in "+str(tuple(accts))+""+"GROUP BY mvl.id,mvl.debit,mvl.credit,mv.name,mv.ref,mv.date order by mv.date;"
					
			excec = self._cr.execute(qry_new)
			new_result = self._cr.fetchall()
			if new_result:            
				for new_line in new_result:
					paid = 0
					move_line_obj = self.env['account.move.line'].browse(new_line[4])
					if move_line_obj.payment_id and move_line_obj.payment_id.id:
						pay_obj = move_line_obj.payment_id
						if pay_obj:
							is_clearing = pay_obj.is_clearing
							od_released = pay_obj.od_released
							if (is_clearing and od_released) or (is_clearing and not od_released):
								move_line_ids.append(move_line_obj)

			for line in result:         
				partner_name = self.env['res.partner'].browse(line[0]).name
				journal_code = self.env['account.journal'].browse(line[12]).code
				paid = 0
				inv = 0
				od_debit = 0
				od_credit = 0
				if type(line[8]) is float:
					paid = line[8]
					od_credit = line[8]
				if type(line[6]) is float:
					inv = line[6]
					od_debit = line[6]
				if account_type == 'payable':
					temp = od_credit
					od_credit = od_debit
					od_debit = temp
					
				if round(float(inv),2) != round(float(paid),2):
					vals = {'partner_id':line[0],'partner_name':partner_name,'label':line[1],'journal_code':journal_code,'ref':line[10],'number':line[9],'date':datetime.strptime(line[11], '%Y-%m-%d'),'due_date':line[2],'debit':od_debit,'credit':od_credit,'balance':(od_debit - od_credit),'od_released':False,'pdc':False
					}  
				
					self.env['od.overdue'].create(vals)
			qry_without_inv ="select  mvl.partner_id,\
			mvl.name,\
			mvl.date_maturity,\
			mvl.ref,\
			mvl.payment_id,\
			mvl.invoice_id,\
			mvl.id,\
			mvl.debit,\
			mvl.credit,\
			mv.name,\
			mv.ref,\
			mv.date,\
			ap.od_released,\
			ap.is_clearing,\
			mvl.journal_id\
			from account_move_line mvl LEFT JOin account_move mv on mvl.move_id = mv.id\
			left join account_payment ap on mvl.payment_id = ap.id\
					where  mvl.id not in (select credit_move_id from account_partial_reconcile ) and mvl.partner_id = '"+str(part)+"' and mvl.account_id in "+str(tuple(accts))+" and mvl.credit >0"+"group by mvl.id,mvl.debit,mvl.credit,mv.name,mv.ref,mv.date,ap.od_released,ap.is_clearing order by mv.date;" 
			exc1 = self._cr.execute(qry_without_inv) 
			result_witout_inv = self._cr.fetchall()         
			for line1 in result_witout_inv:             
			
				partner_name = self.env['res.partner'].browse(line1[0]).name
				journal_code = self.env['account.journal'].browse(line1[14]).code
				debit = 0
				od_debit = 0
				od_credit = 0
				move_line_debit_ids.append(self.env['account.move.line'].browse(line1[6]))
				if type(line1[7]) is float:
					debit = line1[7]
					od_debit = line1[7]
				adv = 0
				if type(line1[8]) is float:
					adv = line1[8]
					od_credit = line1[8]
				if account_type == 'payable':
					temp = od_credit
					od_credit = od_debit
					od_debit = temp
				vals1 = {'partner_id':line1[0],
				'partner_name':partner_name,
				'label':line1[1],
				'ref':line1[3],
				'journal_code':journal_code,
				'number':line1[9],
				'date':datetime.strptime(line1[11], '%Y-%m-%d'),
				'due_date':line1[2],
				'debit':od_debit,
				'credit':od_credit,
				'balance':(od_debit-od_credit),
				'od_released':line1[12],
				'pdc':line1[13]}
				if not vals1['od_released'] and vals1['debit'] != 0:
					self.env['od.overdue'].create(vals1)
			for move_line in move_line_ids: 
			
				if move_line not in move_line_debit_ids:
					vals2 = {'partner_id':move_line.partner_id.id,
						'label':move_line.name,
						'ref':move_line.ref,
						'journal_code': move_line.journal_id and move_line.journal_id.code or 'None',
						'number':move_line.move_id and move_line.move_id.name,
						'date':datetime.strptime(move_line.move_id and move_line.move_id.date, '%Y-%m-%d'),
						'due_date':move_line.date_maturity,
						'debit':move_line.debit,
						'credit':move_line.credit,
						'balance':(move_line.debit-move_line.credit),
						'pdc':True,
						'od_released':move_line.payment_id.od_released,
					

					}
					if not vals2['od_released'] and vals2['debit'] != 0:
						self.env['od.overdue'].create(vals2)                        
		return {
			  'name':'Overdue Report',
			  'view_type': 'form',
			  "view_mode": 'tree',
			  'res_model': 'od.overdue',
			  'type': 'ir.actions.act_window',
		}
	def _get_details_lines(self,partner_id,accts):
		raise UserError(_('the detailed report is under construction'))
		
		qry ="SELECT  mvl.partner_id,mvl.name,mvl.date_maturity,mvl.ref,mvl.invoice_id,mvl.id,mvl.debit,mvl.credit from account_move_line mvl \
					WHERE   mvl.partner_id = '"+str(partner_id)+"' and mvl.account_id in "+str(tuple(accts))+" and mvl.debit >0"+"GROUP BY mvl.id,mvl.debit,mvl.credit;" 
		exc1 = self._cr.execute(qry_without_inv)
		result_witout_inv = self._cr.fetchall()

	
	def list_partner(self):
		search_cond = []
		if self.account_type == 'payable':
			search_cond = [('supplier','=',True)]
		else:
			search_cond = [('customer','!=',False)]
		partner_ids = []
		# if self.od_group_id:
		#     search_cond.append(('od_group_id','=',self.od_group_id and self.od_group_id.id))
		# if self.od_sub_group_id:
		#     search_cond.append(('od_sub_group_id','=',self.od_sub_group_id and self.od_sub_group_id.id))
		# if self.od_area_id:
		#     search_cond.append(('od_area_id','=',self.od_area_id and self.od_area_id.id))
		if self.salesman_id:
			search_cond.append(('user_id','=',self.salesman_id and self.salesman_id.id))
		partner_obj = self.env['res.partner'].search(search_cond)   
		for part in partner_obj:
			partner_ids.append(part.id)
		self.partner_ids = [(6,0,partner_ids)]
		return {
			'name': _('Overdue Report'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'od.overdue.wizard',
			'res_id': self.id,
			'target': 'new',
			'type': 'ir.actions.act_window',
		}         
		
	
	def update_account_type(self):
		account_type = self.account_type
		acc_ids = []
		if account_type == 'receivable':
			account_ids = self.env['account.account'].search([('internal_type','=','receivable')])
			for acc in account_ids:
				acc_ids.append(acc and acc.id)
		else:
			account_ids = self.env['account.account'].search([('internal_type','=','payable')])
			for acc in account_ids:
				acc_ids.append(acc and acc.id)
		values = {
			'account_ids':[(6,0,acc_ids)],
		}
		self.update(values)
		return {
			'name': _('Overdue Report'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'od.overdue.wizard',
			'res_id': self.id,
			'target': 'new',
			'type': 'ir.actions.act_window',
		}       

	def get_partial_reconsile_data(self):
		data = {}
		cr = self.env.cr
		data['form'] = self.read(['date_from', 'date_to', 'account_ids', 'partner_ids','mode','account_type','salesman_id','od_group_id','od_sub_group_id','od_area_id','currency_id'])[0]
		result = self._build_contexts(data)
		cust_query = '(COALESCE(mvl.date,mvl.date_maturity)'
		date_query = '(COALESCE(mvl.date,mvl.date_maturity)'
		from_date = to_date = False
		from_date = result['date_from']
		to_date = result['date_to']
		partner_ids = result['partner_ids']
		args_list = (tuple([self.account_type]),)
		if from_date and to_date:
			cust_query += ' BETWEEN %s AND %s)'
			date_query += ' BETWEEN %s AND %s)'
			args_list += (from_date, to_date)
		elif from_date:
			cust_query += ' >= %s)'
			date_query += ' >= %s)'
			args_list += (from_date,)
		elif to_date:
			cust_query += ' <= %s)'
			date_query += ' <= %s)'
			args_list += (to_date,)
		else:
			raise UserError(_('Select a date'))
		if partner_ids:
			cust_query += ' AND mvl.partner_id in %s'
			args_list += (tuple(partner_ids),)
		query = '''SELECT
CASE WHEN mvl.debit > 0 THEN 'DEBIT'
WHEN mvl.credit > 0 THEN 'CREDIT'
ELSE 'UNKNOWN' END ,
mvl.id,mvl.move_id,mvl.debit,mvl.credit,
mvl.partner_id,mvl.date 
FROM account_move_line mvl
WHERE mvl.account_id in (select id from account_account where internal_type IN %s)
and ''' + cust_query + ''' ORDER BY mvl.date ASC'''

		cr.execute(query, args_list)
		query_rslt = cr.fetchall()
		partnerwise = {}
		debit_line_ids = []
		credit_line_ids = []
		pending_debit_lines = []
		pending_credit_lines = []
		debit_line_value = {}
		credit_line_value = {}
		for line in query_rslt:
			type = line[0]
			line_id = line[1]
			move_id = line[2]
			debit = line[3]
			credit = line[4]
			partner_id = line[5]
			date = line[6]
			if type == 'DEBIT':
				debit_line_ids.append(line_id)
				debit_line_value[line_id] = debit
			elif type == 'CREDIT':
				credit_line_ids.append(line_id)
				credit_line_value[line_id] = credit
		
		pro_debit = []
		pro_credit = []
		if debit_line_ids:
			args_list = (tuple(debit_line_ids),)
			date_query = 'and cr_date'
			if from_date and to_date:
				date_query += ' BETWEEN %s AND %s'
				args_list += (from_date, to_date)
			elif from_date:
				date_query += ' >= %s'
				args_list += (from_date,)
			else:
				date_query += ' <= %s'
				args_list += (to_date,)

			reco_debit_query = '''SELECT 
rec.debit_move_id,sum(rec.amount) 
FROM orchid_account_partial_reconcile_view rec
WHERE  debit_move_id IN %s '''+ date_query+'''
GROUP BY rec.debit_move_id
'''

			cr.execute(reco_debit_query, args_list)
			reco_query_rslt = cr.fetchall()
			
			for line in reco_query_rslt:
				dic = {}
				dic['paid_amount'] = line[1]
				dic['debit_move_id'] = line[0]
				pro_debit.append(dic)
		if credit_line_ids:
			args_list = (tuple(credit_line_ids),)
			date_query = 'and cr_date'
			if from_date and to_date:
				date_query += ' BETWEEN %s AND %s'
				args_list += (from_date, to_date)
			elif from_date:
				date_query += ' >= %s'
				args_list += (from_date,)
			else:
				date_query += ' <= %s'
				args_list += (to_date,)

			reco_credit_query = '''SELECT 
rec.credit_move_id,sum(rec.amount)
FROM orchid_account_partial_reconcile_view rec
WHERE  credit_move_id IN %s '''+ date_query+''' 
GROUP BY rec.credit_move_id'''
			cr.execute(reco_credit_query, args_list)
			reco_query_rslt = cr.fetchall()
			
			for line in reco_query_rslt:
				dic = {}
				dic['paid_amount'] = line[1]
				dic['credit_move_id'] = line[0]
				pro_credit.append(dic)

		ids = [dic['debit_move_id'] for dic in pro_debit]
		pending_debit_lines = [id for id in debit_line_ids if id not in ids]
		ids = [dic['credit_move_id'] for dic in pro_credit]
		pending_credit_lines = [id for id in credit_line_ids if id not in ids]
		
		for line in self.env['account.move.line'].browse(pending_debit_lines):
			dic = {}
			dic['paid_amount'] = 0
			dic['debit_move_id'] = line.id
			pro_debit.append(dic)
		for line in self.env['account.move.line'].browse(pending_credit_lines):
			dic = {}
			dic['paid_amount'] = 0
			dic['credit_move_id'] = line.id
			pro_credit.append(dic)
		return pro_debit,pro_credit

	
	def generate_statement(self):
		debit_reco_lines, credit_reco_lines = self.get_partial_reconsile_data()
		debit_ids = [line['debit_move_id'] for line in debit_reco_lines]
		credit_ids = [line['credit_move_id'] for line in credit_reco_lines]

		data = {}
		new_debit_lines = []
		new_credit_lines = []
		# for line in debit_reco_lines:

		data['debit'] = debit_reco_lines
		data['credit'] = credit_reco_lines
		data['filter'] = self.read(['date_from', 'date_to', 'account_ids', 'partner_ids','mode','account_type','salesman_id','od_group_id','od_sub_group_id','od_area_id','currency_id'])[0]
		
		if data['filter']['date_from']:
			date_frm = datetime.strptime(data['filter']['date_from'], '%Y-%m-%d')
			data['filter']['date_from'] = datetime.strftime(date_frm, "%d/%m/%Y")
		if data['filter']['date_to']:
			date_to = datetime.strptime(data['filter']['date_to'], '%Y-%m-%d')
			data['filter']['date_to'] = datetime.strftime(date_to, "%d/%m/%Y")
		return self.env['report'].with_context(landscape=True).get_action(self, 'orchid_account_enhancement.report_od_partner_statement', data=data)
		return {
			  'view_type': 'form',
			  "view_mode": 'form',
			  'res_model': 'od.overdue.wizard',
			  'res_id': self.id,
			  'type': 'ir.actions.act_window',
			  'target': 'new'
			  }

	
	def generate_statement_xls(self):
		data = {}

		debit_reco_lines, credit_reco_lines = self.get_partial_reconsile_data()
		debit_ids = [line['debit_move_id'] for line in debit_reco_lines]
		credit_ids = [line['credit_move_id'] for line in credit_reco_lines]

		
		data['debit'] = debit_reco_lines
		data['credit'] = credit_reco_lines
		data['filter'] = self.read(['date_from', 'date_to', 'account_ids', 'partner_ids','mode','account_type','salesman_id','od_group_id','od_sub_group_id','od_area_id','currency_id'])[0]
		
		if data['filter']['currency_id']:
			currency_name = data['filter']['currency_id'][1]

		if data['filter']['date_to']:
			to_date = datetime.strptime(self.date_to,'%Y-%m-%d')
			to_Date = to_date.strftime('%d/%m/%Y')

		overdue_line = self.env['report.orchid_account_enhancement.report_od_partner_statement'].generate_overdue(data) 
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

		filename= 'PartnerStatement.xls'
	   
		workbook= xlwt.Workbook(encoding="UTF-8")
		sheet= workbook.add_sheet('Partner Statement',cell_overwrite_ok=True)
		style = xlwt.easyxf('font:height 300, bold True, name Arial; align: horiz center, vert center')
		style_filter = xlwt.easyxf('font:name Arial; align: horiz center, vert center;')
		style_normal_left = xlwt.easyxf('font:name Arial; align: horiz left, vert center;')
		style_normal_right = xlwt.easyxf('font:name Arial; align: horiz right, vert center;')
		# row = 0
		# col =0

		row = 0
		col = 0
		row_merge = row + 2
		col_merge = col + 8

		# row_merge1 = 0
		# col_merge1 = col + 5

		style2 = xlwt.easyxf('font: bold 1')


		sheet.write_merge(row,row_merge,col,col_merge,'CUSTOMER ACCOUNT STATMENT',style)
		row = row + 4

		if currency_obj:
			sheet.write(row,col,'CURRENCY',style2)
			sheet.write(row,col+1,currency_name,style2)
			row = row + 1
		

		if data['filter']['date_to'] != False:
			sheet.write(row,col,'AS ON',style2)
			sheet.write(row,col+1,to_Date,style2)
			row = row + 1   

		
		if data['filter']['account_type'] == 'receivable':  
			for partner  in overdue_line:
				row = row + 1
				sheet.write(row,col,'NAME',style2)
				sheet.write(row,col+1,partner['name'],style2)
				row = row + 1
				sheet.write(row,col,'SAlESPERSON',style2)
				sheet.write(row,col+1,partner['sales_person'],style2)
				row = row + 1
				sheet.write(row,col+1,'INV DATE',style2)           
				sheet.write(row,col+2,'DOC TYPE',style2)
				sheet.write(row,col+3,'SALESPERSON',style2)
				sheet.write(row,col+4,'INV NO. ',style2)
				sheet.write(row,col+5,'LPO NUMBER',style2)
				sheet.write(row,col+6,'INV AMOUNT ',style2)
				sheet.write(row,col+7,'PAID AMOUNT ',style2)
				sheet.write(row,col+8,'BALANCE ',style2)
				sheet.write(row,col+9,'PDC AMOUNT ',style2)
				inv_total = 0
				paid_total = 0
				pdc_total = 0
				balance = 0
				for line in partner['info']:
					

					row = row + 1
					sheet.write(row,col+1,line['date'],style_normal_left)
					sheet.write(row,col+2,line['doc_type'],style_normal_left)
					sheet.write(row,col+3,line['sales_person'],style_normal_left)
					sheet.write(row,col+4,line['inv_name'],style_normal_left)
					sheet.write(row,col+5,line['lpo_no'],style_normal_left)
					sheet.write(row,col+6,line['inv_amount'],style_normal_left)
					sheet.write(row,col+7,line['paid_amount'],style_normal_left)
					balance += line['inv_amount'] - line['paid_amount']
					sheet.write(row,col+8,round(balance,2),style_normal_right)
					inv_total += line['inv_amount']
					paid_total += line['paid_amount']
				row = row + 1
				sheet.write(row,col,'TOTAL ',style2)
				sheet.write(row,col+6,inv_total,style2)
				sheet.write(row,col+7,paid_total,style2)
				sheet.write(row,col+8,balance,style2)
				row = row + 1
		else:
			for partner  in overdue_line:
				row = row + 1
				sheet.write(row,col,'NAME',style2)
				sheet.write(row,col+1,partner['name'],style2)
				row = row + 1
				sheet.write(row,col,'SAlESPERSON',style2)
				sheet.write(row,col+1,partner['sales_person'],style2)
				row = row + 1
				sheet.write(row,col+1,'INV DATE',style2)           
				sheet.write(row,col+2,'DOC TYPE',style2)
				sheet.write(row,col+3,'SALESPERSON',style2)
				sheet.write(row,col+4,'INV NO. ',style2)
				sheet.write(row,col+5,'LPO NUMBER',style2)
				sheet.write(row,col+6,'INV AMOUNT ',style2)
				sheet.write(row,col+7,'PAID AMOUNT ',style2)
				sheet.write(row,col+8,'BALANCE ',style2)
				sheet.write(row,col+9,'PDC AMOUNT ',style2)
				inv_total = 0
				paid_total = 0
				pdc_total = 0
				balance = 0
				for line in partner['info']:
					

					row = row + 1
					sheet.write(row,col+1,line['date'],style_normal_left)
					sheet.write(row,col+2,line['doc_type'],style_normal_left)
					sheet.write(row,col+3,line['sales_person'],style_normal_left)
					sheet.write(row,col+4,line['inv_name'],style_normal_left)
					sheet.write(row,col+5,line['lpo_no'],style_normal_left)
					sheet.write(row,col+6,line['paid_amount'],style_normal_left)
					sheet.write(row,col+7,line['inv_amount'],style_normal_left)
					balance += line['paid_amount'] - line['inv_amount']
					sheet.write(row,col+8,round(balance,2),style_normal_right)
					inv_total += line['inv_amount']
					paid_total += line['paid_amount']
				row = row + 1
				sheet.write(row,col,'TOTAL ',style2)
				sheet.write(row,col+6,inv_total,style2)
				sheet.write(row,col+7,paid_total,style2)
				sheet.write(row,col+8,balance,style2)
				row = row + 1

			

		fp = StringIO()
		workbook.save(fp)
		excel_file = base64.encodestring(fp.getvalue())
		self.excel_file = excel_file
		self.file_name =filename
		fp.close()
		return {
			  'view_type': 'form',
			  "view_mode": 'form',
			  'res_model': 'od.overdue.wizard',
			  'res_id': self.id,
			  'type': 'ir.actions.act_window',
			  'target': 'new'
			  }

	
	
	def generate_statement_sum_xls(self):
		data = {}

		debit_reco_lines, credit_reco_lines = self.get_partial_reconsile_data()
		debit_ids = [line['debit_move_id'] for line in debit_reco_lines]
		credit_ids = [line['credit_move_id'] for line in credit_reco_lines]

		
		data['debit'] = debit_reco_lines
		data['credit'] = credit_reco_lines
		data['filter'] = self.read(['date_from', 'date_to', 'account_ids', 'partner_ids','mode','account_type','salesman_id','od_group_id','od_sub_group_id','od_area_id','currency_id'])[0]
		
		if data['filter']['currency_id']:
			currency_name = data['filter']['currency_id'][1]

		if data['filter']['date_to']:
			to_date = datetime.strptime(self.date_to,'%Y-%m-%d')
			to_Date = to_date.strftime('%d/%m/%Y')

		overdue_line = self.env['report.orchid_account_enhancement.report_od_partner_statement'].generate_overdue(data)
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

		filename= 'PartnerStatementSummary.xls'
	   
		workbook= xlwt.Workbook(encoding="UTF-8")
		sheet= workbook.add_sheet('Partner Statement',cell_overwrite_ok=True)
		style = xlwt.easyxf('font:height 300, bold True, name Arial; align: horiz center, vert center')
		style_filter = xlwt.easyxf('font:name Arial; align: horiz center, vert center;')
		style_normal_left = xlwt.easyxf('font:name Arial; align: horiz left, vert center;')
		style_normal_right = xlwt.easyxf('font:name Arial; align: horiz right, vert center;')
		# row = 0
		# col =0

		row = 0
		col = 0
		row_merge = row + 2
		col_merge = col + 8

		# row_merge1 = 0
		# col_merge1 = col + 5

		style2 = xlwt.easyxf('font: bold 1')


		sheet.write_merge(row,row_merge,col,col_merge,'CUSTOMER ACCOUNT STATMENT',style)
		row = row + 4

		if currency_obj:
			sheet.write(row,col,'CURRENCY',style2)
			sheet.write(row,col+1,currency_name,style2)
			row = row + 1
		

		if data['filter']['date_to'] != False:
			sheet.write(row,col,'AS ON',style2)
			sheet.write(row,col+1,to_Date,style2)
			row = row + 1   

		
		sheet.write(row,col,'NAME',style2)
		sheet.write(row,col+1,'SAlESPERSON',style2)
		sheet.write(row,col+2,'BALANCE',style2) 
		for partner  in overdue_line:
			# row = row + 1
			
			# row = row + 1
			sheet.write(row,col,partner['name'],style2)
			sheet.write(row,col+1,partner['sales_person'],style2)
			# row = row + 1
			# sheet.write(row,col+1,'INV DATE',style2)           
			# sheet.write(row,col+2,'DOC TYPE',style2)
			# sheet.write(row,col+3,'SALESPERSON',style2)
			# sheet.write(row,col+4,'INV NO. ',style2)
			# sheet.write(row,col+5,'LPO NUMBER',style2)
			# sheet.write(row,col+6,'INV AMOUNT ',style2)
			# sheet.write(row,col+7,'PAID AMOUNT ',style2)
			# sheet.write(row,col+8,'BALANCE ',style2)
			# sheet.write(row,col+9,'PDC AMOUNT ',style2)
			# inv_total = 0
			# paid_total = 0
			# pdc_total = 0
			balance = 0
			for line in partner['info']:
				

				# row = row + 1
				# sheet.write(row,col+1,line['date'],style_normal_left)
				# sheet.write(row,col+2,line['doc_type'],style_normal_left)
				# sheet.write(row,col+3,line['sales_person'],style_normal_left)
				# sheet.write(row,col+4,line['inv_name'],style_normal_left)
				# sheet.write(row,col+5,line['lpo_no'],style_normal_left)
				# sheet.write(row,col+6,line['inv_amount'],style_normal_left)
				# sheet.write(row,col+7,line['paid_amount'],style_normal_left)
				balance += line['inv_amount'] - line['paid_amount']
				# sheet.write(row,col+8,round(balance,2),style_normal_right)
				# inv_total += line['inv_amount']
				# paid_total += line['paid_amount']
			# row = row + 1
			# sheet.write(row,col,'TOTAL ',style2)
			# sheet.write(row,col+6,inv_total,style2)
			# sheet.write(row,col+7,paid_total,style2)
			sheet.write(row,col+2,balance,style2)
			row = row + 1        
			

		fp = StringIO()
		workbook.save(fp)
		excel_file = base64.encodestring(fp.getvalue())
		self.excel_file = excel_file
		self.file_name =filename
		fp.close()
		return {
			  'view_type': 'form',
			  "view_mode": 'form',
			  'res_model': 'od.overdue.wizard',
			  'res_id': self.id,
			  'type': 'ir.actions.act_window',
			  'target': 'new'
			  }     