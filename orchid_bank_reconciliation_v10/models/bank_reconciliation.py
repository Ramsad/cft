# -*- coding: utf-8 -*-
import itertools
from lxml import etree
from odoo import models, fields, api, _

import odoo.addons.decimal_precision as dp

class od_bank_reconciliation(models.Model):
	_name = 'od.bank.reconciliation'
	_description = "Bank Reconciliation"

	def od_get_company_id(self):
		return self.env.user.company_id
	company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)



	def apply_bank_date_all(self):
		bank_date = self.bank_date
		if bank_date:
			for line in self.move_line_ids:
				line.od_reconcile_date = bank_date

	def write(self, values):

		result = super(od_bank_reconciliation, self).write(values)
		print("vvvvvvvvvvvvvvvvvvvvvvvvv",result)
		self.update_check_no()

		return result                
				
	
	def update_check_no(self):
		move_line_ids = self.move_line_ids
		print("]]]]]]]]]]]]]]]]]]]]]]]",len(move_line_ids))
		for move in move_line_ids:
			account_payment_ids = self.env['account.payment'].search([('name', '=', move.move_id.name)])
			print("account_payment_ids111111111111111111111111111111",account_payment_ids)
			
			for account_payment  in account_payment_ids:
				print(":::::::::::::::::::::::::::;",account_payment.od_check_no)
				if account_payment:
					move.write({'od_check_vnumber':account_payment.od_check_no})
#                    move.od_check_vnumber = account_payment.od_check_no or ''
			
		
	
	def apply_bank_date(self):
		bank_date = self.bank_date
		if bank_date:
			for line in self.move_line_ids:
				if not line.od_reconcile_date:
					line.od_reconcile_date = bank_date

	
	def update_all_with_effective_date(self):
		for move in self.move_line_ids:
			move.od_fill_date()
		return True

	
	def unlink(self):
#        for bank in self:
#            if bank.state not in ('draft'):
		raise Warning(_('You can delete only draft document'))
		return super(od_bank_reconciliation, self).unlink()

	# TODO:  removed in newer Odoo; refactor for recordsets
# 
	def button_dummy(self):
		return True

	
	def od_open_bank_stmt_reconcile(self):
		#unlink existing
	
		move_line_ids = self.env['account.move.line'].search([('od_reconcile_id','=',self.id)])
		move_line_ids.write({'od_reconcile_id':''})

		

		account_id = self.account_id and self.account_id.id
		date = self.date
		to_date = self.to_date
		date_check = str(self.date_filter)



		domain = ['&','|',('debit','>',0),('credit','>',0),('account_id', '=', account_id)]
		# print "domainnnnnn",domain.append((date_check, '>=', date))
#        if period_id:
#            domain.append(('period_id', '=', period_id))
		
		if date_check == 'od_report':
			if not to_date:
				raise Warning(_('You have to select To Date'))
			
			move_line_ids = self.env['account.move.line'].search(['|','&',('od_reconcile_date', '>', to_date ),('date','<=',to_date),('od_reconcile_date', '=', False ),('date','<=',to_date) and ('date','<=',to_date), '&','|',('debit','>',0),('credit','>',0),('account_id', '=', account_id)])	
			

			move_lines = [x for x in move_line_ids if ((x.move_id.state == 'posted'))]
			# print "move_lieeeeeeeeeeeeeeee",move_lines

			line_ids = [x.id for x in move_lines]
			move_line_ids = self.env['account.move.line'].browse(line_ids)

			if not move_line_ids:
				raise except_orm(_('No Entity To Reconcile!'), _('Please select another account'))

			move_line_ids.write({'od_reconcile_id':self.id})
			return True

		# 	if to_date and not date:
		# 		domain.append(('date', '>=', to_date))
				# domain.append((line_date, '>=', line_recon_date))
				# domain.append((line_recon_date, '==', ' '))
		if date and to_date:
			domain.append((date_check, '>=', date))
			domain.append((date_check, '<=', to_date))
		if date and not to_date:
			domain.append((date_check, '>=', date))
		if to_date and not date:
			domain.append((date_check, '<=', to_date))
#         move_line_ids = self.env['account.move.line'].search(domain)
#        print "\n\n&***",self.date_filter
#
		# print "##\n\n\n\n@@",domain


		if self.type == 'reconciled':
			domain.append(('od_reconcile_date', '!=',False))

		elif self.type == 'unreconciled':
			domain.append(('od_reconcile_date', '=',False))


		move_line_ids = self.env['account.move.line'].search(domain)
#        move_lines = filter(lambda x:((x.move_id.state == 'posted') and ((x.move_id.period_id.od_sequence == 0) or (x.move_id.period_id.special == False))),move_line_ids)

		move_lines = [x for x in move_line_ids if ((x.move_id.state == 'posted'))]


#        move_lines = filter(lambda x:((x.move_id.state== 'posted') and not x.move_id.period_id.special),move_line_ids)
		line_ids = [x.id for x in move_lines]
		move_line_ids = self.env['account.move.line'].browse(line_ids)

		if not move_line_ids:
			raise except_orm(_('No Entity To Reconcile!'), _('Please select another account'))

		move_line_ids.write({'od_reconcile_id':self.id})
		return True

	
	def od_reconcile_bank_stmt_reconcile(self):
		move = self.move_line_ids
		lines = move.filtered(lambda r: r.od_reconcile_date == False)
		lines.write({'od_reconcile_id':False})
		account_id = self.account_id and self.account_id.id
		from_date = self.date
		to_date = self.to_date
		if account_id:
			context = self._context
			ctx={'account_id': account_id}
#            recs = self.pool.get('account.move.line').browse(self._cr, self._uid, [], ctx)
			res = self.env['account.move.line'].od_book_bank_balance(self._cr,self._uid,from_date,to_date,ctx)
			self.book_balance=bkb=res and res.get('book_balance') or 0.0
			self.bank_balance =bnb= res and res.get('bank_balance')  or 0.0
			self.fc_bank_balance=fcbkb=res and res.get('fc_bank_balance') or 0.0
			self.fc_book_balance=fcbnb=res and res.get('fc_book_balance') or 0.0
		self.state='done'
		return True

	# TODO:  removed in newer Odoo; refactor for recordsets
# 
	@api.depends('account_id','date','to_date')
	def _compute_balance(self):
		account_id = self.account_id and self.account_id.id
		from_date = self.date
		to_date = self.to_date
		if account_id:
			context = self._context
			ctx={'account_id': account_id}
#            recs = self.pool.get('account.move.line').browse(self._cr, self._uid, [], ctx)
			res = self.env['account.move.line'].od_book_bank_balance(self._cr,self._uid,from_date,to_date,ctx)
			self.book_balance = res and res.get('book_balance') or 0.0
			self.bank_balance = res and res.get('bank_balance')  or 0.0
			self.fc_bank_balance = res and res.get('fc_bank_balance') or 0.0
			self.fc_book_balance = res and res.get('fc_book_balance') or 0.0
			self.reconciled_balance = res and res.get('reconciled_balance') or 0.0
			self.unconciled_balance = res and res.get('unconciled_balance') or 0.0


	@api.onchange('account_id','date','to_date')
	def onchange_account_id(self):
		account_id = self.account_id and self.account_id.id
		from_date = self.date
		to_date = self.to_date
		if account_id:
			context = self._context
			ctx={'account_id': account_id}
#            recs = self.pool.get('account.move.line').browse(self._cr, self._uid, [], ctx)
#            res = recs.env['account.move.line'].od_book_bank_balance(from_date,to_date)
			res = self.env['account.move.line'].od_book_bank_balance(self._cr,self._uid,from_date,to_date,ctx)
			self.book_balance = res and res.get('book_balance') or 0.0
			self.bank_balance = res and res.get('bank_balance')  or 0.0
			self.fc_bank_balance = res and res.get('fc_bank_balance') or 0.0
			self.fc_book_balance = res and res.get('fc_book_balance') or 0.0
			self.reconciled_balance = res and res.get('reconciled_balance') or 0.0
			self.unconciled_balance = res and res.get('unconciled_balance') or 0.0


	name = fields.Char(string='Reference/Description')
	account_id = fields.Many2one('account.account',string="Account",required=True,readonly=True,states={'draft': [('readonly', False)]})
#    period_id = fields.Many2one('account.period',string="Period",readonly=True,states={'draft': [('readonly', False)]},domain=['|',('od_sequence','=',0),('special','=',False)])
	to_date = fields.Date('To Date')
	bank_date = fields.Date(string="Bank Date")
	state = fields.Selection([
			('draft','Draft'),
			('open','Open'),
			('done','Reconciled'),
		], string='Status', index=True, readonly=True, default='draft',copy=False)
	date = fields.Date(string='From Date', index=True, default=fields.Date.today(),
		help="Keep empty to use the current date", copy=False)
	date_filter = fields.Selection([('date','Cheque'),('od_reconcile_date','Bank'),('od_report','Report')],string="Date",default='date')

	move_line_ids = fields.One2many('account.move.line','od_reconcile_id',string='Reconcile Lines',states={'open': [('readonly', False)]},copy=False)


	book_balance = fields.Float(string='Book Balance', digits=dp.get_precision('Account') ,readonly=True,compute='_compute_balance')
	bank_balance = fields.Float(string='Bank Balance', digits=dp.get_precision('Account'),readonly=True,compute='_compute_balance')
	fc_book_balance = fields.Float(string='FC Book Balance', digits=dp.get_precision('Account'),readonly=True,compute='_compute_balance')
	fc_bank_balance = fields.Float(string='FC Bank Balance', digits=dp.get_precision('Account'),readonly=True,compute='_compute_balance')
	reconciled_balance = fields.Float(string='Reconciled', digits=dp.get_precision('Account'),readonly=True,compute='_compute_balance')
	unconciled_balance = fields.Float(string='Unreconciled', digits=dp.get_precision('Account'),readonly=True,compute='_compute_balance')

	type = fields.Selection([
			('unreconciled','UnReconciled'),
			('reconciled','Reconciled'),
			('all','All'),
		], string='Type',default='unreconciled')

	_sql_constraints = [
		('account_id_uniq', 'unique(account_id)',
			'Account is unique per Reconciliation'),
	]


#    
#    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#        res = super(od_bank_reconciliation, self).fields_view_get(
#            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#        context = self._context
#        doc = etree.XML(res['arch'])
#        for node in doc.xpath("//field[@name='account_id']"):
#            if context.get('bank'):
#                ids = self.pool.get('account.account').search(self._cr,self._uid,[('type','=','liquidity')])
#                val = "[('id', '=',"+str(ids)+")]"
#                node.set('domain', val)
#            res['arch'] = etree.tostring(doc)
#        return res







class account_move(models.Model):
	_inherit = "account.move"

	
	def button_cancel(self):
		for line in self.line_ids:
			line.od_reconcile_id = False
			line.od_reconcile_date = ''
		return super(account_move,self).button_cancel()

class account_move_line(models.Model):
	_inherit = 'account.move.line'


	
	def od_fill_date(self):
		if self.od_reconcile_id.state == 'done':
			raise except_orm(_('Already Reconciled!'), _('Try for other'))
		self.od_reconcile_date = self.date
		return True

	# TODO:  removed in newer Odoo; refactor for recordsets
# 
	@api.depends('move_id','date','name','od_reconcile_date')
	def _compute_check_date(self):
		if self.move_id:
			account_payment_ids = self.env['account.payment'].search([('move_name', '=', self.move_id.name)])
			for account_payment  in account_payment_ids:
				if account_payment:
					self.od_check_date = account_payment.od_check_date or False

	od_reconcile_id = fields.Many2one('od.bank.reconciliation',string='Bank Reconciled')
	od_check_date = fields.Date(string='Check Date',readonly=True,compute='_compute_check_date')
