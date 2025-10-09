# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


# 
# class PartnerArea(models.Model):
#     _name = "orchid.partner.area"
#     name = fields.Char(string='Name')
#     description = fields.Text(string='Desc')  

class AccountPaymentAnalysis(models.Model):
    _name = "account.payment.analysis"
    _description = "Payment Analysis"
    _auto = False


    name = fields.Char(readonly=True, copy=False, default="Draft Payment") # The name is attributed upon post()
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled')], readonly=True, default='draft', copy=False, string="Status")

    payment_type = fields.Char(string='Payment Type')
    partner_type = fields.Char(string='Partner Type')
    journal_id = fields.Many2one('account.journal', string='Payment Journal')
    od_check_no = fields.Char(string='Check No')
    od_check_date = fields.Date(string='Check Date')
    amount = fields.Float(string='Amount')
    payment_date = fields.Date(string='Payment Date')
    od_bank_account = fields.Many2one('account.account', string="Bank Account")
    is_clearing = fields.Boolean(string="Clearing")
    od_released = fields.Boolean(string="Released")
    is_group = fields.Boolean(string="Group Pay")
    payment_transaction_id = fields.Many2one('account.payment', string='Payment Transaction')
    partner_id = fields.Many2one('res.partner', string='Partner')
#    od_group_id = fields.Many2one('orchid.partner.group', string='Group')
#    od_type_id = fields.Many2one('orchid.partner.type', string='Type')
#    od_area_id = fields.Many2one('orchid.partner.area', string='Area')
    user_id = fields.Many2one('res.users', string='Salesman')
    currency_id = fields.Many2one('res.currency', string='Currency')
    company_id = fields.Many2one('res.company', string='Company')       

    _order = 'payment_date desc'
 
    
    def init(self):
        cr = self.env.cr   
        tools.drop_view_if_exists(cr, 'account_payment_analysis')
        cr.execute("""
            create or replace view account_payment_analysis as (
                SELECT row_number() OVER (ORDER BY ap.id) AS id,ap.name as name, ap.state as state, ap.payment_type as payment_type, ap.partner_type as partner_type, ap.journal_id as journal_id,
                ap.od_check_no as od_check_no, ap.od_check_date as od_check_date, ap.amount as amount, ap.date as payment_date,
                ap.od_bank_account as od_bank_account, ap.is_clearing as is_clearing, ap.od_released as od_released, ap.is_group as is_group, ap.payment_transaction_id as payment_transaction_id, ap.partner_id as partner_id,rp.user_id as user_id,ap.currency_id as currency_id,ap.company_id as company_id
                FROM account_payment ap
                LEFT JOIN res_partner rp ON rp.id = ap.partner_id
                GROUP BY ap.id,ap.name, ap.state, ap.payment_type, ap.partner_type, ap.journal_id,
                ap.od_check_no, ap.od_check_date, ap.amount, ap.date,
                ap.od_bank_account,ap.is_clearing,ap.od_released,ap.is_group, ap.payment_transaction_id, ap.partner_id,rp.user_id,ap.company_id,ap.currency_id


            )
        """)

