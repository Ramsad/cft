from odoo import models,api,fields

class res_company(models.Model):
	_inherit = "res.company"

	od_trn = fields.Char(string='TRN')
	od_name_arabic = fields.Char(string='Arabic Name')