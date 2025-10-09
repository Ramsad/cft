from odoo import api, fields, models,_

class AccountInvoice(models.Model):
	_inherit='account.move'

	od_vendor_inv_date=fields.Date(string='Inv. Date')