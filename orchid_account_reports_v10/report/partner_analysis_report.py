# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from odoo import tools

class OrchidPartnerAnalysis(models.Model):
    _name = "orchid.partner.analysis"
    _description = "Orchid Partner Analysis"
    _auto = False
    _rec_name = 'date_maturity'
    _order = 'date_maturity desc'
    balance_cash_basis = fields.Float(string='Balance Cash')
    debit_cash_basis = fields.Float(string='Debit Cash')
    company_currency_id = fields.Many2one('res.currency',string='Company Currency')
    account_id = fields.Many2one('account.account',string='Account')
#    tax_exigible = fields.Float(string='Tax')
    orchid_cc_id =  fields.Many2one('orchid.account.cost.center', string='Cost Center')
    create_uid = fields.Many2one('res.users', string='Created User')
    credit = fields.Float(string='Credit')
    company_id = fields.Many2one('res.company', string='Company')
    credit_cash_basis = fields.Float(string='Credit Cash')
    amount_currency = fields.Float(string='Amount Currency')
    orchid_div_id =  fields.Many2one('orchid.account.division', string='Division')
    date_maturity = fields.Date(string='Date')
    move_id = fields.Many2one('account.move', string='Journal Entry')
    orchid_br_id =  fields.Many2one('orchid.account.branch', string='Branch')
    amount_residual = fields.Float(string='Amount Residual')
    write_date = fields.Datetime(string='Last Updated Date')
    payment_id = fields.Many2one('account.payment', string="Originator Payment",)
    partner_id = fields.Many2one('res.partner', string="Partner",)
    create_date = fields.Datetime(string='Created Date')
    reconciled = fields.Boolean(string='Reconciled')
    amount_residual_currency = fields.Float(string='Amount in Residual')
    invoice_id = fields.Many2one('account.move',string='Invoice')
    od_reconcile_id = fields.Many2one('orchid.bank.reconciliation',string='Bank Reconciled')
    name = fields.Char(string="Journal Entry Line")
    statement_id = fields.Many2one('account.bank.statement', string='Statement')
    line_date = fields.Date(string='Line Date')
    od_reconcile_date = fields.Date(string='Reconcile Date')
    debit = fields.Float(string='Debit')
    journal_id = fields.Many2one('account.journal', string='Journal')
    user_type_id = fields.Many2one('account.account.type', string="User Type")
    line_ref = fields.Char(string="Line Ref")
    currency_id = fields.Many2one('res.currency',string='Line Currency')
#    tax_line_id = fields.Many2one('account.tax', string='Originator tax',)
    full_reconcile_id = fields.Many2one('account.full.reconcile', string="Full Reconcile",)
    write_uid = fields.Many2one('res.users', string='Updated User')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    balance = fields.Float(string='Balance')
    code = fields.Char(string='code')
    internal_type = fields.Char(string='Internal Type')
    ref = fields.Char(string='Journal Entry Ref')
    state = fields.Char(string='Journal Entry State')
    move_name = fields.Char(string='Journal Entry name')
    voucher_date = fields.Date(string='Voucher Date')
    user_id = fields.Many2one('res.users', string='Salesperson')
    country_id = fields.Many2one('res.country', string='Country')
    parent_id = fields.Many2one('res.partner', string='Parent')
    supplier = fields.Boolean(string='Supplier')
    customer = fields.Boolean(string='Customer')
    is_company = fields.Boolean(string='Is Company')
    type = fields.Char(string='Type')
    team_id = fields.Many2one('crm.team', string='Sales Team')
    # od_group_id = fields.Many2one('orchid.partner.group',string="Partner Group")
    # od_sub_group_id = fields.Many2one('orchid.partner.sub.group',string="Partner Sub Group")
    # od_type_id = fields.Many2one('orchid.partner.type',string="Partner Type")
    # od_area_id = fields.Many2one('orchid.partner.area',string="Parner Area")
    inv_ref = fields.Char(string='Invoice Ref')
    inv_number = fields.Char(string='Invoice Number')
    inv_status = fields.Char(string='Invoice Status')
    inv_type = fields.Char(string='Invoice Type')
    ref_doc_inv = fields.Char(string='Invoice ref Doc')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms',)
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position',)
    inv_currency_id = fields.Many2one('res.currency',string='Invoice Currency')
    inv_salesman_id = fields.Many2one('res.users',string='Invoice Salesman')   
    inv_sales_team_id = fields.Many2one('crm.team', string='Invoice Sales Team') 
    
    

 
    
    def init(self):
        cr = self.env.cr   
        tools.drop_view_if_exists(cr, 'orchid_partner_analysis')
        cr.execute("""
            create or replace view orchid_partner_analysis as (
                SELECT row_number() OVER (ORDER BY mvl.id) AS id,
               mvl.balance_cash_basis as balance_cash_basis,
               mvl.debit_cash_basis as debit_cash_basis,
               mvl.company_currency_id as company_currency_id,
               mvl.account_id as account_id,
               mvl.orchid_cc_id as orchid_cc_id,
               mvl.create_uid as create_uid,
               mvl.credit as credit,
               mvl.company_id as company_id,
               mvl.credit_cash_basis as credit_cash_basis,
              mvl.amount_currency as amount_currency,
              mvl.orchid_div_id as orchid_div_id,
              mvl.date_maturity as date_maturity,
              mvl.move_id as move_id,
             mvl.orchid_br_id as orchid_br_id,
             mvl.amount_residual as amount_residual,
            mvl.write_date as write_date,
            mvl.payment_id as payment_id,
            mvl.partner_id as partner_id,
            mvl.create_date as create_date,
            mvl.reconciled as reconciled,
            mvl.amount_residual_currency as amount_residual_currency,
            mvl.invoice_id as invoice_id,
            mvl.od_reconcile_id as od_reconcile_id,
            mvl.name as name,
            mvl.statement_id as statement_id,
            mvl.date as line_date,
            mvl.od_reconcile_date as od_reconcile_date,
            mvl.debit as debit,
            mvl.journal_id as journal_id,
            mvl.user_type_id as user_type_id,
            mvl.ref as line_ref,
            mvl.currency_id as currency_id,
            mvl.tax_line_id as tax_line_id,
            mvl.full_reconcile_id as full_reconcile_id,
            mvl.write_uid as write_uid,
            mvl.analytic_account_id as analytic_account_id,
            mvl.balance as balance, 
            acc.code as code,
            acc.internal_type as internal_type,
            mv.ref as ref,
            mv.state as state,
            mv.name as move_name,
            mv.date as voucher_date,
            ptr.user_id AS user_id,
            ptr.country_id as country_id,
            ptr.parent_id as parent_id,
            ptr.supplier as supplier,
            ptr.customer as customer,
            ptr.is_company as is_company,
            ptr.type as type,
            ptr.team_id AS team_id,
--            ptr.od_group_id as od_group_id,
--            ptr.od_type_id as od_type_id,
--            ptr.od_sub_group_id as od_sub_group_id,
            inv.reference AS inv_ref,
            inv.number AS inv_number,
            inv.state AS inv_status,
            inv.type AS inv_type,
            inv.origin AS ref_doc_inv,
            inv.payment_term_id as payment_term_id,
            inv.fiscal_position_id as fiscal_position_id,
            inv.currency_id AS inv_currency_id,
            inv.user_id AS inv_salesman_id,
            inv.team_id AS inv_sales_team_id
                FROM account_move_line mvl
                LEFT JOIN account_move mv ON mvl.move_id = mv.id
                LEFT JOIN res_partner ptr ON mvl.partner_id = ptr.id
                LEFT JOIN account_account acc ON mvl.account_id = acc.id
                LEFT JOIN account_payment pay ON mvl.payment_id = pay.id
                LEFT JOIN account_invoice inv ON mvl.invoice_id = inv.id


            )
        """)
