# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from odoo import tools
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class orchid_account_partial_reconcile_view(models.Model):
    _name = "orchid.account.partial.reconcile.view"
    _description ='Orchid Partial Reconcile View'
    _auto = False
#
#     
#     def init(self):
#         cr = self.env.cr
#         tools.drop_view_if_exists(cr, 'orchid_account_partial_reconcile_view')
#         cr.execute("""
#               CREATE OR REPLACE VIEW public.orchid_account_partial_reconcile_view AS
#                 select rec.id,rec.credit_move_id,cl.date as cr_date,rec.debit_move_id,rec.full_reconcile_id,dl.date as dr_date,rec.amount
# from account_partial_reconcile rec
# left join account_move_line dl on dl.id=rec.debit_move_id
# left join account_move_line cl on cl.id=rec.credit_move_id
# """)