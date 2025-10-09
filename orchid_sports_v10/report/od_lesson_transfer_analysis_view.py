# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, SUPERUSER_ID, _

class od_lesson_transfer_analysis_view(models.Model):
    _name = "od.lesson.transfer.analysis.view"
    _description = "od.lesson.transfer.analysis.view"
    _auto = False


    od_partner_id = fields.Many2one('res.partner',string='Student')
    od_type_id = fields.Many2one('od.camp.type',string='Fees Type',required=True)
    lesson_id = fields.Many2one('od.lesson.transfer', string='Lesson Transfer')
    od_amount = fields.Float(string='Fees')
    od_no_of_clases = fields.Float(string='Paid Lesson')
    od_transportation = fields.Float(string='Registration')
    venue_id = fields.Many2one('od.venue', string='Venue',)
    old_venue_id = fields.Many2one('od.venue', string='Venue',)
    od_coach_commision = fields.Float(string='Coach Comm.')
    od_trn_amount = fields.Float(string='T.Fees')
    od_trn_no_of_clases = fields.Float(string='T. Lesson No.')
    od_trn_transportation = fields.Float(string='T.Registration')
    receipt_line_id = fields.Many2one('od.sports.receipt.line', string='Collection Line')
    od_new_activities_id = fields.Many2one('od.activities',string="New Program")
    od_trn_coach_comm = fields.Float(string='T. Coach Comm.', store=True)
    od_trn_coach_per = fields.Float(string='T. Coach %')
    od_new_coach_per = fields.Float(string='New Coach %')
    od_new_coach_comm = fields.Float(string='New Coach Comm', store=True)
    date = fields.Date(string='Date')
    name = fields.Char(string='Name', default='/')
    od_activities_id = fields.Many2one('od.activities',string="Program")
    od_term_id = fields.Many2one('od.terms', string='Term')
    state = fields.Selection([
            ('draft','Draft'),
            ('confirm','Confirm'),
            ('cancel','Cancel'),
        ], string='Status', default='draft')
    move_id = fields.Many2one('account.move',string='Journal Number')

    #
    # def _select(self):
    #     select_str = """
    #          SELECT ROW_NUMBER () OVER (ORDER BY oltl.id ) AS id,
    #             oltl.od_partner_id as od_partner_id,
    #             oltl.od_type_id as od_type_id,
    #             oltl.lesson_id as lesson_id,
    #             oltl.od_amount as od_amount,
    #             oltl.od_no_of_clases as od_no_of_clases,
    #             oltl.od_transportation as od_transportation,
    #             oltl.venue_id as venue_id,
    #             oltl.old_venue_id as old_venue_id,
    #             oltl.od_coach_commision as od_coach_commision,
    #             oltl.od_trn_amount as od_trn_amount,
    #             oltl.od_trn_no_of_clases as od_trn_no_of_clases,
    #             oltl.od_trn_transportation as od_trn_transportation,
    #             oltl.receipt_line_id as receipt_line_id,
    #             oltl.od_new_activities_id as od_new_activities_id,
    #             oltl.od_trn_coach_comm as od_trn_coach_comm,
    #             oltl.od_trn_coach_per as od_trn_coach_per,
    #             oltl.od_new_coach_per as od_new_coach_per,
    #             oltl.od_new_coach_comm as od_new_coach_comm,
    #             olt.date as date,
    #             olt.name as name,
    #             olt.od_activities_id as od_activities_id,
    #             olt.od_term_id as od_term_id,
    #             olt.state as state,
    #             olt.move_id
    #
    #     """
    #     return select_str
    #
    # def _from(self):
    #     from_str = """
    #             od_lesson_transfer_line   oltl
    #
    #     """
    #     return from_str
    # def _group_by(self):
    #     group_by_str = """
    #         GROUP BY oltl.id,
    #             oltl.od_partner_id,
    #             oltl.od_type_id,
    #             oltl.lesson_id,
    #             oltl.od_amount,
    #             oltl.od_no_of_clases,
    #             oltl.od_transportation,
    #             oltl.venue_id,
    #             oltl.old_venue_id,
    #             oltl.od_coach_commision,
    #             oltl.od_trn_amount,
    #             oltl.od_trn_no_of_clases,
    #             oltl.od_trn_transportation,
    #             oltl.receipt_line_id,
    #             oltl.od_new_activities_id,
    #             oltl.od_trn_coach_comm,
    #             oltl.od_trn_coach_per,
    #             oltl.od_new_coach_per,
    #             oltl.od_new_coach_comm
    #
    #     """
    #     return group_by_str
    #
    #
    # def init(self):
    #     tools.drop_view_if_exists(self._cr, self._table)
    #     self._cr.execute("""CREATE or REPLACE VIEW %s as (
    #         %s
    #         FROM  %s
    #         left join od_lesson_transfer olt ON (oltl.lesson_id = olt.id)
    #         )""" % (self._table, self._select(), self._from()))
