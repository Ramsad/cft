from odoo import models, fields, api

class AccountInvoiceTaxCalc(models.TransientModel):
	_name="od.account.tax.calculation"

	def recompute_tax(self):

		context = dict(self._context or {})
		invoice_ids = context.get('active_ids', []) or []

		for line in self.env['account.move'].browse(invoice_ids):
			for line_ids in line.invoice_line_ids:
				line_ids.compute_tax_amount()


