from odoo import models,api,fields


class PurchaseLine(models.Model):
    _inherit = "purchase.order.line"

    od_tax_amount = fields.Float(string="Tax Amount",readonly=True,store=True)
    od_net_amount = fields.Float(string="Total",readonly=True,store=True)


	#
	# @api.depends('taxes_id','price_subtotal')
	# def compute_taxes_amount(self):
	# 	sum=0
	# 	for tax in self.taxes_id:
	# 		sum=sum+(tax.amount*self.price_subtotal)/100
	# 	self.od_tax_amount=sum
	#
	#
	#
	# @api.depends('od_tax_amount','price_subtotal')
	# def compute_net_amount(self):
	# 	sum=0
	# 	for line in self:
	# 		sum=sum+(self.od_tax_amount+self.price_subtotal)
	# 	self.od_net_amount=sum
