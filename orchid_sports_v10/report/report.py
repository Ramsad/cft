# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, SUPERUSER_ID, _

class orchid_receipt_summary_report_view(models.Model):
    _name = "orchid.receipt.summary.report.view"
    _description = "orchid.receipt.summary.report.view"
    _auto = False
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner',string='Student')
    fee = fields.Float(string='Fee')
    classes = fields.Float(string='No.Of Classes')
    registartion = fields.Float(string='Registartion')
    activities_id = fields.Many2one('od.activities',string='Program')
    term_id = fields.Many2one('od.terms', string='Term')
    

    #
    # 
    # def init(self):
    # 	cr = self.env.cr
    #     tools.drop_view_if_exists(cr, 'orchid_receipt_summary_report_view')
    #     cr.execute("""
    #         create or replace view orchid_receipt_summary_report_view as (
    #             SELECT
    #         partner_id AS partner_id,
    #         SUM(amount) AS fee,
    #         SUM(no_of_clases) AS classes,
    #         SUM(transportation) AS registartion,
    #         activities_id as activities_id,
    #         term_id as term_id
    #         FROM od_sports_receipt_line
    #         LEFT JOIN od_sports_receipt ON od_sports_receipt_line.receipt_id=od_sports_receipt.id
    #
    #         GROUP BY  partner_id,activities_id,term_id
    #         )
    #     """)
    #

#    def _select(self):
#        select_str = """
#             SELECT ROW_NUMBER () OVER (ORDER BY od_sports_receipt_line.id ) AS id,
#            partner_id AS partner_id, 
#            SUM(amount) AS fee,
#            SUM(no_of_clases) AS classes,
#            SUM(transportation) AS registartion,
#            activities_id as activities_id,
#            term_id as term_id



#        """

#        return select_str

#    def _from(self):
#        from_str = """
#                od_sports_receipt_line
#        """
#        return from_str
#    def _group_by(self):
#        group_by_str = """
#GROUP BY  partner_id,activities_id,term_id,od_sports_receipt_line.id

#                   
#        """
#        return group_by_str        






#    def init(self):
#        tools.drop_view_if_exists(self._cr, self._table)
#        self._cr.execute("""CREATE or REPLACE VIEW %s as (
#            %s
#            FROM  %s 
#LEFT JOIN od_sports_receipt ON od_sports_receipt_line.receipt_id=od_sports_receipt.id
#  %s
#            )""" % (self._table, self._select(), self._from() ,self._group_by()))





class orchid_attendance_summary_report_view(models.Model):
    _name = "orchid.attendance.summary.report.view"
    _description = "orchid.attendance.summary.report.view"
    _auto = False
    _rec_name = 'partner_id'
    
    partner_id = fields.Many2one('res.partner',string='Student')

    classes = fields.Float(string='No.Of Classes')
    
    abst = fields.Float(string='Abst')
    attnd = fields.Float(string='Attnd')
    activities_id = fields.Many2one('od.activities',string='Program')  
    term_id = fields.Many2one('od.terms', string='Term')
    
    


    #
    # fee = fields.Float(string='Fee')
    # 
    # def init(self):
    # 	cr = self.env.cr
    #     tools.drop_view_if_exists(cr, 'orchid_attendance_summary_report_view')
    #     cr.execute("""
    #         create or replace view orchid_attendance_summary_report_view as (
    #             SELECT
    #             foo.student as partner_id,
    #             sum(foo.classes) as classes,
    #             sum(foo.abst) as abst,
    #             sum(foo.attnd) AS attnd,
    #             foo.activities_id as activities_id,
    #             foo.term_id as term_id
    #             FROM (SELECT
    #             partner_id AS student,
    #             count(jv) AS classes,
    #             CASE WHEN jv=TRUE
    #             THEN count(jv)
    #             ELSE 0
    #             END AS abst,
    #             CASE WHEN jv=FALSE
    #             THEN count(jv)
    #             ELSE 0
    #         END AS attnd,
    #         activities_id,
    #         term_id
    #         FROM od_sports_attendance_line
    #         LEFT JOIN od_sports_attendance ON od_sports_attendance_line.attendance_id=od_sports_attendance.id
    #         GROUP BY partner_id,activities_id,term_id,jv ) foo
    #         GROUP BY
    #         foo.student,
    #         foo.classes,
    #     foo.activities_id,
    #     foo.term_id
    #
    #         )
    #     """)
    #
    #
    #
    #
    #
    #



class orchid_schedule_summary_report_view(models.Model):
    _name = "orchid.schedule.summary.report.view"
    _description = "orchid.schedule.summary.report.view"
    _auto = False
    _rec_name = 'partner_id'
    
    partner_id = fields.Many2one('res.partner',string='Student')

    classes = fields.Float(string='No.Of Classes')
    
    activities_id = fields.Many2one('od.activities',string='Program')  
    term_id = fields.Many2one('od.terms', string='Term')
    
    
#
#
#
#     
#     def init(self):
#     	cr = self.env.cr
#         tools.drop_view_if_exists(cr, 'orchid_schedule_summary_report_view')
#         cr.execute("""
#             create or replace view orchid_schedule_summary_report_view as (
#                 SELECT
# partner_id AS partner_id,
# sum(no_of_classes) AS classes,
# activities_id as activities_id,
# term_id as term_id
# FROM od_scheduled_line
# LEFT JOIN od_scheduled ON od_scheduled_line.scheduled_id=od_scheduled.id
# GROUP BY partner_id,activities_id,term_id
#
#             )
#         """)
#
#
#
#
#
#
        
        
        
        
        
        
        
class orchid_sports_master_report_view(models.Model):
    _name = "orchid.sports.master.report.view"
    _description = "orchid.sports.master.report.view"
    _auto = False
    _rec_name = 'partner_id'
    
    partner_id = fields.Many2one('res.partner',string='Student')
    name = fields.Char(string='Program')
    fee = fields.Float(string='Fee')

    classes = fields.Float(string='No.Of Classes')
    registartion = fields.Float(string='Registartion') 
    activities_id = fields.Many2one('od.activities',string='Receipt Program')   
    term_id = fields.Many2one('od.terms', string='Receipt Term') 
    sch_classes = fields.Float(string='Sch.Classes') 
    sch_activities_id = fields.Many2one('od.activities',string='Sch.Program')     
    sch_term_id = fields.Many2one('od.terms', string='Sch.Term')
    classes_done = fields.Float(string='Classes Done')
    abst = fields.Float(string='Abst')
    attnd = fields.Float(string='Attnd')
    att_activities_id = fields.Many2one('od.activities',string='Att.Program')     
    att_term_id = fields.Many2one('od.terms', string='Att.Term')     
    
   
    
    


#
#     
#     def init(self):
#     	cr = self.env.cr
#         tools.drop_view_if_exists(cr, 'orchid_sports_master_report_view')
#         cr.execute("""
#             create or replace view orchid_sports_master_report_view as (
#                  SELECT row_number() OVER () AS id,
# receipt.partner_id as partner_id,
# actv.name as name,
# sum(receipt.fee) as fee,
# sum(receipt.classes) AS classes,
# sum(receipt.registartion) as registartion,
# receipt.activities_id AS activities_id,
# receipt.term_id AS term_id,
# schedule.classes as sch_classes,
# schedule.activities_id AS sch_activities_id,
# schedule.term_id AS sch_term_id,
# attendance.classes as classes_done,
# attendance.abst as abst,
# attendance.attnd as attnd,
# attendance.activities_id AS att_activities_id,
# attendance.term_id AS att_term_id
#  from od_activities actv
# LEFT JOIN orchid_receipt_summary_report_view receipt ON actv.id= receipt.activities_id
# LEFT JOIN orchid_schedule_summary_report_view schedule ON actv.id=schedule.activities_id AND receipt.term_id=schedule.term_id
# LEFT JOIN orchid_attendance_summary_report_view attendance on actv.id=attendance.activities_id AND receipt.term_id=attendance.term_id
# GROUP BY
# actv.id,
# receipt.partner_id,
# receipt.fee,
# receipt.classes,
# receipt.registartion,
# receipt.activities_id ,
# receipt.term_id ,
# schedule.classes ,
# schedule.activities_id,
# schedule.term_id,
# attendance.classes ,
# attendance.abst,
# attendance.attnd,
# attendance.activities_id,
# attendance.term_id
#
#             )
#         """)
#
#
        
        
        
        
        
       











#----------------------------------------------------

#-------attendance_summary
#SELECT
#foo.student,
#sum(foo.classes) as classes,
#sum(foo.abst) as abst,
#sum(foo.attnd) AS attnd,
#foo.activities_id,
#foo.term_id
#FROM (SELECT
#partner_id AS student,
#count(jv) AS classes,
#CASE WHEN jv=TRUE
#THEN count(jv)
#ELSE 0
#END AS abst,
#CASE WHEN jv=FALSE
#THEN count(jv)
#ELSE 0
#END AS attnd,
#activities_id,
#term_id
#FROM od_sports_attendance_line 
#LEFT JOIN od_sports_attendance ON od_sports_attendance_line.attendance_id=od_sports_attendance.id
#GROUP BY partner_id,activities_id,term_id,jv ) foo
#GROUP BY 
#foo.student,
#foo.classes,
#foo.activities_id,
#foo.term_id

#-------schedule_summary
#SELECT
#partner_id AS student, 
#sum(no_of_classes) AS classes,
#activities_id,
#term_id
#FROM od_scheduled_line 
#LEFT JOIN od_scheduled ON od_scheduled_line.scheduled_id=od_scheduled.id
#GROUP BY partner_id,activities_id,term_id
