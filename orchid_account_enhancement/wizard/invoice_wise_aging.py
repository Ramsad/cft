# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError
import xlwt
from io import StringIO
import base64


class od_invoice_aging(models.TransientModel):
	_name = 'od.invoice.aging'
	_description = 'Invoice Wise Aging Wizard'
	
	date_from = fields.Date(string='Date')
	account_type = fields.Selection([
		('receivable', 'Recievable'),
		('payable', 'Payable'),
		], string='What do you want?',default='receivable')
	account_ids = fields.Many2many('account.account',string='Accounts')
	partner_ids = fields.Many2many('res.partner',string='Partner')
	period_length = fields.Integer(string='Period Length (days)',default=30)
	excel_file = fields.Binary(string='Dowload Report Excel',readonly=True)
	file_name = fields.Char(string='Excel File',readonly=True)
	report_type = fields.Selection([
		('invoice', 'Invoice Wise'),
		('partner', 'Partner Wise'),
		], string='Aging Type?',default='invoice')
	

	def get_filters(self):
		data = {}
		res = {}
		if self.period_length<=0:
			raise UserError(_('You must set a period length greater than 0.'))
		if not self.date_from:
			raise UserError(_('You must set a start date.'))
		start = datetime.strptime(self.date_from, "%Y-%m-%d")
		
		for i in range(7)[::-1]:
			stop = start - relativedelta(days=self.period_length - 1)
			res[str(i)] = {
				'name': (i!=0 and (str((7-(i+1)) * self.period_length) + '-' + str((7-i) * self.period_length)) or ('+'+str(6 * self.period_length))),
				'stop': start.strftime('%Y-%m-%d'),
				'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
			}
			start = stop - relativedelta(days=1)

		# print 'res>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',res
		data['form'] = {}
		data['form']['period']=res
		data['form']['date_from'] = self.date_from
		data['form']['account_type'] = self.account_type
#<<<<<<<<<<<<<<<<< Filters tobe added >>>>>>>>>>>>>>>>>>>>>> 
		# data['form']['od_period_lenght6']=self.od_period_lenght6
		# data['form']['od_period_lenght5']=self.od_period_lenght5
		# data['form']['od_period_lenght4']=self.od_period_lenght4
		# data['form']['od_period_lenght3']=self.od_period_lenght3
		# data['form']['od_period_lenght2']=self.od_period_lenght2
		# data['form']['od_period_lenght1']=self.od_period_lenght1

		# data['form']['od_is_slab']=self.od_is_slab
		# data['form']['od_is_invoice_date']=self.od_is_invoice_date
		# data['form']['period_length']=self.period_length
		# data['form']['od_account_id']= self.od_account_id and self.od_account_id.id or False
		# data['form']['result_selection']=self.result_selection
		# data['form']['target_move'] = self.target_move
		# journal_ids = []
		# for jou in self.journal_ids:
		#     journal_ids.append(jou.id)
		# data['form']['journal_ids']=journal_ids
#<<<<<<<<<<<<<<<<< Filters tobe added end>>>>>>>>>>>>>>>>>>>>>>         
		partners = []
		partner_ids = self.partner_ids
		for part in partner_ids:
			partners.append(part.id)
		data['form']['partners'] = partners
		# print 'filters-------------------------------------------------------'
		# print data['form']
		return data


	def generate_partnerwise_data(self):
		cr = self._cr
		move_line_obj = self.env['account.move.line']
		partner_obj = self.env['res.partner']
		data = self.get_filters()
		slab_data = {}
		for key, value in data['form']['period'].items():
			from_date = data['form']['period'][key]['start']
			to_date = data['form']['period'][key]['stop']
			date_query = '(COALESCE(mvl.date,mvl.date_maturity)'
			args_list = (tuple([self.account_type]),)
			if from_date and to_date:
				date_query += ' BETWEEN %s AND %s)'
				args_list += (from_date, to_date)
			elif to_date:
				date_query += ' <= %s)'
				args_list += (to_date,)
			elif from_date:
				date_query += ' >= %s)'
				args_list += (from_date,)
			else:
				raise UserError(_('Select a date'))
			if data['form']['partners']:
				date_query += ' AND mvl.partner_id IN %s'
				args_list += (tuple(data['form']['partners']),)
			query = '''SELECT
CASE WHEN mvl.debit > 0 THEN 'DEBIT'
WHEN mvl.credit > 0 THEN 'CREDIT'
ELSE 'UNKNOWN' END ,
mvl.id,mvl.move_id,mvl.debit,mvl.credit,
mvl.partner_id,mvl.date 
FROM account_move_line mvl
WHERE mvl.account_id in (select id from account_account where internal_type IN %s)
and ''' + date_query + ''' ORDER BY mvl.date ASC'''

			cr.execute(query, args_list)
			query_rslt = cr.fetchall()
			debit_line_ids = []
			credit_line_ids = []
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
			temp_d_ids = []
			if debit_line_ids:
				args_list = (tuple(debit_line_ids),)
				date_query = 'and cr_date'
				t_date = data['form']['period']['6']['stop']
				if t_date:
					date_query += ' <= %s'
					args_list += (t_date,)

				reco_debit_query = '''SELECT 
				rec.debit_move_id,sum(rec.amount) 
				FROM orchid_account_partial_reconcile_view rec
				WHERE  debit_move_id IN %s '''+ date_query+'''
				GROUP BY rec.debit_move_id
				'''

				cr.execute(reco_debit_query, args_list)
				reco_query_rslt = cr.fetchall()
				
				for line in reco_query_rslt:
					d_id = line[0]
					m_obj = move_line_obj.browse(d_id)
					p_id = partner_obj.browse(m_obj.partner_id.id)
					temp_d_ids.append(d_id)
					if p_id.id in slab_data:
						actual = m_obj.debit
						if (actual - line[1]) > 0:
							slab_data[p_id.id][key] = actual-line[1]
					else:
						actual = m_obj.debit
						if (actual - line[1]) > 0:
							slab_data[p_id.id] = {}
							slab_data[p_id.id][key] = actual-line[1]
							# slab_data[d_id]['type'] = 'invoice'
			for dr_data in move_line_obj.browse([id for id in debit_line_ids if id not in temp_d_ids]):
				if dr_data.partner_id.id in slab_data:
					if key in slab_data[dr_data.partner_id.id]:
						slab_data[dr_data.partner_id.id][key] += dr_data.debit
					else:
						slab_data[dr_data.partner_id.id][key] = dr_data.debit
					# slab_data[dr_data.partner_id.id]['type'] = 'invoice'
				else:
					slab_data[dr_data.partner_id.id] = {}
					slab_data[dr_data.partner_id.id][key] = dr_data.debit
					# slab_data[dr_data.partner_id.id]['type'] = 'invoice'

			if credit_line_ids:
				reco_credit_query = '''SELECT 
				credit_move_id
				FROM account_partial_reconcile
				WHERE  credit_move_id IN %s'''
				
				args_list = (tuple(credit_line_ids),)
				cr.execute(reco_credit_query, args_list)
				reco_query_rslt = cr.fetchall()
				paymnt_ids = []
				for line in reco_query_rslt:
					paymnt_ids.append(line[0])
				credit_ids = [id for id in credit_line_ids if id not in paymnt_ids]
				for crd in move_line_obj.browse(credit_ids):
					p_id = crd.partner_id.id
					if p_id in slab_data:
						if key in slab_data[p_id]:
							slab_data[p_id][key] -= (crd.credit)
						else:
							slab_data[p_id][key] = -(crd.credit)
					else:
						slab_data[p_id] = {}
						slab_data[p_id][key] = -(crd.credit)
					# slab_data[crd.id]['type'] = 'payment'

		period = data['form']['period']
		return slab_data,period

	def generate_data(self):
		cr = self._cr
		move_line_obj = self.env['account.move.line']
		data = self.get_filters()
		slab_data = {}
		for key, value in data['form']['period'].items():
			from_date = data['form']['period'][key]['start']
			to_date = data['form']['period'][key]['stop']
			date_query = '(COALESCE(mvl.date,mvl.date_maturity)'
			args_list = (tuple([self.account_type]),)
			if from_date and to_date:
				date_query += ' BETWEEN %s AND %s)'
				args_list += (from_date, to_date)
			elif to_date:
				date_query += ' <= %s)'
				args_list += (to_date,)
			elif from_date:
				date_query += ' >= %s)'
				args_list += (from_date,)
			else:
				raise UserError(_('Select a date'))
			if data['form']['partners']:
				date_query += ' AND mvl.partner_id IN %s'
				args_list += (tuple(data['form']['partners']),)
			query = '''SELECT
CASE WHEN mvl.debit > 0 THEN 'DEBIT'
WHEN mvl.credit > 0 THEN 'CREDIT'
ELSE 'UNKNOWN' END ,
mvl.id,mvl.move_id,mvl.debit,mvl.credit,
mvl.partner_id,mvl.date 
FROM account_move_line mvl
WHERE mvl.account_id in (select id from account_account where internal_type IN %s)
and ''' + date_query + ''' ORDER BY mvl.date ASC'''

			cr.execute(query, args_list)
			query_rslt = cr.fetchall()
			debit_line_ids = []
			credit_line_ids = []
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
			temp_d_ids = []
			if debit_line_ids:
				args_list = (tuple(debit_line_ids),)
				date_query = 'and cr_date'
				t_date = data['form']['period']['6']['stop']
				if t_date:
					date_query += ' <= %s'
					args_list += (t_date,)

				reco_debit_query = '''SELECT 
				rec.debit_move_id,sum(rec.amount) 
				FROM orchid_account_partial_reconcile_view rec
				WHERE  debit_move_id IN %s '''+ date_query+'''
				GROUP BY rec.debit_move_id
				'''

				cr.execute(reco_debit_query, args_list)
				reco_query_rslt = cr.fetchall()
				
				for line in reco_query_rslt:
					d_id = line[0]
					temp_d_ids.append(d_id)
					if d_id in slab_data:
						actual = move_line_obj.browse(d_id).debit
						if (actual - line[1]) > 0:
							slab_data[d_id][key] = actual-line[1]
					else:
						actual = move_line_obj.browse(d_id).debit
						if (actual - line[1]) > 0:
							slab_data[d_id] = {}
							slab_data[d_id][key] = actual-line[1]
							slab_data[d_id]['type'] = 'invoice'
			for dr_data in move_line_obj.browse([id for id in debit_line_ids if id not in temp_d_ids]):
				slab_data[dr_data.id] = {}
				slab_data[dr_data.id][key] = dr_data.debit
				slab_data[dr_data.id]['type'] = 'invoice'

			if credit_line_ids:
				reco_credit_query = '''SELECT 
				credit_move_id
				FROM account_partial_reconcile
				WHERE  credit_move_id IN %s'''
				
				args_list = (tuple(credit_line_ids),)
				cr.execute(reco_credit_query, args_list)
				reco_query_rslt = cr.fetchall()
				paymnt_ids = []
				for line in reco_query_rslt:
					paymnt_ids.append(line[0])
				credit_ids = [id for id in credit_line_ids if id not in paymnt_ids]
				for crd in move_line_obj.browse(credit_ids):
					slab_data[crd.id] = {}
					slab_data[crd.id][key] = -(crd.credit)
					slab_data[crd.id]['type'] = 'payment'

		period = data['form']['period']
		return slab_data,period

	def generate_excel(self):
		if self.report_type == 'invoice':
			self.generate_excel_invoicewise()
		elif self.report_type == 'partner':
			self.generate_excel_partnerwise()
		return {
			  'view_type': 'form',
			  "view_mode": 'form',
			  'res_model': 'od.invoice.aging',
			  'res_id': self.id,
			  'type': 'ir.actions.act_window',
			  'target': 'new'
			  }

	def generate_excel_partnerwise(self):
		data, period = self.generate_partnerwise_data()
		print(data)
		filename= 'PartnerWiseAging.xls'
		move_line_obj = self.env['account.move.line']
		partner_obj = self.env['res.partner']
		
		workbook= xlwt.Workbook(encoding="UTF-8")
		sheet= workbook.add_sheet('Partner Statement Summary',cell_overwrite_ok=True)
		style = xlwt.easyxf('font:height 200, bold True, name Arial; align: horiz center, vert center;borders: top medium,right medium,bottom medium,left medium')
		style_filter = xlwt.easyxf('font:name Arial; align: horiz center, vert center;')
		style_normal_left = xlwt.easyxf('font:name Arial; align: horiz left, vert center;')
		style_normal_right = xlwt.easyxf('font:name Arial; align: horiz right, vert center;')
		row = 3
		col =0
		sheet.write(row,col,'PARTNER',style)
		col = col + 1
		sheet.write(row,col,'NAME',style)
		col = col + 1
		for index in range(7)[::-1]:
			sheet.write(row,col,period[str(index)]['name'],style)
			col = col + 1
		sheet.write(row,col,'TOTAL',style)
		row = row + 1
		grand_total = 0
		# print "sssssssssssssssss",data
		for key, value in data.items():
			print(value)
			print('kkkkk',key)
			partner_res = partner_obj.browse(key)
			# name = partner_res.move_id.name
			name = ''
			print(partner_res)
			partner = partner_res.name
			# amount = partner_res.balance
			total = 0
			sheet.write(row,0,partner,style_normal_left)
			sheet.write(row,1,name,style_normal_left)
			# if value['type'] == 'invoice':
				# print value
			if '6' in value:
				sheet.write(row,2,round(value['6'],2),style_normal_right)
				total += round(value['6'],2)
			if '5' in value:
				sheet.write(row,3,round(value['5'],2),style_normal_right)
				total += round(value['5'],2)
			if '4' in value:
				sheet.write(row,4,round(value['4'],2),style_normal_right)
				total += round(value['4'],2)
			if '3' in value:
				sheet.write(row,5,round(value['3'],2),style_normal_right)
				total += round(value['3'],2)
			if '2' in value:
				sheet.write(row,6,round(value['2'],2),style_normal_right)
				total += round(value['2'],2)
			if '1' in value:
				sheet.write(row,7,round(value['1'],2),style_normal_right)
				total += round(value['1'],2)
			if '0' in value:
				sheet.write(row,8,round(value['0'],2),style_normal_right)
				total += round(value['0'],2)
			# elif value['type'] == 'payment':
			#     if '6' in value:
			#         sheet.write(row,2,round(value['6'],2),style_normal_right)
			#         total += round(value['6'],2)
			#     if '5' in value:
			#         sheet.write(row,3,round(value['5'],2),style_normal_right)
			#         total += round(value['5'],2)
			#     if '4' in value:
			#         sheet.write(row,4,round(value['4'],2),style_normal_right)
			#         total += round(value['4'],2)
			#     if '3' in value:
			#         sheet.write(row,5,round(value['3'],2),style_normal_right)
			#         total += round(value['3'],2)
			#     if '2' in value:
			#         sheet.write(row,6,round(value['2'],2),style_normal_right)
			#         total += round(value['2'],2)
			#     if '1' in value:
			#         sheet.write(row,7,round(value['1'],2),style_normal_right)
			#         total += round(value['1'],2)
			#     if '0' in value:
			#         sheet.write(row,8,round(value['0'],2),style_normal_right)
			#         total += round(value['0'],2)
			sheet.write(row,9,total,style_normal_right)
			grand_total += total
			row = row + 1

		fp = StringIO()
		workbook.save(fp)
		excel_file = base64.encodestring(fp.getvalue())
		self.excel_file = excel_file
		self.file_name =filename
		fp.close()
		




	def generate_excel_invoicewise(self):
		data, period = self.generate_data()
		filename= 'InvoiceWiseAging.xls'
		move_line_obj = self.env['account.move.line']
		
		workbook= xlwt.Workbook(encoding="UTF-8")
		sheet= workbook.add_sheet('Partner Statement Summary',cell_overwrite_ok=True)
		style = xlwt.easyxf('font:height 200, bold True, name Arial; align: horiz center, vert center;borders: top medium,right medium,bottom medium,left medium')
		style_filter = xlwt.easyxf('font:name Arial; align: horiz center, vert center;')
		style_normal_left = xlwt.easyxf('font:name Arial; align: horiz left, vert center;')
		style_normal_right = xlwt.easyxf('font:name Arial; align: horiz right, vert center;')
		row = 3
		col =0
		sheet.write(row,col,'PARTNER',style)
		col = col + 1
		sheet.write(row,col,'NAME',style)
		col = col + 1
		for index in range(7)[::-1]:
			sheet.write(row,col,period[str(index)]['name'],style)
			col = col + 1
		sheet.write(row,col,'TOTAL',style)
		row = row + 1
		grand_total = 0
		# print "sssssssssssssssss",data
		for key, value in data.items():
			move_line_res = move_line_obj.browse(key)
			name = move_line_res.move_id.name
			partner = move_line_res.partner_id.name
			amount = move_line_res.balance
			total = 0
			sheet.write(row,0,partner,style_normal_left)
			sheet.write(row,1,name,style_normal_left)
			if value['type'] == 'invoice':
				# print value
				if '6' in value:
					sheet.write(row,2,round(value['6'],2),style_normal_right)
					total += round(value['6'],2)
				if '5' in value:
					sheet.write(row,3,round(value['5'],2),style_normal_right)
					total += round(value['5'],2)
				if '4' in value:
					sheet.write(row,4,round(value['4'],2),style_normal_right)
					total += round(value['4'],2)
				if '3' in value:
					sheet.write(row,5,round(value['3'],2),style_normal_right)
					total += round(value['3'],2)
				if '2' in value:
					sheet.write(row,6,round(value['2'],2),style_normal_right)
					total += round(value['2'],2)
				if '1' in value:
					sheet.write(row,7,round(value['1'],2),style_normal_right)
					total += round(value['1'],2)
				if '0' in value:
					sheet.write(row,8,round(value['0'],2),style_normal_right)
					total += round(value['0'],2)
			elif value['type'] == 'payment':
				if '6' in value:
					sheet.write(row,2,round(value['6'],2),style_normal_right)
					total += round(value['6'],2)
				if '5' in value:
					sheet.write(row,3,round(value['5'],2),style_normal_right)
					total += round(value['5'],2)
				if '4' in value:
					sheet.write(row,4,round(value['4'],2),style_normal_right)
					total += round(value['4'],2)
				if '3' in value:
					sheet.write(row,5,round(value['3'],2),style_normal_right)
					total += round(value['3'],2)
				if '2' in value:
					sheet.write(row,6,round(value['2'],2),style_normal_right)
					total += round(value['2'],2)
				if '1' in value:
					sheet.write(row,7,round(value['1'],2),style_normal_right)
					total += round(value['1'],2)
				if '0' in value:
					sheet.write(row,8,round(value['0'],2),style_normal_right)
					total += round(value['0'],2)
			sheet.write(row,9,total,style_normal_right)
			grand_total += total
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
			  'res_model': 'od.invoice.aging',
			  'res_id': self.id,
			  'type': 'ir.actions.act_window',
			  'target': 'new'
			  }
		
	          
	def generate_pdf(self,data):
		move_line_obj = self.env['account.move.line']
		data, period = self.generate_data()
		invoice_data = {}
		invoice_data['periods'] = period
		invoice_data['values'] = []
		for key, value in data.items():
			datas = {}
			move_line_res = move_line_obj.browse(key)
			name = move_line_res.move_id.name
			partner = move_line_res.partner_id.name
			datas['partner'] = partner
			datas['name'] = name
			total = 0
			datas['6'] = 0 
			datas['5'] = 0 
			datas['4'] = 0 
			datas['3'] = 0 
			datas['2'] = 0 
			datas['1'] = 0 
			datas['0'] = 0 
			if value['type'] == 'invoice':
				if '6' in value:
					datas['6'] = value['6']
					total+=value['6']
				if '5' in value:
					datas['5'] = value['5']
					total+=value['5']
				if '4' in value:
					datas['4'] = value['4']
					total+=value['4']
				if '3' in value:
					datas['3'] = value['3']
					total+=value['3'] 
				if '2' in value:
					datas['2'] = value['2'] 
					total+=value['2']
				if '1' in value:
					datas['1'] = value['1']
					total+=value['1'] 
				if '0' in value:
					datas['0'] = value['0']
					total+=value['0']
			elif value['type'] == 'payment':
				if '6' in value:
					datas['6'] = value['6']
					total+=value['6']
				if '5' in value:
					datas['5'] = value['5']
					total+=value['5']
				if '4' in value:
					datas['4'] = value['4']
					total+=value['4']
				if '3' in value:
					datas['3'] = value['3']
					total+=value['3'] 
				if '2' in value:
					datas['2'] = value['2'] 
					total+=value['2']
				if '1' in value:
					datas['1'] = value['1']
					total+=value['1'] 
				if '0' in value:
					datas['0'] = value['0']
					total+=value['0']
			datas['total']=total                                                        
			invoice_data['values'].append(datas)
		return self.env['report'].with_context(landscape=True).get_action(self,'orchid_account_enhancement.report_od_invoice_aging',data=invoice_data)
		