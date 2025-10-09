# -*- coding: utf-8 -*-
##############################################################################

from odoo import fields, models, api, _
from odoo.tools.translate import _
from odoo.exceptions import UserError, AccessError


class partner_collection_wizard(models.TransientModel):
    _name = 'partner.collection.wizard'
    _description = 'Partner Collection Wizard'

    partner_id = fields.Many2one('res.partner', string='Student Name', onchange="_onchange_partner")
    mobile = fields.Char(string='Mobile Number')
    email = fields.Char(string='Email Address')
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    od_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender', default='male')
    od_age = fields.Integer(string='Age')
    od_dob = fields.Date(string='Dob')
    school_id = fields.Many2one('orchid.school', string='School')
    zip = fields.Char(string='Zip')
    racket_info = fields.Char(string='Racket Info')
    wizard_line_ids = fields.One2many('partner.collection.wizard.line', 'partner_collection_id',
                                      string='Collection Lines')

    def default_get(self, default_fields):
        res = super(partner_collection_wizard, self).default_get(default_fields)
        partner_id = self._context.get('active_ids')
        if len(partner_id) > 1:
            raise UserError(_('Multiple partner not allowed!!'))
        student_obj = self.env['res.partner'].browse(partner_id)
        lines = []
        collection_line_objs = self.env['od.sports.receipt.line'].search([('partner_id', '=', partner_id)])
        for cl_obj in collection_line_objs:
            line = {
                'rv_no': cl_obj.rv_no,
                'total': cl_obj.total,
                'type_id': cl_obj.type_id and cl_obj.type_id.id or False,
                'date': cl_obj.receipt_id and cl_obj.receipt_id.date,
                'no_of_clases': cl_obj.no_of_clases,
                'coach_id': cl_obj.receipt_id and cl_obj.receipt_id.coach_id and cl_obj.receipt_id.coach_id.id or False,
            }
            lines.append((0, 0, line))

        res.update({
            'partner_id': student_obj and student_obj.id,
            'mobile': student_obj.mobile,
            'email': student_obj.email,
            'street': student_obj.street,
            'street2': student_obj.street2,
            'city': student_obj.city,
            'state_id': student_obj.state_id and student_obj.state_id.id or False,
            'country_id': student_obj.country_id and student_obj.country_id.id or False,
            'od_dob': student_obj.od_dob,
            'od_gender': student_obj.od_gender,
            'od_age': student_obj.od_age,
            'school_id': student_obj.school_id and student_obj.school_id.id or False,
            'zip': student_obj.zip,
            'racket_info': student_obj.racket_info,
            'wizard_line_ids': lines
        })
        return res

    def print_report(self):
        datas = {
            'ids': [self.id],
            'model': 'partner.collection.wizard',
            'form': self.read(self)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'orchid_sports_v10.report_partner_collection',
            'report_type': 'qweb',
            'datas': datas,
            'res_model': 'partner.collection.wizard',
            'src_model': 'partner.collection.wizard',
        }


class partner_collection_wizard_line(models.TransientModel):
    """
    Orchid inbound assign wizard.
    """
    _name = 'partner.collection.wizard.line'
    _description = 'Partner Collection Wizard Line'

    rv_no = fields.Char(string='RV no')
    total = fields.Float(string='Amount Paid')
    type_id = fields.Many2one('od.camp.type', string='Type of lesson')
    date = fields.Date(string='Date of payment')
    no_of_clases = fields.Float(string='No. of Lesson Booked')
    coach_id = fields.Many2one('res.partner', string='Coach Name')
    lesson_taken = fields.Float(string='Lesson Taken')
    pending_lesson = fields.Float(string='Pending Lesson')
    partner_collection_id = fields.Many2one('partner.collection.wizard', string='Partner Collection')
