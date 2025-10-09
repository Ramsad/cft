# -*- coding: utf-8 -*-
import math
from odoo import api, fields, models, _
from odoo.tools import float_utils
from odoo.tools.misc import get_lang


class AccountMove(models.Model):
    _inherit = "account.move"
    od_check_print = fields.Boolean(string="Check Print Option")
    od_check_date = fields.Date(string="Check Date",default=fields.Date.context_today)
    od_check_to = fields.Char("Check To :")
    od_check_amount = fields.Float("Check Amount")
    od_check_amount_in_words = fields.Char(string="Amount in Words",compute='_compute_od_check_amount_in_words')


        #
    @api.depends('od_check_amount', 'currency_id')
    def _compute_od_check_amount_in_words(self):
        """Compute amount in words like 'ONE THOUSAND ... AND 25/100' (no currency name)."""
        for rec in self:
            amount = rec.od_check_amount or 0.0
            lang_code = get_lang(self.env).code or 'en_US'

            # Integer part in words (suppress currency name)
            words = rec.currency_id.amount_to_text(
                math.floor(amount),

            )
            # Odoo may return "and Zero Cent(s)" – strip it
            words = words.replace(' and Zero Cent', '').replace(' and Zero Cents', '')

            # Decimals → XX/100
            decimals = amount - math.floor(amount)
            cents = int(float_utils.float_round(decimals * 100, precision_rounding=1))
            if cents:
                words += _(' and %s/100') % cents

            # Final cleanup and case
            rec.od_check_amount_in_words = words.replace(',', '').upper()

