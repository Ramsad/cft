# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import xlwt
from io import StringIO
import base64

class AccountReportGeneralLedger(models.TransientModel):
	_inherit = "account.report.general.ledger"

	od_partner_ids = fields.Many2many('res.partner',string='Partners')
	od_account_ids = fields.Many2many('account.account',string='Accounts')
	od_analytic_ids = fields.Many2many('account.analytic.account',string='Analytic Accounts')
	od_cost_center_ids = fields.Many2many('orchid.account.cost.center',string='Costcenter')
	od_journal_ids = fields.Many2many('account.journal',string='Journal')
	od_product_ids = fields.Many2many('product.template',string='Products')
	move_line_ids = fields.One2many('wizard.account.move.line','wizard_id',string='Move Line')

	excel_file = fields.Binary(string='Dowload Report Excel',readonly=True)
	file_name = fields.Char(string='Excel File',readonly=True)
	od_template=fields.Selection([('daily', 'Daily Report'),('monthly', 'Monthly Report')],string='Template',store=True)
	
	
	
#    
#    @api.onchange('od_partner_ids','od_account_ids','od_analytic_ids','od_cost_center_ids','od_journal_ids')
#    def onchange_od_partner_ids(self):
#    	partner_ids = []
#    	search_cond = []
#    	move_line_ids = []
#    	cost_ids = []
#    	analytic_ids = []
#    	account_ids = []
#    	od_journal_ids = []
#    	if self.od_journal_ids:
#    		for jou in self.od_journal_ids:
#    			od_journal_ids.append(jou.id)
#    		search_cond.append(('journal_id','in',od_journal_ids))
#    	if self.od_partner_ids:
#    		for part in self.od_partner_ids:
#    			partner_ids.append(part.id)
#    		search_cond.append(('partner_id','in',partner_ids))
#    	if self.od_account_ids:
#    		for acc in self.od_account_ids:
#    			account_ids.append(acc.id)
#    		search_cond.append(('account_id','in',account_ids))
#    	if self.od_analytic_ids:
#    		for ana in self.od_analytic_ids:
#    			analytic_ids.append(ana.id)
#    		search_cond.append(('analytic_account_id','in',analytic_ids))    			
#    	if self.od_cost_center_ids:
#    		for cost in self.od_cost_center_ids:
#    			cost_ids.append(cost.id)
#    		search_cond.append(('orchid_cc_id','in',cost_ids))
#    	move_obj = []
#    	if search_cond:
#    		move_obj = self.env['account.move.line'].search(search_cond)
#    	if move_obj:
#    		for mvlineids in move_obj:
#    			move_line_ids.append((0,0,{'move_line_id':mvlineids.id}))
#    			
#    		
#    	print "22222222222222222222222222222222222",move_line_ids		
#        values = {
#            'move_line_ids':move_line_ids,
#        }
#        self.update(values)
		
	
	def get_move_line_ids(self):        
		partner_ids = []
		search_cond = []
		move_line_ids = []
		cost_ids = []
		analytic_ids = []
		account_ids = []
		od_journal_ids = []
		product_ids = []
		if self.od_journal_ids:
			for jou in self.od_journal_ids:
				od_journal_ids.append(jou.id)
			search_cond.append(('journal_id','in',od_journal_ids))
		if self.od_partner_ids:
			for part in self.od_partner_ids:
				partner_ids.append(part.id)
			search_cond.append(('partner_id','in',partner_ids))
		if self.od_account_ids:
			for acc in self.od_account_ids:
				account_ids.append(acc.id)
			search_cond.append(('account_id','in',account_ids))
		if self.od_analytic_ids:
			for ana in self.od_analytic_ids:
				analytic_ids.append(ana.id)
			search_cond.append(('analytic_account_id','in',analytic_ids))    			
		if self.od_cost_center_ids:
			for cost in self.od_cost_center_ids:
				cost_ids.append(cost.id)
			search_cond.append(('orchid_cc_id','in',cost_ids))
		if self.od_product_ids:
			for pro in self.od_product_ids:
				print('hhhhhhhhhhhhhhhhhhhhhhhhhhh')
				product_ids.append(pro.id)
			search_cond.append(('product_id','in',product_ids))

		move_obj = []
		if search_cond:
			move_obj = self.env['account.move.line'].search(search_cond)
		if move_obj:
			for mvlineids in move_obj:
				move_line_ids.append(mvlineids.id) 
				
		return move_line_ids
			  


	
	def check_report(self):
		result = super(AccountReportGeneralLedger,self).check_report()
		move_line_ids = []
		if self.od_partner_ids or self.od_account_ids or self.od_analytic_ids or self.od_cost_center_ids or self.od_journal_ids:
			move = self.get_move_line_ids()
			if not move:
			
				raise UserError(_("no data for selected search codition"))	

			move_line_ids = move
		result['od_move_lines'] = list(set(move_line_ids))
			
		return result
		
		
	# def get_excel_filters(self,data,sheet,style2,style_filter):
	#     filter_col_index = 0
	#     sheet.write(0,0,'Filter By',style2)
	#     if self.od_group_id:
	#         group_name = self.od_group_id and self.od_group_id.name or 'None'
	#         sheet.write(2,filter_col_index,group_name,style_filter)
	#         sheet.write(1,filter_col_index,'Group',style2)
	#         filter_col_index += 1
	#     if self.od_sub_group_id:
	#         sub_group_name = self.od_sub_group_id and self.od_sub_group_id.name or 'None'
	#         sheet.write(2,filter_col_index,sub_group_name,style_filter)
	#         sheet.write(1,filter_col_index,'Sub Group',style2)
	#         filter_col_index += 1
	#     if self.salesman_id:
	#         salesman_name = self.salesman_id and self.salesman_id.name or 'None'
	#         sheet.write(2,filter_col_index,salesman_name,style_filter)
	#         sheet.write(1,filter_col_index,'Salesman',style2)
	#         filter_col_index += 1
	#     if self.od_area_id:
	#         area_name = self.od_area_id and self.od_area_id.name or 'None'
	#         sheet.write(2,filter_col_index,area_name,style_filter)
	#         sheet.write(1,filter_col_index,'Area',style2)
	#         filter_col_index += 1
	#     sheet.write(1,filter_col_index,'As On Date',style2)
	#     sheet.write(2,filter_col_index,data['form']['date_from'],style_filter)
	#     return sheet

	def get_data_for_xls(self):
		data = {}
		data['form'] = {}      
		data['form'].update(self.read(['display_account','date_to','date_from','target_move','initial_balance', 'sortby'])[0]) 
		print(data['form'])
		od_journ_ids = []
		od_journal_ids = self.od_journal_ids
		od_template=self.od_template
		if od_journal_ids:
			for jou in od_journal_ids:
				od_journ_ids.append(jou.id) 


		if not od_journ_ids:
			journal_ob=self.env['account.journal'].search([])
			print('lllllllllllllll',journal_ob)
			for jou in journal_ob:
				od_journ_ids.append(jou.id)



		move_line_ids = []
		data['od_move_lines'] = []
		move = self.get_move_line_ids()
		move_line_ids = move
	  
		data['od_move_lines'] = list(set(move_line_ids))
		if data['form'].get('initial_balance') and not data['form'].get('date_from'):
			raise UserError(_("You must define a Start Date"))
		if od_journ_ids:
			data['form']['journal_ids'] = od_journ_ids

		if od_template:
			data['form']['od_template']=od_template
		# data['form']['target_move']=self.target_move
		# data['form']['display_account']=self.display_account
		# if self.date_from and self.date_to:
		#     if self.date_to < self.date_from:
		#         raise UserError(_('Invalid date.'))
		#     else:
		#         data['form']['date_from']=self.date_from
		#         data['form']['date_to']=self.date_to
		# data['form']['sortby']=self.sortby
		# data['form']['initial_balance']=self.initial_balance

		# journal_ids = []
		# account_ids = []
		# analytic_ids = []
		# partner = []
		# cost_center_ids = []
		# for jou in self.journal_ids:
		#     journal_ids.append(jou.id)
		# data['form']['journal_ids']=journal_ids        
		# for part in self.od_partner_ids:
		#     partner.append(part.id)
		# data['form']['partner'] = partner
		# for analytic in self.od_analytic_ids:
		#     analytic_ids.append(analytic.id)
		# data['form']['analytic'] = analytic_ids
		# for acc in self.od_account_ids:
		#     account_ids.append(acc.id)
		# data['form']['account'] = account_ids
		# for cost in self.od_cost_center_ids:
		#     cost_center_ids.append(cost.id)
		# data['form']['cost'] = cost_center_ids
		# move_line_ids = []
		# data['od_move_lines'] = []
		# if self.move_line_ids:
		#     for move_line in self.move_line_ids:
		#         move_line_ids.append(move_line.id)  
		#     data['od_move_lines'] = move_line_ids
		# if data['form'].get('initial_balance') and not data['form'].get('date_from'):
		#     raise UserError(_("You must define a Start Date"))
		# records = self.env[data['model']].browse(data.get('ids', []))
		# if od_journ_ids:
		#     data['form']['journal_ids'] = od_journ_ids
		return data

	def _build_contexts(self, data):
		result = {}
		result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
		result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
		result['date_from'] = data['form']['date_from'] or False
		result['date_to'] = data['form']['date_to'] or False
		result['strict_range'] = True if result['date_from'] else False
		return result

	def print_excel(self):
		filename= 'GeneralLedger.xls'
		ctx = self.env.context
		data = self.get_data_for_xls()
		sortby = data['form']['sortby']
		init_balance = data['form']['initial_balance']
		date_from =  data['form']['date_from']
		date_to =  data['form']['date_to']
		od_template=data['form'].get('od_template', False)
		# accounts = data['form']['account']
		od_move_lines = self.get_move_line_ids()
		od_move_lines = self.env['account.move.line'].browse(od_move_lines)
		search_cond = '''  '''
		
		if od_move_lines:
			search_cond = search_cond + ''' and l.id in %s '''
					
		if data['form'].get('journal_ids', False):
			codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]
		self.model = self.env.context.get('active_model')
		accounts = self.env['account.account'].browse(ctx.get('active_id')) if self.model == 'account.account' else self.env['account.account'].search([])
		display_account = data['form']['display_account']

		ctx = {'dt_cont':{'date_from':date_from,'date_to':date_to}}
		# print "ctx>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",ctx
		used_context = self._build_contexts(data)
		data['form']['used_context'] = dict(used_context, lang=ctx.get('lang', 'en_US'))
		movelines = self.env['report.account.report_generalledger'].with_context(data['form'].get('used_context',{}))._get_account_move_entry( accounts, init_balance, sortby, display_account,od_move_lines,search_cond,od_template)
		# print "move lines>>>>>>>>>>>>>>>>>>>>>>",movelines
		workbook= xlwt.Workbook(encoding="UTF-8")
		sheet= workbook.add_sheet('General Ledger Report',cell_overwrite_ok=True)
		style = xlwt.easyxf('font:height 400, bold True, name Arial; align: horiz center, vert center;borders: top medium,right medium,bottom medium,left medium')
		style_filter = xlwt.easyxf('font:name Arial; align: horiz center, vert center;')
		a = list(range(1,10))
		row = 0
		col = 0
		# header = header
		style2 = xlwt.easyxf('font: bold 1')
		
		sheet.write(row,0,"Date",style2)
		sheet.write(row,1,"JRNL",style2)
		sheet.write(row,2,"Partner",style2)
		sheet.write(row,3,"Ref",style2)
		sheet.write(row,4,"Move",style2)
		sheet.write(row,5,"Entry Label",style2)
		sheet.write(row,6,"Debit",style2)
		sheet.write(row,7,"Credit",style2)
		sheet.write(row,8,"Balance",style2)
		
		row = 1
		for index,data in enumerate(movelines):
			# print 'ppppppppppppppppppppppppppppppppppppphhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh'
			# print "nameeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
			# print "nameeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
			# print "nameeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
			# print "nameeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
			# print data.get('name')
			name = data.get('name')
			total_credit = data.get('credit')
			total_debit = data.get('debit')
			total_balance = data.get('balance')
			sheet.write(row,0,name,style2)
			sheet.write(row,6,total_debit,style2)
			sheet.write(row,7,total_credit,style2)
			sheet.write(row,8,total_balance,style2)
			row = row +  1
			for inner_index,data1 in enumerate(data.get('move_lines')):
				date = data1.get('ldate')
#                 if date_from and date < date_from:
#                     continue
#                 if date_to and date > date_to:
#                     continue
				lcode = data1.get('lcode')
				partner_name = data1.get('partner_name')
				lref = data1.get('lref')
				move_name = data1.get('move_name')
				# print "lnamelnamelnamelnamelnamelnamelnamelnamelnamelnamelnamelname"
				# print "lnamelnamelnamelnamelnamelnamelnamelnamelnamelnamelnamelname"
				# print "lnamelnamelnamelnamelnamelnamelnamelnamelnamelnamelnamelname"
				# print "lnamelnamelnamelnamelnamelnamelnamelnamelnamelnamelnamelname"
				# print "lnamelnamelnamelnamelnamelnamelnamelnamelnamelnamelnamelname"
				# print data1.get('lname')
				if data1.get('lname') == 'Prepayment Line' :
					print("Prepaymenttttttttttttttttttttttttttttttttttttt")
					print("Prepaymenttttttttttttttttttttttttttttttttttttt")
					print("Prepaymenttttttttttttttttttttttttttttttttttttt")
					print(data1.get('lanalytic_account_name'))
				lname = data1.get('lname')
				debit = data1.get('debit')
				credit = data1.get('credit')
				balance = data1.get('balance')
				currency_id = data1.get('currency_id')
				sheet.write(row+inner_index,col,date)
				sheet.write(row+inner_index,col+1,lcode)
				sheet.write(row+inner_index,col+2,partner_name)
				sheet.write(row+inner_index,col+3,lref)
				sheet.write(row+inner_index,col+4,move_name)
				sheet.write(row+inner_index,col+5,lname)
				sheet.write(row+inner_index,col+6,debit)
				sheet.write(row+inner_index,col+7,credit)
				sheet.write(row+inner_index,col+8,balance)
				sheet.write(row+inner_index,col+9,name)
			row = row + len(data.get('move_lines')) + 1
		fp = StringIO()
		workbook.save(fp)
		excel_file = base64.encodestring(fp.getvalue())
		self.excel_file = excel_file
		self.file_name =filename
		fp.close()
		ir_model_data = self.env['ir.model.data']
		compose_form_id = ir_model_data.get_object_reference('account', 'account_report_general_ledger_view')[1]
		return {            
		'type': 'ir.actions.act_window',            
		'view_type': 'form',            
		'view_mode': 'form',            
		'res_model': 'account.report.general.ledger',            
		'views': [(compose_form_id, 'form')], 
		'res_id': self.id,           
		'view_id': compose_form_id,            
		'target': 'new',            
		}

	def _print_report(self, data):
		data = self.pre_print_report(data)
		od_journ_ids = []
		cost_center_ids = []
		data['form']['cost_center_ids'] = []
		od_journal_ids = self.od_journal_ids
		od_template=self.od_template
		if od_journal_ids:
			for jou in od_journal_ids:
				od_journ_ids.append(jou.id)	
		od_cost_center_ids = self.od_cost_center_ids
		if od_cost_center_ids:
			for cos in od_cost_center_ids:
				cost_center_ids.append(cos.id)
		data['form'].update(self.read(['initial_balance', 'sortby'])[0])
#        move_line_ids = []
#        data['od_move_lines'] = []
#    	if self.move_line_ids:
#    		for move_line in self.move_line_ids:
#    			move_line_ids.append(move_line.move_line_id.id)

		move = self.get_move_line_ids()
		move_line_ids = move
		data['od_move_lines'] = list(set(move_line_ids))
		if data['form'].get('initial_balance') and not data['form'].get('date_from'):
			raise UserError(_("You must define a Start Date"))
		records = self.env[data['model']].browse(data.get('ids', []))
		if od_journ_ids:
			data['form']['journal_ids'] = od_journ_ids
		if od_cost_center_ids:
			data['form']['cost_center_ids'] = cost_center_ids
		data['form']['od_template']=od_template or False	
		
		return self.env['report'].with_context(landscape=True).get_action(records, 'account.report_generalledger', data=data)
		
class WizardAccountMoveLine(models.TransientModel):
	_name = "wizard.account.move.line"
	wizard_id = fields.Many2one('wizard.account.move.line',string='Wizard')
	move_line_id = fields.Many2one('account.move.line',string='MoveLine')        
	
