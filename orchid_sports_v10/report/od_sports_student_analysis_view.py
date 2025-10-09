# -*- coding: utf-8 -*-
from odoo import tools
from odoo.osv import fields, osv
class od_sports_student_analysis_view(osv.osv):
    _name = "od.sports.student.analysis.view"
    _description = "od.sports.student.analysis.view"
    _auto = False
    _rec_name = 'attendance_id'
    _columns = {

        'attendance_id':fields.many2one('od.sports.attendance', string='Name'),

    }
    #
    # def _select(self):
    #     select_str = """
    #          SELECT ROW_NUMBER () OVER (ORDER BY osal.id ) AS id,
    #             osal.attendance_id as attendance_id
    #
    #
    #
    #     """
    #     return select_str
    #
    # def _from(self):
    #     from_str = """
    #             od_sports_attendance_line osal
    #     """
    #     return from_str
    # def _group_by(self):
    #     group_by_str = """
    #         GROUP BY osal.id,
    #             osal.attendance_id
    #
    #     """
    #     return group_by_str
    #
    #




    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
left join od_sports_attendance osa ON (osal.attendance_id= osa.id)
            )""" % (self._table, self._select(), self._from()))


