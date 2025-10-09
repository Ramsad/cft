
# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError


class od_terms(models.Model):
    _name = 'od.terms'

    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Selection([
            ('Term-1','Term-1'),
            ('Term-2','Term-2'),
            ('Term-3','Term-3'),
            ('Summer','Summer'),
        ], string='Term', default='Term-1')

    # 
    # def create(self, vals):
    #     if vals.get('name'):
    #         name_exist = self.env['od.terms'].search([('name','=',vals.get('name'))])
    #         if name_exist:
    #         	raise UserError(_('%s already created')%vals.get('name'))
    #     return super(od_terms, self).create(vals)