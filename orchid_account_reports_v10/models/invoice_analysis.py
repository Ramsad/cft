# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from odoo import tools




# OrchidAccountInvoiceCost
class OrchidAccountInvoiceCost(models.Model):
    _name = "orchid.account.move.cost"
    _description = "Orchid Account Invoice Cost"
    _auto = False
    _order = "id ASC"

    inv_id = fields.Many2one('account.move',string="Invoice")
    product_id = fields.Many2one('product.product',string="Product")
    quantity = fields.Float(string="Quantity")
    cost = fields.Float(string="Cost")
   
    # 
    # def init(self):
    #     cr = self.env.cr
    #     tools.drop_view_if_exists(cr, 'orchid_account_invoice_cost')
    #     cr.execute("""
    #         create or replace view orchid_account_invoice_cost as (
    #             SELECT row_number() OVER (ORDER BY inv.id) AS id,
    #                 inv.id AS inv_id,
    #                 mvl.product_id,
    #                 mvl.quantity,
    #                 CASE
    #                     WHEN ((inv.type)::text = 'out_invoice'::text) THEN (sum(mvl.debit)/sum(mvl.quantity))
    #                     WHEN ((inv.type)::text = 'out_refund'::text) THEN ((sum(mvl.credit)/sum(mvl.quantity) )* ('-1'::integer)::numeric)
    #                     ELSE (0)::numeric
    #                 END AS cost
    #             FROM (((account_move_line mvl
    #              JOIN account_account acc ON ((mvl.account_id = acc.id)))
    #              JOIN account_account_type typ ON ((acc.user_type_id = typ.id)))
    #              JOIN account_invoice inv ON ((inv.move_id = mvl.move_id)))
    #             WHERE (((typ.name)::text = 'Cost of Revenue'::text) AND ((inv.type)::text = ANY ((ARRAY['out_invoice'::character varying, 'out_refund'::character varying])::text[])))
    #             GROUP BY inv.type, inv.id, mvl.product_id,mvl.quantity
    #         )
    #     """)

# OrchidAccountInvoiceReport
class OrchidAccountInvoiceReport(models.Model):
    _name = "orchid.account.move.report"
    _description = "Orchid Account Invoice Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    number = fields.Char(string='Invoice', readonly=True)
    name = fields.Char(string='Reference', readonly=True)
    date = fields.Date(readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_qty = fields.Float(string='Product Quantity', readonly=True)
    uom_name = fields.Char(string='Reference UoM', readonly=True)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', readonly=True)
    fiscal_position_id = fields.Many2one('account.fiscal.position',  string='Fiscal Position', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    commercial_partner_id = fields.Many2one('res.partner', string='Partner Company', help="Commercial Entity")
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    price_total = fields.Float(string='Invoice Price', readonly=True)
    price_average = fields.Float(string='Average Price', readonly=True, group_operator="avg")
    currency_rate = fields.Float(string='Currency Rate', readonly=True)
    nbr = fields.Integer(string='# of Lines', readonly=True)  # TDE FIXME master: rename into nbr_lines
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Refund'),
        ], readonly=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('paid', 'Done'),
        ], string='Invoice Status', readonly=True)
    date_due = fields.Date(string='Due Date', readonly=True)
    account_id = fields.Many2one('account.account', string='Account', readonly=True, domain=[('deprecated', '=', False)])
    account_line_id = fields.Many2one('account.account', string='Account Line', readonly=True, domain=[('deprecated', '=', False)])
    partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Account', readonly=True)
    residual = fields.Float(string='Un Paid', readonly=True)
    residual_local = fields.Float(string="Un Paid (LC)")
    paid_amount = fields.Float(string="Paid")
    country_id = fields.Many2one('res.country', string='Country of the Partner Company')
    weight = fields.Float(string='Gross Weight', readonly=True)
    volume = fields.Float(string='Volume', readonly=True)
    # orchid_brand_id =  fields.Many2one('orchid.product.brand', string='Brand', readonly=True)
    # orchid_type_id =  fields.Many2one('orchid.product.type', string='Product Type', readonly=True)
    # orchid_sub_type_id =  fields.Many2one('orchid.product.sub.type', string='Sub Type', readonly=True)
    # orchid_group_id =  fields.Many2one('orchid.product.group', string='Group', readonly=True)
    # orchid_sub_group_id =  fields.Many2one('orchid.product.sub.group', string='Sub Group', readonly=True)
    # orchid_class_id =  fields.Many2one('orchid.product.classification', string='Classification', readonly=True)
    orchid_country_id = fields.Many2one('res.country', string='Country Of Origin', readonly=True)
    # orchid_hscode_id = fields.Many2one('orchid.product.hscode', string='HS Code', readonly=True)
    cost = fields.Float(string='Cost', readonly=True)
    profit = fields.Float(string='Profit', readonly=True)
    state_id = fields.Many2one('res.country.state',string='Emirates')
#
#     
#     def init(self):
#         cr = self.env.cr
#         tools.drop_view_if_exists(cr, 'orchid_account_invoice_report')
#         cr.execute("""
#             create or replace view orchid_account_invoice_report as (
#                 SELECT
#                     inv.number,
#                     inv.name,
#                     rpt.id,
#                     rpt.date,
#                     rpt.product_id,
#                     rpt.partner_id,
#                     rpt.country_id,
#                     rpt.account_analytic_id,
#                     rpt.payment_term_id,
#                     rpt.uom_name,
#                     rpt.currency_id,
#                     rpt.journal_id,
#                     rpt.fiscal_position_id,
#                     rpt.user_id,
#                     rpt.company_id,
#                     rpt.nbr,
#                     rpt.type,
#                     rpt.state,
#                     rpt.weight,
#                     rpt.volume,
#                     rpt.categ_id,
#                     rpt.date_due,
#                     rpt.account_id,
#                     rpt.account_line_id,
#                     rpt.partner_bank_id,
#                     rpt.product_qty,
#                     rpt.currency_rate,
#                     rpt.price_total,
#                     rpt.price_average,
#                    case when (rpt.price_total > 0) then rpt.residual
#
#                    else (rpt.residual*(-1)) end AS residual,
#                     rpt.commercial_partner_id,
#
# --                    tmpl.orchid_group_id,
# --                    tmpl.orchid_country_id,
# --                    tmpl.orchid_hscode_id,
# --                    tmpl.orchid_brand_id,
# --                    tmpl.orchid_sub_group_id,
# --                    tmpl.orchid_type_id,
# --                    tmpl.orchid_class_id,
# --                    tmpl.orchid_sub_type_id,
#                    case when (rpt.price_total > 0) then (rpt.price_total - rpt.residual)
#
#                    else (rpt.price_total + rpt.residual) end AS paid_amount,
#                    cst.cost * ivl.quantity AS cost,
#
#                     rpt.price_total - (cst.cost * ivl.quantity) AS profit,
#                     resp.state_id as state_id
#
#                 FROM account_invoice_report rpt
#                 LEFT JOIN account_invoice_line ivl ON rpt.id = ivl.id
#                 LEFT JOIN account_invoice inv ON ivl.invoice_id = inv.id
#                 LEFT JOIN res_partner resp ON inv.partner_id = resp.id
#                 LEFT JOIN orchid_account_invoice_cost cst ON ivl.invoice_id = cst.inv_id
#                     and ivl.product_id = cst.product_id
#                     and ivl.quantity = cst.quantity
#                 LEFT JOIN product_product prd ON rpt.product_id = prd.id
# --                LEFT JOIN product_template tmpl ON prd.product_tmpl_id = tmpl.id
#                 WHERE rpt.type IN ('out_invoice','out_refund') AND rpt.state IN ('open','paid')
#             )
#         """)


