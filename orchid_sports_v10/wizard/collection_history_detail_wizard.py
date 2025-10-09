# -*- coding: utf-8 -*-
##############################################################################

from odoo import fields,models,api,_
from odoo.tools.translate import _
from odoo.exceptions import UserError, AccessError

class collection_history_detail_wizard(models.TransientModel):
    _name = "collection.history.detail.wizard"
    _description = "Collection Detail"

    wizard_line = fields.One2many('collection.history.detail.wizard.line','wizard_id',string="Wizard Line")
    amount_total = fields.Float(string='Amount Total')

    # 
    # def default_get(self, fields):
    #     res = super(collection_history_detail_wizard, self).default_get(fields)
    #
    #     active_model = self._context.get('active_model', False) or False
    #     active_ids = self._context.get('active_ids', []) or []
    #     print("AAAAAAAAAAAAA",active_ids,active_model)
    #     reciept_line_id = active_ids
    #     receipt_line_obj = self.env['od.sports.receipt.line'].browse(reciept_line_id)
    #
    #     reciept_id = receipt_line_obj.receipt_id and receipt_line_obj.receipt_id.id
    #     receipt_obj = self.env['od.sports.receipt'].browse(reciept_id)
    #     activity_id = receipt_obj.activities_id and receipt_obj.activities_id.id
    #     term_id = receipt_obj.term_id and receipt_obj.term_id.id
    #     student_id = receipt_line_obj.partner_id and receipt_line_obj.partner_id.id
    #     print("2222222222222222222222222222222222student_id",student_id)
    #     type_id = receipt_line_obj.type_id and receipt_line_obj.type_id.id
    #     old_collection_ids = self.env['od.sports.receipt'].search([('term_id','=',term_id),('activities_id','=',activity_id)])
    #     print("ccccccccccccccccccccccccccccold_collection_ids",old_collection_ids)
    #     previous_data =[]
    #
    #     if not old_collection_ids:
    #         raise UserError(_('no previous collections found'))
    #     for collection in old_collection_ids:
    #         #collection_line_ids = self.env['od.sports.receipt.line'].search([('type_id','=',type_id),('partner_id','=',student_id),('receipt_id','=',collection.id)])
    #         collection_line_ids = self.env['od.sports.receipt.line'].search([('receipt_id','=',collection.id)])
    #         print(collection_line_ids)
    #         print('KKKKKKKKKKKKKKKKKKKKKKKKLLLLLL',type_id,student_id,collection.id)
    #         # collection_obj = self.env['od.sports.receipt.line'].browse(collection_line_ids.id)
    #         # print collection_obj
    #         for val in collection_line_ids:
    #             print("333333333333333333333333333val.partner_id and val.partner_id.id",val.partner_id and val.partner_id.id)
    #             if val.partner_id and val.partner_id.id == student_id:
    #                 values = {'receipt_id':val.receipt_id and val.receipt_id.id,
    #                 'rv_no':val.rv_no,
    #                 'partner_id':val.partner_id and val.partner_id.id,
    #                 'amount':val.amount,
    #                 'transportation':val.transportation,
    #                 'total':val.total,
    #                 'payment_type_account_id':val.payment_type_account_id and val.payment_type_account_id.id,
    #                 'remarks':val.remarks,
    #                 'date':val.date,
    #                 'type_id':val.type_id and val.type_id.id,
    #                 'receipt_date':collection.date
    #                 }
    #                 previous_data.append((0,0,values))
    #
    #     res.update({'amount_total': 200,'wizard_line':previous_data})
    #     return res


class collection_history_detail_wizard_line(models.TransientModel):
    _name = "collection.history.detail.wizard.line"
    _description = "Collection Detail Line"
    
    wizard_id = fields.Many2one('collection.history.detail.wizard', string='Wizard')
    receipt_id = fields.Many2one('od.sports.receipt', string='Sports Receipt',ondelete='cascade')
    
    rv_no = fields.Char(string='RV/Number',)
    partner_id = fields.Many2one('res.partner',string='Student',)
    amount = fields.Float(string='Fees')
    transportation = fields.Float(string='Registration')
    total = fields.Float(string='Total',store=True,readonly=True,)
    payment_type_account_id = fields.Many2one('account.account',string='Account',domain=[('type', 'in', ['liquidity'])])
    remarks = fields.Char(string='Cheque No')
    date = fields.Date(string="Cheque Date") 
    receipt_date = fields.Date(string="Date")      
    type_id = fields.Many2one('od.camp.type',string='Type')        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
