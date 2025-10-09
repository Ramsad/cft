# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, SUPERUSER_ID, _

class od_attendance_total_view(models.Model):
    _name = "od.attendance.total.view"
    _description = "od.attendance.total.view"
    _auto = False
    _rec_name = 'activities_id'

    attendance = fields.Float(string='Attendance')
    activities_id = fields.Many2one('od.activities',string='Program')

#
#     def _select(self):
#         select_str = """
#              SELECT ROW_NUMBER () OVER (ORDER BY od_sports_attendance.id ) AS id,
#                 od_sports_attendance.activities_id as activities_id,
# 	            COUNT(od_sports_attendance_line.attendance) as attendance
#
#
#
#         """
#
#         return select_str
#
#     def _from(self):
#         from_str = """
#                 od_sports_attendance
#         """
#         return from_str
#     def _group_by(self):
#         group_by_str = """
# GROUP BY  od_sports_attendance.activities_id,
# od_sports_attendance.id
#
#
#         """
#         return group_by_str






    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
INNER JOIN od_sports_attendance_line ON od_sports_attendance.id = od_sports_attendance_line.attendance_id
WHERE od_sports_attendance_line.attendance is TRUE
  %s
            )""" % (self._table, self._select(), self._from() ,self._group_by()))


