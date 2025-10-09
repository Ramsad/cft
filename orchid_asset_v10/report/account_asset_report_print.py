# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models
from datetime import datetime


class ReportAssetStatement(models.AbstractModel):
	_name = 'report.orchid_asset_v10.report_asset_statement'
	# _template = 'orchid_asset_v10.report_asset_statement'


	
	def render_html(self, docids, data=None):
		# print data,'renderrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr'
		model = self.env.context.get('active_model')
		docs = self.env[model].browse(self.env.context.get('active_id'))
		report_obj = self.env['report']
		date = datetime.now()
		docargs = {
			'doc_ids': self.ids,
			'doc_model': model,
			'docs': docs,
			'filters':data,
			'get_category_by_id':self.get_category_by_id,
			'get_asset_by_category':self.get_asset_by_category,
			'get_depreciation_amt':self.get_depreciation_amt,
			'get_acc_depreciation_amt':self.get_acc_depreciation_amt,
			'date':date,
		}
		# print docargs
		return self.env['report'].render('orchid_asset_v10.report_asset_statement', docargs)


	def get_category_by_id(self,category_id):
		if category_id:
			return self.env['account.asset.category'].browse(category_id).name
		return {}




	def get_asset_by_category(self,category_id,filter):
		asset_obj = self.env['account.asset']
		asset_ids = asset_obj.search([('category_id','=',category_id),('od_purchase_date','<=',filter.get('date_to'))])
		return asset_ids

	def get_depreciation_amt(self,val,asset):
		move_ids = []
		res =0.0
		# print '///////////////////////////',val
		# print asset
		if val.get('date_from') and val.get('date_to'):
			asset_move_line_pool = self.env['account.asset.depreciation.line']
			# print val
			# print asset
			line_ids = asset_move_line_pool.search([('depreciation_date','>=',val.get('date_from')),('depreciation_date','<=',val.get('date_to')),('asset_id','=',asset.id)])
			for val in line_ids:
				if val.move_check:
					res = res + val.amount
		# print res,'llllllllllllllll'
		return res


	def get_acc_depreciation_amt(self,val,asset):
		move_ids = []
		res = 0
		# print '///////////////////////////',val
		# print asset
		if val.get('date_from') and val.get('date_to'):
			asset_move_line_pool = self.env['account.asset.depreciation.line']
			# print val
			# print asset
			line_ids = asset_move_line_pool.search([('depreciation_date','<',val.get('date_from')),('asset_id','=',asset.id)])
			for val in line_ids:
				if val.move_check:
					res = res + val.amount
		# print res,'llllllllllllllll'
		return res