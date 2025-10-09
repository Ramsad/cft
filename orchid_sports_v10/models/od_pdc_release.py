import itertools
from lxml import etree
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
import odoo.addons.decimal_precision as dp
import copy
class od_pdc_release(models.Model):
    
    _name = 'od.pdc.release'
    _description = "od.pdc.Release"
    
    

    def od_open_receipt(self):
        self.line_ids.unlink()
        account_id = self.account_id and self.account_id.id
        sport_line_obj = self.env['od.sports.receipt.line']
        sport_line_ids = sport_line_obj.search([('payment_type_account_id','=',account_id),])
        vals =[]
        for sport_line in sport_line_ids:
            val = {}
            val['rv_no'] = sport_line.rv_no
            val['partner_id'] = sport_line.partner_id
            val['payment_type_account_id'] = sport_line.payment_type_account_id
            val['type_id'] = sport_line.type_id
            val['remarks'] = sport_line.remarks
            val['date'] = sport_line.date
            val['amount'] = sport_line.amount
            val['transportation'] = sport_line.transportation
            val['total'] = sport_line.total
            vals.append(val)
        self.line_ids = vals
        return True

    
    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    account_id = fields.Many2one('account.account', string='Account', required=True)
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    type = fields.Selection([('release','Released'),('unrelease','Unreleased'),('all','All')], string='Type')
    line_ids = fields.One2many('od.sports.receipt.line','release_id', string='PDC Line')
    
    
class od_pdc_release_line(models.Model):
    
    _inherit = 'od.sports.receipt.line'     
    
    release_id = fields.Many2one('od.pdc.release', string='Pdc Release',ondelete='cascade')
    od_account_id = fields.Many2one('account.account', string='Account')
     

    
    
    
    