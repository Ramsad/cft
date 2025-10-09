from odoo import models, api, fields


class InvoiceLine(models.Model):
    _inherit = "account.move.line"

    od_tax_amount = fields.Float(string="Tax Amount", readonly=True, compute="compute_tax_amount", store=True)
    od_net_amount = fields.Float(string="Total", readonly=True, compute="compute_net_amount", store=True)

    @api.depends(
        'tax_ids',
        'price_unit', 'quantity', 'discount',
        'currency_id',
        'product_id',
        'move_id.partner_id',)
    def compute_tax_amount(self):
        for rec in self:
            amount = 0.0
            if rec.tax_ids:
                # price after discount
                price = rec.price_unit * (1 - (rec.discount or 0.0) / 100.0)
                res = rec.tax_ids.compute_all(
                    price_unit=price,
                    currency=rec.currency_id,
                    quantity=rec.quantity or 0.0,
                    product=rec.product_id,
                    partner=rec.move_id.partner_id,
                    is_refund=rec.move_id.move_type in ('out_refund', 'in_refund'),
                )
                amount = sum(t.get('amount', 0.0) for t in res.get('taxes', []))
            rec.od_tax_amount = amount
    @api.depends('od_tax_amount', 'price_subtotal')
    def compute_net_amount(self):
        for line in self:
            sum = 0
            sum = sum + (line.od_tax_amount + line.price_subtotal)
            line.od_net_amount = sum


class Account_Invoice(models.Model):
    _inherit = "account.move"

    od_rcm_input_account_id = fields.Many2one('account.account', string="Input Account")
    od_rcm_output_account_id = fields.Many2one('account.account', string="Output Account")
    od_rcm_amount = fields.Float(string="Amount")
    od_rcm_ref = fields.Text(string="Reference")

    def invoice_line_move_line_get(self):
        res = super(Account_Invoice, self).invoice_line_move_line_get()
        # self.number = self.name
        if self.od_rcm_amount > 0:
            rcm_line_dict1 = {
                'name': self.od_rcm_ref or False,
                'price_unit': self.od_rcm_amount or False,
                'quantity': "1",
                'price': self.od_rcm_amount or False,
                'account_id': self.od_rcm_input_account_id and self.od_rcm_input_account_id.id or False,
                'invoice_id': self.id,
            }

            rcm_line_dict2 = {
                'name': self.od_rcm_ref or False,
                'price_unit': -self.od_rcm_amount or False,
                'quantity': "1",
                'price': -self.od_rcm_amount or False,
                'account_id': self.od_rcm_output_account_id and self.od_rcm_output_account_id.id or False,
                'invoice_id': self.id,
            }

            if rcm_line_dict1:
                # self.move_id.update(data)
                res.append(rcm_line_dict1)
                res.append(rcm_line_dict2)

        return res
