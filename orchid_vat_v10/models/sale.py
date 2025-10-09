from odoo import models,api,fields

class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"

	od_tax_amount = fields.Float(string="Tax Amount", readonly=True,store=True)

	

	@api.depends('tax_id','price_subtotal')
	def compute_amount(self):
		sum=0
		for tax in self.tax_id:
			sum=sum+(tax.amount*self.price_subtotal)/100
		self.od_tax_amount=sum

