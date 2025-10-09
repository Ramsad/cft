# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

import odoo.addons.decimal_precision as dp


class ODOverdue(models.Model):
    _name = "od.overdue"
    partner_id = fields.Many2one('res.partner','Partner')
    user_id = fields.Many2one('res.users','Sales Person',related='partner_id.user_id')
    ref = fields.Char(string='Ref')
    label = fields.Char(string='Name')
    due_date = fields.Date(string='Due Date')
    debit = fields.Float(string='Due')
    credit = fields.Float(string='Paid')
    balance = fields.Float(string='Balance')
    number = fields.Char(string='Number')
    date = fields.Date(string='Date')
    od_released = fields.Boolean('Released')
    pdc = fields.Boolean('PDC')
    journal_code = fields.Char(string='Journal Code')
	
	
    
  





 
