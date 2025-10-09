# -*- coding: utf-8 -*-
from odoo.models import expression
from odoo.tools.translate import _
import copy
import math
# from odoo import models, fields, api, _
# from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
import dateutil.relativedelta
from datetime import date, timedelta
import itertools
from lxml import etree
import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError



class orchid_school(models.Model):
    _name = 'orchid.school'
    _description = 'Orchid School'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    

class res_partner(models.Model):
    _inherit = 'res.partner'

    od_age = fields.Integer(string='Age')
    od_gender = fields.Selection([
            ('male','Male'),
            ('female','Female'),
        ], string='Gender', default='male')
    od_dob = fields.Date(string='DOB')
    od_coach = fields.Boolean(string="Coach")
    od_student = fields.Boolean(string="Student")
    od_percent = fields.Float(string="Percentage")
    od_program_count = fields.Integer(compute='_count_program', compute_sudo=True)
    od_collection_count = fields.Integer(compute='_count_collection', compute_sudo=True)
    od_attendance_count = fields.Integer(compute='_count_attendance', compute_sudo=True)
    school_id = fields.Many2one('orchid.school',string='School')
    racket_info = fields.Char(string='Racket Information')
    
#    
#    
#    def name_search(self, name, args=None, operator='ilike', limit=80):
#        args = args or []
#        if operator in expression.NEGATIVE_TERM_OPERATORS:
#            domain = [('mobile', operator, name), ('name', operator, name)]
#        else:
#            domain = ['|', ('mobile', operator, name), ('name', operator, name)]
#        # ids = self.env['res.partner'].search(user, expression.AND([domain, args]), limit=limit)
#        return self.name_get()

#    def name_get(self):
#        if not self._ids:
#            return []
#        reads = self.read(['name','mobile'])
#        res = []
#        for record in reads:
#            name = record['name']
#            if record['mobile']:
#                name = record['mobile']+ ' / ' +name
#            res.append((record['id'],name ))
#        return res

        
    # 
    # def create(self,vals):
    #     if not vals.get('email',False):
    #         raise Warning("Email Is Mandatory in Partner Form")
    #     return super(res_partner,self).create(vals)
    
#
#     def od_btn_open_program(self):
#         partner_id = self.id
#         reg_ids = []
#         if self.od_coach:
#             domain = [('coach_id','=',partner_id)]
#         else:
#             reg_line_obj = self.env['od.registration.line'].search([('partner_id','=',partner_id)])
#             for reg_ln in reg_line_obj:
#                 if reg_ln.activities_id.id not in reg_ids:
#                     reg_ids.append(reg_ln.activities_id.id)
#             domain = [('id','in',reg_ids)]
#         return {
#             'domain':domain,
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'od.activities',
#             'type': 'ir.actions.act_window',
#         }
#
#
#
#
#     def od_btn_open_schedule(self):
#         partner_id = self.id
#         sch_ids = []
#         if self.od_coach:
#             domain = [('coach_id','=',partner_id)]
#         else:
#             sch_line_obj = self.env['od.scheduled.line'].search([('partner_id','=',partner_id)])
#             for sch_ln in sch_line_obj:
#                 if sch_ln.scheduled_id.id not in sch_ids:
#                     sch_ids.append(sch_ln.scheduled_id.id)
#             domain = [('id','in',sch_ids)]
#         return {
#             'domain':domain,
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'od.scheduled',
#             'type': 'ir.actions.act_window',
#         }
#
#
#     # TODO:  removed in newer Odoo; refactor for recordsets
# #
#     def _count_program(self):
#         partner_id = self.id
#
#         objcts = self.env['od.activities'].search([('coach_id','=',partner_id)])
#         self.od_program_count = len(objcts)
#
#
#     def od_btn_open_collection(self):
#         partner_id = self.id
#         rcpt_ids = []
#         if self.od_coach:
#             domain = [('coach_id','=',partner_id)]
#         else:
#             rcpt_line_obj = self.env['od.sports.receipt.line'].search([('partner_id','=',partner_id)])
#             for rcpt_ln in rcpt_line_obj:
#                 if rcpt_ln.receipt_id.id not in rcpt_ids:
#                     rcpt_ids.append(rcpt_ln.receipt_id.id)
#             domain = [('id','in',rcpt_ids)]
#         return {
#             'domain':domain,
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'od.sports.receipt',
#             'type': 'ir.actions.act_window',
#         }
#     # TODO:  removed in newer Odoo; refactor for recordsets
# #
#     def _count_collection(self):
#         partner_id = self.id
#
#         collection = self.env['od.sports.receipt'].search([('coach_id','=',partner_id)])
#         self.od_collection_count = len(collection)
#
#
#
#     def od_btn_open_attendance(self):
#         partner_id = self.id
#         attn_ids = []
#         if self.od_coach:
#             domain = [('coach_id','=',partner_id)]
#         else:
#             attn_line_obj = self.env['od.sports.attendance.line'].search([('partner_id','=',partner_id)])
#             for attn_ln in attn_line_obj:
#                 if attn_ln.attendance_id.id not in attn_ids:
#                     attn_ids.append(attn_ln.attendance_id.id)
#             domain = [('id','in',attn_ids)]
#         return {
#             'domain':domain,
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'od.sports.attendance',
#             'type': 'ir.actions.act_window',
#         }
#     # TODO:  removed in newer Odoo; refactor for recordsets
# #
#     def _count_attendance(self):
#         partner_id = self.id
#
#         attendance = self.env['od.sports.attendance'].search([('coach_id','=',partner_id)])
#         self.od_attendance_count = len(attendance)
#
#
