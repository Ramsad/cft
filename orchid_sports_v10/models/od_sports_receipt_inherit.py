
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta
import time
# from odoo.osv import fields, osv
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import odoo.addons.decimal_precision as dp
from odoo import workflow



class od_sports_receipt_line(models.Model):
    _inherit = 'od.sports.receipt.line'

    # 
    # def _search(self, operator, value):
    #     if self._context is None:
    #         self._context={}
    #     so_ids=[]
    #     if self._context.get('roster') and not self._context.get('roster_date'):
    #         operator.append(['id', 'in', so_ids])
    #     if self._context.get('roster') and self._context.get('roster_date'):
    #         date = self._context.get('roster_date')
    #         qry = """select id from sale_order where state in ('progress','manual') and date_order >= '%s' and date_order < ('%s'::date + '1 day'::interval)"""%(date,date)
    #         self._cr.execute(qry)
    #         res = self._cr.fetchall()
    #         if res:
    #             so_ids.extend([i[0] for i in res])
    #         operator.append(['id', 'in', so_ids])
    #     return super(od_sports_receipt_line, self)._search(operator, value)

    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     if self._context is None:
    #         self._context={}
    #     so_ids=[]
    #     if self._context.get('roster') and not self._context.get('roster_date'):
    #         args.append(['id', 'in', so_ids])
    #     if self._context.get('roster') and self._context.get('roster_date'):
    #         date = context.get('roster_date')
    #         qry = """select id from sale_order where state in ('progress','manual') and date_order >= '%s' and date_order < ('%s'::date + '1 day'::interval)"""%(date,date)
    #         self._cr.execute(qry)
    #         res = self._cr.fetchall()
    #         if res:
    #             so_ids.extend([i[0] for i in res])
    #         args.append(['id', 'in', so_ids])
    #     return super(sale_order, self)._search(args, offset=offset, limit=limit, order=order)
    #
    #


