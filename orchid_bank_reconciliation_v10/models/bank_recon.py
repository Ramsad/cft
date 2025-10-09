# -*- coding: utf-8 -*-
import itertools
from lxml import etree
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
import odoo.addons.decimal_precision as dp

class OrchidBankReconciliation(models.Model):
    _name = 'orchid.bank.reconciliation'
    _description = "Bank Reconciliation"

    def od_get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one('res.company', string='Company',default=od_get_company_id)



    
    def update_all_with_effective_date(self):
        for move in self.move_line_ids:
            move.od_fill_date()
        return True

    
    def unlink(self):
#        for bank in self:
#            if bank.state not in ('draft'):
        raise Warning(_('You can delete only draft document'))
        return super(OrchidBankReconciliation, self).unlink()

    # TODO:  removed in newer Odoo; refactor for recordsets
# 
    def button_dummy(self):
        return True

    
    def od_open_bank_stmt_reconcile(self):
        #unlink existing
        move_line_ids = self.env['account.move.line'].search([('od_reconcile_id','=',self.id)])
        move_line_ids.write({'od_reconcile_id':''})
        
        
        account_id = self.account_id and self.account_id.id
        date = self.date 
        to_date = self.to_date
        domain = ['&','|',('debit','>',0),('credit','>',0),('account_id', '=', account_id)]
        if date and to_date:
            domain.append(('date', '>=', date))
            domain.append(('date', '<=', to_date))
        if date and not to_date:
            domain.append(('date', '>=', date))
        if to_date and not date:
            domain.append(('date', '<=', to_date))
#         move_line_ids = self.env['account.move.line'].search(domain)
     
       

        if self.type == 'reconciled':
            domain.append(('od_reconcile_date', '!=',False))
            
        elif self.type == 'unreconciled':
            domain.append(('od_reconcile_date', '=',False))
        
        move_line_ids = self.env['account.move.line'].search(domain)
        move_lines = [x for x in move_line_ids if x.move_id.state== 'posted']
        line_ids = [x.id for x in move_lines]
        move_line_ids = self.env['account.move.line'].browse(line_ids)
       
        if not move_line_ids:
            raise except_orm(_('No Entity To Reconcile!'), _('Please select another account'))
      
        move_line_ids.write({'od_reconcile_id':self.id})
        return True

    
    def od_reconcile_bank_stmt_reconcile(self):
        move = self.move_line_ids
        lines = move.filtered(lambda r: r.od_reconcile_date == False)
        lines.write({'od_reconcile_id':False})
        account_id = self.account_id and self.account_id.id
        from_date = self.date
        to_date = self.to_date
        if account_id:
            context = self._context
            ctx={'account_id': account_id}
            recs = self.pool.get('account.move.line').browse(self._cr, self._uid, [], ctx)
            res = recs.env['account.move.line'].od_book_bank_balance(from_date,to_date)
            self.book_balance=bkb=res and res.get('book_balance') or 0.0
            self.bank_balance =bnb= res and res.get('bank_balance')  or 0.0
            self.fc_bank_balance=fcbkb=res and res.get('fc_bank_balance') or 0.0
            self.fc_book_balance=fcbnb=res and res.get('fc_book_balance') or 0.0
        self.state='done'
        return True

    # TODO:  removed in newer Odoo; refactor for recordsets
# 
    @api.depends('account_id','date','to_date')
    def _compute_balance(self):
        account_id = self.account_id and self.account_id.id
        from_date = self.date
        to_date = self.to_date
        if account_id:
            context = self._context
            ctx={'account_id': account_id}
            recs = self.pool.get('account.move.line').browse(self._cr, self._uid, [], ctx)
            res = recs.env['account.move.line'].od_book_bank_balance(from_date,to_date)
            self.book_balance = res and res.get('book_balance') or 0.0
            self.bank_balance = res and res.get('bank_balance')  or 0.0
            self.fc_bank_balance = res and res.get('fc_bank_balance') or 0.0
            self.fc_book_balance = res and res.get('fc_book_balance') or 0.0
            self.reconciled_balance = res and res.get('reconciled_balance') or 0.0
            self.unconciled_balance = res and res.get('unconciled_balance') or 0.0


    @api.onchange('account_id','date','to_date')
    def onchange_account_id(self):
        account_id = self.account_id and self.account_id.id
        from_date = self.date
        to_date = self.to_date
        if account_id:
            context = self._context
            ctx={'account_id': account_id}
#             recs = self.pool.get('account.move.line').browse(self._cr, self._uid, [], ctx)
            res = self.env['account.move.line'].od_book_bank_balance(from_date,to_date)
            self.book_balance = res and res.get('book_balance') or 0.0
            self.bank_balance = res and res.get('bank_balance')  or 0.0
            self.fc_bank_balance = res and res.get('fc_bank_balance') or 0.0
            self.fc_book_balance = res and res.get('fc_book_balance') or 0.0
            self.reconciled_balance = res and res.get('reconciled_balance') or 0.0
            self.unconciled_balance = res and res.get('unconciled_balance') or 0.0


    name = fields.Char(string='Reference/Description')
    account_id = fields.Many2one('account.account',string="Account",required=True,readonly=True,states={'draft': [('readonly', False)]})
    to_date = fields.Date('To Date')
    state = fields.Selection([
            ('draft','Draft'),
            ('open','Open'),
            ('done','Reconciled'),
        ], string='Status', index=True, readonly=True, default='draft',copy=False)
    date = fields.Date(string='From Date', index=True, default=fields.Date.today(),
        help="Keep empty to use the current date", copy=False)
    
    move_line_ids = fields.One2many('account.move.line','od_reconcile_id',string='Reconcile Lines',states={'open': [('readonly', False)]},copy=False)

#    book_balance = fields.Float(string='Book Balance', digits=dp.get_precision('Account'))
#    bank_balance = fields.Float(string='Bank Balance', digits=dp.get_precision('Account'))
#    fc_book_balance = fields.Float(string='FC Book Balance', digits=dp.get_precision('Account'))
#    fc_bank_balance = fields.Float(string='FC Bank Balance', digits=dp.get_precision('Account'))
#    reconciled_balance = fields.Float(string='Reconciled', digits=dp.get_precision('Account'))
#    unconciled_balance = fields.Float(string='Unreconciled', digits=dp.get_precision('Account'))


    book_balance = fields.Float(string='Book Balance', digits=dp.get_precision('Account') ,readonly=True,compute='_compute_balance')
    bank_balance = fields.Float(string='Bank Balance', digits=dp.get_precision('Account'),readonly=True,compute='_compute_balance')
    fc_book_balance = fields.Float(string='FC Book Balance', digits=dp.get_precision('Account'),readonly=True,compute='_compute_balance')
    fc_bank_balance = fields.Float(string='FC Bank Balance', digits=dp.get_precision('Account'),readonly=True,compute='_compute_balance')
    reconciled_balance = fields.Float(string='Reconciled', digits=dp.get_precision('Account'),readonly=True,compute='_compute_balance')
    unconciled_balance = fields.Float(string='Unreconciled', digits=dp.get_precision('Account'),readonly=True,compute='_compute_balance')

    type = fields.Selection([
            ('unreconciled','UnReconciled'),
            ('reconciled','Reconciled'),
            ('all','All'),
        ], string='Type',default='unreconciled')

    _sql_constraints = [
        ('account_id_uniq', 'unique(account_id)',
            'Account is unique per Reconciliation'),
    ]


#     
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super(OrchidBankReconciliation, self).fields_view_get(
#             view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         context = self._context
#         doc = etree.XML(res['arch'])
#         for node in doc.xpath("//field[@name='account_id']"):
#             if context.get('bank'):
# #                account = self.env['account.move.line'].od_list_accounts()
# #                ids = account and [a[0] for a in account] or []
# #                val = "[('id', '=',"+str(ids)+")]"
#                 ids = self.pool.get('account.account').search(self._cr,self._uid,[('type','=','liquidity')])
#                 val = "[('id', '=',"+str(ids)+")]"
# #                print "DDDDDDDDDddd",ids
#                 node.set('domain', val)
#             res['arch'] = etree.tostring(doc)
#         return res

class account_move_line(models.Model):
    _inherit = 'account.move.line'


    
    def od_fill_date(self):
        if self.od_reconcile_id.state == 'done':
            raise except_orm(_('Already Reconciled!'), _('Try for other'))
        self.od_reconcile_date = self.date
        return True

    # TODO:  removed in newer Odoo; refactor for recordsets
# 
    @api.depends('move_id','date','name','od_reconcile_date')
    def _compute_check_date(self):
        if self.move_id:
            account_voucher_id = self.env['account.voucher'].search([('move_id', '=', self.move_id.id)])
            if account_voucher_id:
                self.od_check_date = account_voucher_id.check_date or False
    od_reconcile_id = fields.Many2one('orchid.bank.reconciliation',string='Bank Reconciled')
    od_check_date = fields.Date(string='Check Date',readonly=True,compute='_compute_check_date')

