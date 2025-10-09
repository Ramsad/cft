# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero
class account_asset_asset(models.Model):
	_inherit = 'account.asset'
	od_purchase_date = fields.Date('OD Purchase Date')
	od_sequence = fields.Char('Sequence',readonly=True)
	od_cost = fields.Float('Cost')
	od_depreciation = fields.Float('Depreciation')
	od_serial_number = fields.Char('Serial Number')
	od_prorata_days = fields.Boolean('Prorata Days')
	od_amount_per_day = fields.Char('Amount Per Day')
	od_cost_center_id = fields.Many2one('orchid.account.cost.center','Cost Center')
	od_mac_address = fields.Char('MAC Address')
	od_closing_date = fields.Date('Closing Date')
	od_warranty_date = fields.Date('Warranty Date')
	custodion_id = fields.Many2one('res.partner',string='Custodion')


	# 
	# def create(self, vals):
	# 	asset = super(account_asset_asset, self.with_context(mail_create_nolog=True)).create(vals)
	# 	if asset['date']:
	# 		asset['od_purchase_date'] = asset['date']
	# 	if asset['value']:
	# 		asset['od_cost'] = asset['value']
	# 	return asset
	
	# def compute_depreciation_board(self, cr, uid, ids, context=None):
	# 	res = super(account_asset_asset,self).compute_depreciation_board(cr, uid, ids, context=context)
	# 	return res
#    def _check_mac_address(self, cr, uid, ids, context=None):
#        obj_fy = self.browse(cr, uid, ids[0], context=context)
#        mac_address = obj_fy.od_mac_address
#        if mac_address:
#            length_of_mac = len(mac_address)
#            if length_of_mac != 17:
#                return False
#            length_of_attributes_mac = len(mac_address.split(':'))
#            if length_of_attributes_mac != 6:
#                return False
#        return True

#    def set_to_close(self, cr, uid, ids, context=None):
#        obj = self.browse(cr,uid,ids,context)
#        today_current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#        print "iiiiiiiiiiiiiiiiiiiiiii",today_current_datetime
#        if not obj.od_closing_date:
#            self.write(cr, uid, ids, {'od_closing_date': str(today_current_datetime)}, context=context)
#            
#        return self.write(cr, uid, ids, {'state': 'close'}, context=context)


#    def create(self, cr, uid, vals, context=None):
#        if context is None:
#            context = {}
#        if vals.get('od_sequence', '/') == '/':
#            vals['od_sequence'] = self.pool.get('ir.sequence').get(cr, uid, 'od.asset.asset') or '/'
#        return super(account_asset_asset,self).create(cr, uid, vals, context=context)



#    _columns = {
#                'od_purchase_date':fields.date('OD Purchase Date',states={'draft':[('readonly',False)]},readonly=True),
#                'od_sequence':fields.char('Sequence',readonly=True),
#                'od_cost':fields.float('Cost',states={'draft':[('readonly',False)]},readonly=True),
#                'od_depreciation':fields.float('Depreciation',states={'draft':[('readonly',False)]},readonly=True),
#                'od_serial_number':fields.char('Serial Number',states={'draft':[('readonly',False)]},readonly=True),
#                'od_prorata_days':fields.boolean('Prorata Days',states={'draft':[('readonly',False)]},readonly=True),
#                'od_amount_per_day':fields.char('Amount Per Day',readonly=True),
#                'od_cost_center_id':fields.many2one('od.cost.centre',string='Cost Centre',states={'draft':[('readonly',False)]},readonly=True),
#                'od_mac_address':fields.char('MAC Address',states={'draft':[('readonly',False)]},readonly=True),
#                'od_closing_date':fields.date('Closing Date',)
#                }
#    _defaults = {
#                 'od_sequence':'/',
#                 'od_purchase_date': fields.date.context_today,
#                 }


#    _constraints = [
#        (_check_mac_address, 'Error!\nmac address should be like the format 64:5a:04:9c:bc:ca', ['od_mac_address'])
#    ]




	
	# def compute_depreciation_board(self):
	# 	res = super(AccountAssetAsset,self).compute_depreciation_board()
	# 	return res


#     def compute_depreciation_board(self, cr, uid, ids, context=None):
#         res = super(account_asset_asset,self).compute_depreciation_board(cr, uid, ids, context=context)
#         print "haiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiffffffffffffffffffffffffffffffffffffffiiiii",res
#         return res




#    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
#        res = super(account_asset_asset,self).onchange_category_id(cr, uid, ids, category_id, context=context)
#        asset_categ_obj = self.pool.get('account.asset.category')
#        if category_id:
#            category_obj = asset_categ_obj.browse(cr, uid, category_id, context=context)
#            res['value']['od_prorata_days'] = category_obj.od_prorata_days
#            print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",res
#        return res
#
# 	def onchange_category_id_values(self, category_id):
# 		res = super(account_asset_asset,self).onchange_category_id_values(category_id)
# 		print("111111111111111111111111111",res)
# 		if category_id:
#
# 			res['value']['od_prorata_days'] = self.category_id.od_prorata_days
# 		return res
#
#
# 	@api.onchange('category_id')
# 	def onchange_category_id(self):
# 		res = super(account_asset_asset,self).onchange_category_id()
# 		print("gggggggggggggggggggggggggggggggggggggggggggg",res)
#
# 		return res
#
#
# 	def last_day_of_month(self,any_day):
# 		next_month = any_day.replace(day=28) + relativedelta(days=4)  # this will never fail
# 		return next_month - relativedelta(days=next_month.day)
#
#
# 	def compute_depreciation_board(self):
# 		depreciation_lin_obj = self.env['account.asset.depreciation.line']
# 		currency_obj = self.env['res.currency']
# 		total_amount = 0
#
# 		for asset in self:
# 			amount_check = asset.value - asset.salvage_value
# 			if asset.value_residual == 0.0:
# 				continue
# 			posted_depreciation_line_ids = depreciation_lin_obj.search([('asset_id', '=', asset.id), ('move_check', '=', True)],order='depreciation_date desc')
# 			old_depreciation_line_ids = depreciation_lin_obj.search([('asset_id', '=', asset.id), ('move_id', '=', False)])
# 			if old_depreciation_line_ids:
# 				old_depreciation_line_ids.unlink()
#
# 			amount_to_depr = residual_amount = asset.value_residual
#
# 			if asset.prorata:
# #                depreciation_date = datetime.strptime(self._get_last_depreciation_date())
# 				depreciation_date = datetime.strptime(self._get_last_depreciation_date()[self.id], DF).date()
# 				depreciation_date=self.last_day_of_month(depreciation_date)
#
# 			else:
# 				# depreciation_date = 1st January of purchase year
# 				purchase_date = datetime.strptime(asset.date, '%Y-%m-%d')
# 				#if we already have some previous validated entries, starting date isn't 1st January but last entry + method period
# 				if (len(posted_depreciation_line_ids)>0):
# 					last_depreciation_date = datetime.strptime(posted_depreciation_line_ids[0].depreciation_date, '%Y-%m-%d')
# 					depreciation_date = (last_depreciation_date+relativedelta(months=+asset.method_period))
# 				else:
# 					depreciation_date = datetime(purchase_date.year, 1, 1)
# 			day = depreciation_date.day
# 			month = depreciation_date.month
# 			year = depreciation_date.year
# 			total_days = (year % 4) and 365 or 366
# 			undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date, total_days)
# 			if asset.prorata and asset.od_prorata_days:
# 				dep_date = datetime.strptime(self._get_last_depreciation_date()[self.id], DF).date()
# 				depreciation_date = self.last_day_of_month(dep_date)
# 				delta = depreciation_date - dep_date
# 				no_of_days = delta.days + 1
# #                 last_date = depreciation_date + relativedelta(months=asset.method_number)
# 				new_ldate = dep_date + relativedelta(months=asset.method_number,days=-1)
# 				total_delta = new_ldate - dep_date
# 				total_days = total_delta.days +1
# 				if not total_days:
# 					amount_per_day = 0
# 				else:
# 					amount_per_day = asset.value_residual/total_days
# #                asset.od_amount_per_day = amount_per_day
# 				for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
# 					i = x + 1
# 					company_currency = asset.company_id.currency_id.id
# 					current_currency = asset.currency_id.id
# 					amount = amount_per_day * no_of_days
# 					residual_amount -= amount
#
# 					if i == undone_dotation_number:
# 						amount = amount_check - total_amount
# 						amount = round(amount,3)
# 						print("last vals amount_check,total_amount,amount",amount_check,total_amount,amount)
# 					else:
# 						total_amount += amount
# 					vals = {
# 						 'amount': amount,
# 						 'od_no_of_days':no_of_days,
# 						 'asset_id': asset.id,
# 						 'sequence': i,
# 						 'name': str(asset.id) +'/' + str(i),
# 						 'remaining_value': residual_amount,
# 						 'depreciated_value': (asset.value - asset.salvage_value) - (residual_amount + amount),
# 						 'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
# 					}
#
# 					if amount:
# 						depreciation_lin_obj.create(vals)
# 					next_date = (datetime(year, month, 0o1) + relativedelta(months=+asset.method_period))
# 					depreciation_date=self.last_day_of_month(next_date)
# 					delta = depreciation_date - next_date
# 					if str(depreciation_date) > str(new_ldate):
# 						delta = datetime.strptime(str(new_ldate)[:10],DF) - datetime.strptime(str(next_date)[:10],DF)
# 					no_of_days = delta.days+1
# 					day = depreciation_date.day
# 					month = depreciation_date.month
# 					year = depreciation_date.year
# 				return True
#
# 			else:
# 				for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
# 					i = x + 1
# 					amount = self._compute_board_amount(i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date)
#
#
# 					company_currency = asset.company_id.currency_id
# 					current_currency = asset.currency_id
#
#
#
#
# 					# compute amount into company currency
# 					amount = current_currency.compute(amount, company_currency)
# 					residual_amount -= amount
#
# 					vals = {
# 						 'amount': amount,
# 						 'asset_id': asset.id,
# 						 'sequence': i,
# 						 'name': str(asset.id) +'/' + str(i),
# 						 'remaining_value': residual_amount,
# 						 'depreciated_value': (asset.value - asset.salvage_value) - (residual_amount + amount),
# 						 'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
# 					}
#
# 					if amount:
# 						depreciation_lin_obj.create(vals)
# 					# Considering Depr. Period as months
# 					depreciation_date = (datetime(year, month, day) + relativedelta(months=+asset.method_period))
# 					depreciation_date=self.last_day_of_month(depreciation_date)
# 					day = depreciation_date.day
# 					month = depreciation_date.month
# 					year = depreciation_date.year
# 		return True
# class account_asset_depreciation_line(models.Model):
# 	_inherit = 'account.asset.depreciation.line'
#
# 	od_no_of_days = fields.Char('Days')

#    
#    def create_move(self, post_move=True):
#        can_close = False
#        asset_obj = self.env['account.asset']
#        period_obj = self.env['account.period']
#        move_obj = self.env['account.move']
#        move_line_obj = self.env['account.move.line']
#        currency_obj = self.env['res.currency']
#        created_move_ids = []
#        asset_ids = []
#        for line in self:
#            depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
#            company_currency = line.asset_id.company_id.currency_id
#            current_currency = line.asset_id.currency_id
#            amount = current_currency.compute(line.amount, company_currency)
#            sign = (line.category_id.journal_id.type == 'purchase' and 1) or -1
##            sign = (line.asset_id.category_id.journal_id.type == 'purchase' and 1) or -1
#            asset_name = line.asset_id.name
#           	cost_centre_id = line.asset_id.od_cost_center_id and line.asset_id.od_cost_center_id.id or False
#            reference = line.name
#            move_vals = {
#                'name': asset_name,
#                'date': depreciation_date,
#                'ref': reference,
#                'journal_id': line.asset_id.category_id.journal_id.id,
#                }
#            move_id = move_obj.create(move_vals)
#            journal_id = line.asset_id.category_id.journal_id.id
#            partner_id = line.asset_id.partner_id.id
#            move_line_obj.create({
#                'name': asset_name,
#                'ref': reference,
#                'move_id': move_id,
#                'account_id': line.asset_id.category_id.account_depreciation_id.id,
#                'debit': 0.0,
#                'credit': amount,
#                'od_cost_centre_id':od_cost_centre_id,
#                'journal_id': journal_id,
#                'partner_id': partner_id,
#                'currency_id': company_currency.id != current_currency.id and  current_currency.id or False,
#                'amount_currency': company_currency.id != current_currency.id and - sign * line.amount or 0.0,
#                'date': depreciation_date,
#            })
#            move_line_obj.create({
#                'name': asset_name,
#                'ref': reference,
#                'move_id': move_id,
#                'account_id': line.asset_id.category_id.account_expense_depreciation_id.id,
#                'credit': 0.0,
#                'debit': amount,
#                'od_cost_centre_id':od_cost_centre_id,
#                'journal_id': journal_id,
#                'partner_id': partner_id,
#                'currency_id': company_currency.id != current_currency.id and  current_currency.id or False,
#                'amount_currency': company_currency.id != current_currency.id and sign * line.amount or 0.0,
#                'analytic_account_id': line.asset_id.category_id.account_analytic_id.id,
#                'date': depreciation_date,
#                'asset_id': line.asset_id.id
#            })
#            self.write({'move_id': move_id})
#            created_move_ids.append(move_id)
#            asset_ids.append(line.asset_id.id)
##        # we re-evaluate the assets to determine whether we can close them
#        for asset in asset_obj.browse(list(set(asset_ids))):
##            if currency_obj.is_zero(cr, uid, asset.currency_id, asset.value_residual):
#           asset.write({'state': 'close'})
#        return created_move_ids



# class account_asset_category(models.Model):
# 	_inherit = 'account.asset.category'
# 	od_prorata_days = fields.Boolean('Prorata Days')
#
