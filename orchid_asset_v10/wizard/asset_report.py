# -*- encoding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
# import logging
# _logger = logging.getLogger(__name__)

class od_asset_report(models.TransientModel):
	_name = 'od.asset.report' 
	_description = 'Asset Report'

	company_id = fields.Many2one('res.company', string='Company',readonly=True,default=lambda self: self.env['res.company']._company_default_get('od.asset.report'))
	category_ids = fields.Many2many('account.asset.category',string='Asset Category')
	date_from = fields.Date('Start Date',required=True,domain="[('company_id','=',company_id)]")
	date_to = fields.Date('End Date',required=True,domain="[('company_id','=',company_id)]")

	def pre_print_report(self):
		if context is None:
			context = {}
		return data

	def build_filter(self):
		data = self.read(['date_from', 'date_to', 'category_ids', 'company_id'])[0]
		
		if not data.get('category_ids'):
			category_ids = self.env['account.asset.category'].search([('company_id','=',data.get('company_id')[0])])
			data['category_ids'] = [ids.id for ids in category_ids]
		if not data.get('date_from') or not data.get('date_to') or data.get('date_from') > data.get('date_to'):
			raise UserError(('Date field should be proper'))
		return data

	def print_report(self):        
		data = self.build_filter()
		return self.env['report'].with_context(landscape=True).get_action(self,'orchid_asset_v10.report_asset_statement', data=data)

	