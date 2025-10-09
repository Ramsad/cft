# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, SUPERUSER_ID, _

class od_sports_attenadance_analysis_view(models.Model):
    _name = "od.sports.attenadance.analysis.view"
    _description = "od.sports.attenadance.analysis.view"
    _auto = False
    _rec_name = 'partner_id'
    provision_move_id = fields.Many2one('account.move',string='Provision Journal',readonly=True)
    booking_move_id = fields.Many2one('account.move',string='Booking Journal',readonly=True)
    name = fields.Char(string='Name')
    date = fields.Date('Date',)
    od_scheduled = fields.Many2one('od.scheduled',string='Schedule')     
    activities_id = fields.Many2one('od.activities',string='Program')
    venue_id = fields.Many2one('od.venue', string='Venue', readonly=True,)   
    cost_centre_id = fields.Many2one('orchid.account.cost.center',string='Cost Centre')    
        
    date_from = fields.Float(string="Date From")
    date_to = fields.Float(string="Date To")
    duration = fields.Float(string="Duration",)
    term_id = fields.Many2one('od.terms', string='Term')

    move_id = fields.Many2one('account.move',string='Journal Number',readonly=True)


    state = fields.Selection([
            ('draft','Draft'),
            ('confirm','Confirm'),
            ('cancel','Cancel'),
        ], string='Status', default='draft')

    mobile_no = fields.Char(string='Mobile No', readonly=True,)
    partner_id = fields.Many2one('res.partner',string='Student',required=True)
    type_id = fields.Many2one('od.camp.type',string='Type',required=True)
    fees = fields.Float(string='Fees')
    remarks = fields.Char(string='Remarks')
    jv = fields.Boolean(string='Absend')
#    booked_lesson = fields.Float(string="Booked Lesson")
    no_of_lesson = fields.Float(string="Number Of Lesson") 
#    pending_lesson = fields.Float(string="Pending Lesson")  
    day = fields.Char(string="Day")  
    coach_id = fields.Many2one('res.partner',string='Coach') 
    
    
                    

#
#     def _select(self):
#         select_str = """
#              SELECT ROW_NUMBER () OVER (ORDER BY osal.id ) AS id,
#                 osa.name as name,
#                 osa.provision_move_id as provision_move_id,
#                 osa.booking_move_id as booking_move_id,
#                 osa.date as date,
#                 osa.od_scheduled as od_scheduled,
#                 osa.activities_id as activities_id,
#                 osa.venue_id as venue_id,
#                 osa.cost_centre_id as cost_centre_id,
#                 osa.date_from as date_from,
#                 osa.date_to as date_to,
#                  osa.duration as duration,
#                  osa.term_id as term_id,
#                  osa.move_id as move_id,
#                  osa.coach_id as coach_id,
#                  osa.state as state,
#                  osal.jv as jv,
#                  osal.remarks as remarks,
#                  osal.fees as fees,
#                  osal.type_id as type_id,
#                  osal.partner_id as partner_id,
#                  osal.mobile_no as mobile_no,
#                  osa.day as day,
#
#                  osl.no_of_classes as no_of_lesson
#
#
#
#         """
#         return select_str
#
#     def _from(self):
#         from_str = """
#                 od_sports_attendance_line osal
#                 left join res_partner p on (osal.partner_id = p.id)
#
#         """
#         return from_str
#     def _group_by(self):
#         group_by_str = """
#             GROUP BY osal.id,
#                 osa.name,
#                 osa.provision_move_id,
#                 osa.booking_move_id,
#                 osa.date,
#                 osa.od_scheduled,
#                 osa.activities_id,
#                 osa.venue_id,
#                 osa.cost_centre_id,
#                 osa.day,
#                 osa.coach_id,
#                 osa.date_from,
#                 osa.date_to,
#                  osa.duration,
#                  osa.term_id,
#                  osa.move_id,
#                  osa.state,
#                  osal.jv,
#                  osal.remarks,
#                  osal.fees,
#                  osal.type_id,
#                  osal.partner_id,
#                  osal.mobile_no,
#                  osl.no_of_classes
#
#
#         """
#         return group_by_str
#
#
#
#
#
#
#     def init(self):
#         tools.drop_view_if_exists(self._cr, self._table)
#         a = """CREATE or REPLACE VIEW %s as (
#             %s
#             FROM  %s
# left join od_sports_attendance osa ON (osal.attendance_id= osa.id)
#                 left join od_scheduled os on (osa.od_scheduled = os.id)
#                 left join od_scheduled_line osl on (os.id = osl.scheduled_id)
#             )""" % (self._table, self._select(), self._from())
#
#
#         self._cr.execute("""CREATE or REPLACE VIEW %s as (
#             %s
#             FROM  %s
# left join od_sports_attendance osa ON (osal.attendance_id= osa.id)
#                 left join od_scheduled os on (osa.od_scheduled = os.id)
#                 left join od_scheduled_line osl on (os.id = osl.scheduled_id)
#             )""" % (self._table, self._select(), self._from()))
