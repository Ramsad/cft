# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models, SUPERUSER_ID, _


class ReportPartnerOverdue(models.AbstractModel):
	_name = 'report.orchid_account_enhancement.report_od_invoice_aging'

	
	def render_html(self,docids,data):
		model = self.env.context.get('active_model')
		docs = self.env[model].browse(self.env.context.get('active_id'))
		docargs = {
			'doc_ids': self.ids,
			'doc_model': model,
			'docs': docs,
			'periods': data['periods'],
			'move_lines': data['values']
		}
		return self.env['report'].render('orchid_account_enhancement.report_od_invoice_aging', docargs)
