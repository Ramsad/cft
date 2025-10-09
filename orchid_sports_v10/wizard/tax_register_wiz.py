from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, AccessError

import time
from datetime import date
from datetime import datetime,date
from datetime import timedelta

import base64
import xlwt
from io import StringIO
from pprint import pprint
import logging
from odoo import tools
_logger = logging.getLogger(__name__)
from collections import defaultdict


class OrchidTaxRegister(models.TransientModel):
	"""
	Orchid Tax Register.
	"""
	_inherit = 'orchid.tax.register'
	_description = 'Tax Register'

	from_date = fields.Date(string='From Date')
	to_date = fields.Date(string='To Date')
	excel_file = fields.Binary(string='Excel Report',readonly=True)
	file_name = fields.Char(string='Excel File',readonly=True)
	journal_id = fields.Many2many('account.journal',string='Journals')
	account_id = fields.Many2many('account.account',string='Accounts')

	# def generate(self):
	# 	if self.from_date > self.to_date:
	# 		raise UserError(_('From date cannot be greater than To date!!'))
	# 	inv_obj = self.env['account.move']
	# 	move_obj = self.env['account.move.line']
	# 	journal_ids = [journal.id for journal in self.journal_id]
	# 	account_ids = [account.id for account in self.account_id]
	# 	if len(account_ids) == 0:
	# 		raise UserError(_('Requires minimum one account!!'))
	# 	domain = []
	# 	domain.append(('account_id','in',account_ids))
	# 	domain.append(('move_id.state','=','posted'))
	# 	domain.append(('date','<=',self.to_date))
	# 	domain.append(('date','>=',self.from_date))
	# 	if len(journal_ids) > 0:
	# 		domain.append(('journal_id','in',journal_ids))
	# 	move_datas  = move_obj.search(domain)
	# 	ls = []
	# 	for move_data in move_datas:
	# 		data = {}
	# 		temp=0
	# 		d = defaultdict(list)
    #
	# 		data['move_data'] = move_data
	# 		data['partner'] = move_data.partner_id and move_data.partner_id.name or ""
	# 		data['partner_trn'] = move_data.partner_id.vat or ""
	# 		data['inv_date'] = move_data.date or ''
	# 		data['inv_num'] = move_data.invoice_id.number or move_data.move_id.name
	# 		data['tax_amount'] = move_data.debit or -move_data.credit or False
	# 		data['price_subtotal'] = 0
	# 		data['od_net_amount'] = 0
	# 		d['taxes'] = []
	# 		if move_data.invoice_id:
	# 			if data['tax_amount'] < 0:
	# 				data['price_subtotal'] = move_data.invoice_id and -move_data.invoice_id.amount_untaxed or False
	# 				data['od_net_amount'] = move_data.invoice_id and -move_data.invoice_id.amount_total or False
	# 			else:
	# 				data['price_subtotal'] = move_data.invoice_id and move_data.invoice_id.amount_untaxed or False
	# 				data['od_net_amount'] = move_data.invoice_id and move_data.invoice_id.amount_total or False
	# 		vendor_data = self.env['account.move'].search([('move_id','=',move_data.move_id.id)])
	# 		data['vendor_reference']=vendor_data.reference or ''
	# 		data['supplier_invoice_date']=''
	# 		if vendor_data.od_vendor_inv_date:
	# 			data['supplier_invoice_date']=datetime.strptime(vendor_data.od_vendor_inv_date , '%Y-%m-%d').strftime('%d/%m/%Y')
	#
	# 		col_res = self.env['od.sports.receipt'].search([('name','=',move_data.move_id.ref)])
	# 		refund_res = self.env['od.refund.entry'].search([('name','=',move_data.move_id.ref)])
    #
	# 		if len(col_res) > 0:
    #
	# 			col_res = col_res[0]
	# 			price_subtotal = 0
	# 			od_net_amount = 0
    #
	# 			col_line_res = self.env['od.sports.receipt.line'].search([('receipt_id','=',col_res.id),('partner_id','=',move_data.partner_id and move_data.partner_id.id)])
    #
	# 			for lin in col_line_res:
	# 				if lin.od_vat_amount == abs(data['tax_amount']) and lin.od_invoice_no in move_data.name:
	# 					price_subtotal += lin.total
	# 					od_net_amount += lin.grand_total
	# 					data['inv_num'] = lin.od_invoice_no
	# 			d['taxes'].append((col_res.receipt_line and col_res.receipt_line[0].od_vat_id and col_res.receipt_line[0].od_vat_id.name) or " ")
	# 			if data['tax_amount'] < 0:
	# 				data['price_subtotal'] = -price_subtotal
	# 				data['od_net_amount'] = -od_net_amount
	# 			else:
	# 				data['price_subtotal'] = price_subtotal
	# 				data['od_net_amount'] = od_net_amount
	# 		if len(refund_res) > 0:
	# 			refund_res = refund_res[0]
	# 			price_subtotal = refund_res.subtotal
	# 			od_net_amount = refund_res.total_amount
	# 			tax = refund_res.refund_line and refund_res.refund_line[0].od_vat_id.name
	# 			d['taxes'].append(tax)
	# 			data['price_subtotal'] = price_subtotal
	# 			data['od_net_amount'] = od_net_amount
    #
	# 		data['state_id']= move_data.partner_id.state_id.name or ""
	# 		data['fcy']=move_data.currency_id.name or 0
	# 		data['inv_date']=datetime.strptime(data['inv_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
    #
	# 		if move_data.invoice_id:
	# 			for line in move_data.invoice_id.invoice_line_ids[0]:
	# 				for l in line.invoice_line_tax_ids:
	# 					d['taxes'].append(l.name)
	# 		if d['taxes']:
	# 			data['taxes'] = d['taxes']
	# 		else:
	# 			data['taxes'] = [move_data.account_id.name]
	# 		ls.append(data)
    #
	# 	ls=sorted(ls, key=lambda k: ((k['inv_num'])))
	# 	return self.generate_excel_sum(ls)
    #
	# def generate_excel_sum(self, move_datas):
    #
	# 	company = self.env['res.company'].browse(self.env.user.company_id.id)
	# 	vat_period = datetime.strptime(self.from_date, '%Y-%m-%d').strftime('%d/%m/%Y')+"-"+datetime.strptime(self.to_date,'%Y-%m-%d').strftime('%d/%m/%Y')
	#
	# 	head=defaultdict(list)
	# 	head['add'].append(company.street or "")
	# 	head['add'].append(company.street2 or "")
	# 	head['add'].append(company.state_id.name or "")
	# 	head['add'].append(company.zip or "")
	# 	head['add'].append(company.country_id.name or "")
	# 	head['vat'].append(company.vat or "")
    #
	# 	workbook = xlwt.Workbook(encoding="UTF-8")
	# 	xlwt.add_palette_colour("custom_colour", 0x10)
	# 	workbook.set_colour_RGB(0x10,197,11,11)
	# 	filename='VatRegisterSummary.xls'
	# 	sheet= workbook.add_sheet('Sales Report',cell_overwrite_ok=True)
	# 	style = xlwt.easyxf('font:name Arial,height 200,colour white;align: horiz center, vert center;pattern: fore_colour custom_colour,pattern solid;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;')
	# 	style2 = xlwt.easyxf('font:name Arial,height 200,colour white;align: horiz left, vert center;pattern: fore_colour custom_colour, pattern solid;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;')
	# 	style3=xlwt.easyxf('align: horiz center, vert center;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;')
	# 	style4=xlwt.easyxf('align: horiz left, vert center;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;')
	# 	style5=xlwt.easyxf('align: horiz right, vert center;borders:top_color black, bottom_color black, right_color black, left_color black, top thin,right thin,bottom thin,left thin;')
    #
	# 	title=['Name of the Company','Name of the Company','Address of the Company','TRN of the Company','VAT Return Period']
	# 	row = 2
	# 	col =0
	# 	sheet.write(row,col,title[0],style2)
	# 	if company.od_name_arabic==True:
	# 		row=row+1
	# 		sheet.write(row,col,title[1],style2)
	# 	row = row+1
	# 	sheet.write(row,col,title[2],style2)
	# 	row=row+1
	# 	sheet.write(row,col,title[3],style2)
	# 	row=row+1
	# 	sheet.write(row,col,title[4],style2)
	#
	# 	row=2
	# 	col=1
	# 	sheet.write(row,col,company.name,style4)
	# 	if company.od_name_arabic==True:
	# 		row=row+1
	# 		sheet.write(row,col,company.od_name_arabic,style4)
	# 	row=row+1
	# 	sheet.write(row,col,head['add'],style4)
	# 	row=row+1
	# 	sheet.write(row,col,head['vat'],style4)
	# 	row=row+1
	# 	sheet.write(row,col,vat_period,style4)
    #
	# 	header=['Sr.No','Party Name','TRN','Invoice\nDate','Date of\nSupply','Invoice\nNumber','Vendor Reference','Supplier Invoice Date'
	# 			,'Invoice Value\nexcluding VAT AED','Value of VAT\nAED','Total\nincluding VAT AED',
	# 			'VAT Type','Emirates']
    #
	# 	foreign_header=['FYC\ncode','Value of supply excluding VAT\nin Foreign currency','Value of VAT\nin Foreign currency']# not__included=['Total Value of\nsupplies in AED','Total Value of VAT\nin AED']
	#
	# 	col=0
	# 	row=row+5
	# 	for i in range (0,13):
	# 		sheet.write(row,col,header[i],style)
	# 		col=col+1
	# 	flag=0
	# 	for data in move_datas:
    #
	# 		if data['move_data'].invoice_id:
	# 			for line in data['move_data'].invoice_id.invoice_line_ids:
	# 				if data['move_data'].currency_id.name != 'AED' and data['move_data'].currency_id.name != 0:
	# 					flag=1;
	# 	if flag==1:
	# 		for i in range(0,3):
	# 			sheet.write(row,col,foreign_header[i],style)
	# 			col=col+1
    #
	# 	s=0
	# 	inv_total = 0
	# 	tax_total = 0
	# 	grand_total = 0
    #
	# 	for move_data in move_datas:
	# 		# print move_data,'---------------------'
	# 		s=s+1
	# 		row=row+1
	# 		col=0
	# 		sheet.write(row,col,s,style3)
	# 		col=col+1
	# 		sheet.write(row,col,move_data['partner'],style3)
	# 		col=col+1
	# 		sheet.write(row,col,move_data['partner_trn'],style3)
	# 		col=col+1
	# 		sheet.write(row,col,move_data['inv_date'],style3)
	# 		col=col+1
	# 		sheet.write(row,col,move_data['inv_date'],style3)
	# 		col=col+1
	# 		sheet.write(row,col,move_data['inv_num'],style3)
	# 		col=col+1
	# 		sheet.write(row,col,move_data['vendor_reference'],style3)
	# 		col=col+1
	# 		sheet.write(row,col,move_data['supplier_invoice_date'],style3)
	#
	# 		if move_data['fcy'] == 'AED' or move_data['fcy'] ==0:
	# 			col=col+1
	# 			sheet.write(row,col,round(move_data['price_subtotal'],2),style5)
	# 			col=col+1
	# 			sheet.write(row,col,round(move_data['tax_amount'],2),style5)
	# 			col=col+1
	# 			sheet.write(row,col,round(move_data['od_net_amount'],2),style5)
	# 			temp=col
	# 			inv_total += move_data['price_subtotal']
	# 			tax_total += move_data['tax_amount']
	# 			grand_total += move_data['od_net_amount']
	# 		else:
	# 			price = move_data['move_data'].currency_id.compute(move_data['price_subtotal'], company.currency_id)
	# 			tax = move_data['move_data'].currency_id.compute(move_data['tax_amount'], company.currency_id)
	# 			od_net_amount = move_data['move_data'].currency_id.compute(move_data['od_net_amount'], company.currency_id)
	# 			col=col+1
	# 			sheet.write(row,col,round(price,2),style5)
	# 			col=col+1
	# 			sheet.write(row,col,round(tax,2),style5)
	# 			col=col+1
	# 			sheet.write(row,col,round(od_net_amount,2),style5)
	# 			temp=col
	# 			inv_total += price
	# 			tax_total += tax
	# 			grand_total += move_data['od_net_amount']
    #
	# 		col=col+1
	# 		# if move_data['inv_num'] == 'PUR/2018/0092':
	# 		# 	print move_data['taxes']
	# 		sheet.write(row,col,move_data['taxes'],style4)
	# 		col=col+1
	# 		sheet.write(row,col,move_data['state_id'],style3)
	# 		# col=col+1
	# 		# sheet.write(row,col,"",style3)
	# 		if move_data['fcy'] != 'AED' and move_data['fcy'] != 0:
	# 			col=col+1
	# 			sheet.write(row,col,move_data['fcy'],style3)
	# 			col=col+1
	# 			sheet.write(row,col,round(move_data['price_subtotal'],2),style5)
	# 			col=col+1
	# 			sheet.write(row,col,round(move_data['tax_amount'],2),style5)
	# 	cancel_inv=self.env['account.move'].search([('state','=','cancel'),('date','<=',self.to_date),('date','>=',self.from_date)])
	# 	if cancel_inv:
	# 		for inv in cancel_inv:
    #
	# 			if inv.move_name :
	# 				data={}
	# 				data['partner']=inv.partner_id.name
	# 				data['partner_trn']=inv.partner_id.vat or ""
	# 				date= inv.date_invoice or ""
	# 				data['inv_date']=datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
	# 				data['inv_num']=inv.move_name or ""
	# 				data['vendor_reference']=inv.reference or ''
	# 				data['supplier_invoice_date']=''
	# 				if inv.od_vendor_inv_date:
	# 					data['supplier_invoice_date']=datetime.strptime(inv.od_vendor_inv_date , '%Y-%m-%d').strftime('%d/%m/%Y')
	#
	# 				s=s+1
	# 				row=row+1
	# 				col=0
	# 				sheet.write(row,col,s,style3)
	# 				col=col+1
	# 				sheet.write(row,col,data['partner'],style3)
	# 				col=col+1
	# 				sheet.write(row,col,data['partner_trn'],style3)
	# 				col=col+1
	# 				sheet.write(row,col,data['inv_date'],style3)
	# 				col=col+1
	# 				sheet.write(row,col,data['inv_date'],style3)
	# 				col=col+1
	# 				sheet.write(row,col,data['inv_num'],style3)
	# 				col=col+1
	# 				sheet.write(row,col,data['vendor_reference'],style3)
	# 				col=col+1
	# 				sheet.write(row,col,data['supplier_invoice_date'],style3)
	# 				col=col+1
	# 				sheet.write(row,col,"",style3)
	# 				col=col+1
	# 				sheet.write(row,col,"",style3)
	# 				col=col+1
	# 				sheet.write(row,col,"",style3)
	# 				col=col+1
	# 				sheet.write(row,col,"",style3)
	# 				col=col+1
	# 				sheet.write(row,col,"",style3)
    #
	# 	row = row + 1
	# 	col = 7
	# 	sheet.write(row,col,'TOTAL ',style3)
	# 	col=col+1
	# 	sheet.write(row,col,round(inv_total,2),style5)
	# 	col=col+1
	# 	sheet.write(row,col,round(tax_total,2),style5)
	# 	col=col+1
	# 	sheet.write(row,col,round(grand_total,2),style5)
    #
	# 	fp = StringIO()
	# 	workbook.save(fp)
	# 	excel_file = base64.encodestring(fp.getvalue())
	# 	self.excel_file = excel_file
	# 	self.file_name =filename
	# 	fp.close()
	# 	return {
	# 		  'view_type': 'form',
	# 		  "view_mode": 'form',
	# 		  'res_model': 'orchid.tax.register',
	# 		  'res_id': self.id,
	# 		  'type': 'ir.actions.act_window',
	# 		  'target': 'new'
	# 		  }

