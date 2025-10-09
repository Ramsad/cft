# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, SUPERUSER_ID, _

class od_collection_sum_view(models.Model):
    _name = "od.collection.sum.view"
    _description = "od.collection.sum.view"
    _auto = False
    _rec_name = 'amount'

    amount = fields.Float(string='Amount')
    activities_id = fields.Many2one('od.activities',string='Program')

#
#     def _select(self):
#         select_str = """
#              SELECT ROW_NUMBER () OVER (ORDER BY od_sports_receipt.id ) AS id,
#                 od_sports_receipt.activities_id as activities_id,
# 	            SUM(od_sports_receipt_line.amount) as amount
#
#
#
#         """
#
#         return select_str
#
#     def _from(self):
#         from_str = """
#                 od_sports_receipt
#         """
#         return from_str
#     def _group_by(self):
#         group_by_str = """
# GROUP BY  od_sports_receipt.activities_id,
# od_sports_receipt.id
#
#         """
#         return group_by_str
#
#

#
#
#
#     def init(self):
#         tools.drop_view_if_exists(self._cr, self._table)
#         self._cr.execute("""CREATE or REPLACE VIEW %s as (
#             %s
#             FROM  %s
# INNER JOIN od_sports_receipt_line ON od_sports_receipt.id = od_sports_receipt_line.receipt_id
#   %s
#             )""" % (self._table, self._select(), self._from(), self._group_by()))


