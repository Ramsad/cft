# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, SUPERUSER_ID, _

class od_activity_analysis_view(models.Model):
    _name = "od.activity.analysis.view"
    _description = "od.activity.analysis.view"
    _auto = False
    _rec_name = 'name'

    venue_id = fields.Many2one('od.venue',string='Venue')
    coach_id = fields.Many2one('res.partner',string='Coach')
    fees = fields.Float(string='Fees')
    no_of_class = fields.Float('Number Of Class')
    manager_id = fields.Many2one('res.partner',string='Manager')
    academy_id = fields.Many2one('res.partner',string='Academy')
    cost_centre_id = fields.Many2one('orchid.account.cost.center',string='Cost Centre')
    division_id = fields.Many2one('od.cost.division','Division')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    name = fields.Char('Activity')

    product_id = fields.Many2one('product.product','Term')
    academy_percentage = fields.Float(string='Academy(%)')
    coach_percentage = fields.Float(string='Coach(%)')
    amount = fields.Float('Amount')
    academy_amount = fields.Float('Academy Amount')
    coach_amount = fields.Float('Coach Amount')
    attendance = fields.Float('Attendance')
    utilized = fields.Float('Utilized')
    balance = fields.Float('Balance')




#     def _select(self):
#         select_str = """
#              SELECT ROW_NUMBER () OVER (ORDER BY od_activities.id ) AS id,
# 	od_activities.venue_id as venue_id,
# 	od_activities.coach_id as coach_id,
# 	od_activities.fees as fees,
# 	od_activities.no_of_class as no_of_class,
# 	od_activities.manager_id as manager_id,
# 	od_activities.academy_id as academy_id,
# 	-- od_cost_centre.division_id as division_id,
# 	od_activities.cost_centre_id as cost_centre_id,
# 	od_activities.start_date as start_date,
# 	od_activities.end_date as end_date,
# 	od_activities.name as name,
# 	od_activities.product_id as product_id,
# 	od_activities.academy_percentage as academy_percentage,
# 	od_activities.coach_percentage as coach_percentage,
# 	od_collection_sum_view.amount as amount,
# 	((od_collection_sum_view.amount * od_activities.academy_percentage)/100) AS academy_amount,
# 	((od_collection_sum_view.amount * od_activities.coach_percentage)/100) AS coach_amount,
# 	od_attendance_total_view.attendance as attendance,
# 	((od_activities.fees/od_activities.no_of_class)*od_attendance_total_view.attendance) AS utilized,
# 	(od_collection_sum_view.amount-((od_activities.fees/od_activities.no_of_class)*od_attendance_total_view.attendance)) AS balance
#
#
#
#         """
#
#         return select_str
#
#     def _from(self):
#         from_str = """
#                 od_activities
#         """
#         return from_str
#     def _group_by(self):
#         group_by_str = """
# GROUP BY  od_activities.id,
# od_activities.venue_id,
# 	od_activities.coach_id,
# 	od_activities.fees,
# 	od_activities.no_of_class,
# 	od_activities.manager_id,
# 	od_activities.academy_id,
# 	-- od_cost_centre.division_id,
# 	od_activities.cost_centre_id,
# 	od_activities.start_date,
# 	od_activities.end_date,
# 	od_activities.name,
# 	od_activities.product_id,
# 	od_activities.academy_percentage,
# 	od_activities.coach_percentage,
# 	od_collection_sum_view.amount,
# 	od_attendance_total_view.attendance
#
#
#         """
#         return group_by_str



  #
  #
  #
  #   def init(self):
  #       tools.drop_view_if_exists(self._cr, self._table)
  #       self._cr.execute("""CREATE or REPLACE VIEW %s as (
  #           %s
  #           FROM  %s
	# -- LEFT JOIN od_cost_centre ON od_cost_centre.id=od_activities.cost_centre_id
	# LEFT JOIN od_collection_sum_view  ON od_collection_sum_view.activities_id=od_activities.id
	# LEFT JOIN od_attendance_total_view  ON od_attendance_total_view.activities_id=od_activities.id
  # %s
  #           )""" % (self._table, self._select(), self._from() ,self._group_by()))
  #
  #
  #
  #
  #
  #

