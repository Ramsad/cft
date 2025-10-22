# -*- coding: utf-8 -*-
import math
from odoo import fields, models, api, _
from odoo import tools
# from odoo.tools import amount_to_text_en, float_round
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.osv import expression


class OrchidAccountDivision(models.Model):
    _name = 'orchid.account.division'
    _description = "Account Division"

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)


class OrchidAccountBranch(models.Model):
    _name = 'orchid.account.branch'
    _description = "Account Branch"

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)


class OrchidAccountCostCenter(models.Model):
    _name = 'orchid.account.cost.center'
    _description = "Account Cost Center"

    code = fields.Char(string='Code', required=True)
    seq = fields.Integer(string="Sequence")
    name = fields.Char(string='Name', required=True)
    branch_id = fields.Many2one('orchid.account.branch', string='Branch')
    div_id = fields.Many2one('orchid.account.division', string='Division')
    div_mgr_id = fields.Many2one('res.users', string="Division Manager")
    target = fields.Float(string="Sales Target", help="This is for Day Report...Not for Incentive")



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _order = "id ASC"

    orchid_div_id = fields.Many2one('orchid.account.division', string='Division')
    orchid_br_id = fields.Many2one('orchid.account.branch', string='Branch')
    orchid_cc_id = fields.Many2one('orchid.account.cost.center', string='Cost Center')

    @api.onchange('account_id')
    def move_line_account_change(self):
        if self.journal_id and self.journal_id.orchid_div_id:
            self.orchid_div_id = self.journal_id.orchid_div_id.id
        if self.journal_id and self.journal_id.orchid_br_id:
            self.orchid_br_id = self.journal_id.orchid_br_id.id
        if self.journal_id and self.journal_id.orchid_cc_id:
            self.orchid_cc_id = self.journal_id.orchid_cc_id.id



    @api.onchange('currency_id')
    def od_amount_currency_onchange(self):
        default_currency = self.move_id and self.move_id.currency_id
        rate = default_currency.rate
        from_currency_rate = self.currency_id.rate
        amount = 0
        if float(from_currency_rate) >=0.1:
            amount = float(self.amount_currency * (float(1)/float(from_currency_rate)))
        else:
            amount = float(self.amount_currency * float(from_currency_rate))

        if amount <0:
            self.credit = abs(amount)
            self.debit = 0
        else:
            self.debit = abs(amount)
            self.credit = 0


# Modifications in account.journal
class AccountJournal(models.Model):
    _inherit = "account.journal"
    od_cheque_in_acc_id = fields.Many2one('account.account', string='Cheque In Account',
                                          domain=[('deprecated', '=', False)],
                                          help="Cheque Recieved and posted to this account instead Bank A/C")
    od_cheque_out_acc_id = fields.Many2one('account.account', string='Cheque Out Account',
                                           domain=[('deprecated', '=', False)],
                                           help="Cheque Issued and posted to this account instead Bank A/C")
    orchid_div_id = fields.Many2one('orchid.account.division', string='Division')
    orchid_br_id = fields.Many2one('orchid.account.branch', string='Branch')
    orchid_cc_id = fields.Many2one('orchid.account.cost.center', string='Cost Center')


# Modifications in account.payment
class AccountPayment(models.Model):
    _inherit = "account.payment"

    # payment_type = fields.Selection(selection_add=[('inbound', 'Receipt'),('outbound', 'Payment'),('income', 'Income'),('expense', 'Expense')],  ondelete={'inbound': 'set default'},)
    od_income_expense_line = fields.One2many('od.income.expense.line', 'payment_id', string="Income Expense Line")
    is_clearing = fields.Boolean(string='Clearing', copy=False)
    is_reverse = fields.Boolean(string='Reverse', copy=False)
    is_group = fields.Boolean(string='Group Pay', copy=False)
    od_bank_account = fields.Many2one('account.account', string='Bank Account', required=False,
                                      domain=[('deprecated', '=', False)],
                                      help="Select Bank Account (Default filled from Journal)", copy=False)
    od_clearing_account = fields.Many2one('account.account', string='Clearing Account',
                                          domain=[('deprecated', '=', False)],
                                          help="Select Clearing Account (Default filled from Journal)", copy=False)
    od_type = fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], string="Type", related="journal_id.type")
    od_check_no = fields.Char(string="Check No", readonly=True, states={'draft': [('readonly', False)]})
    od_check_date = fields.Date(string="Check Date")
    od_release_move_id = fields.Many2one('account.move', string="Release Entry")
    od_group_move_id = fields.Many2one('account.move', string="Group Entry")
    od_inex_move_id = fields.Many2one('account.move', string="Entry", copy=False)
    group_line = fields.One2many('orchid.group.payment', 'group_pay_id', string='Group Pay', readonly=False)
    od_released = fields.Boolean(string='Released')
    od_check_amount_in_words = fields.Char(string="Amount in Words", compute='od_get_amount_in_words')
    od_check_print = fields.Boolean(string="Check Print Option")
    od_check_to = fields.Char(string="Check To :")
    od_internal_note = fields.Text('Note')

    #
    # @api.onchange('od_check_print')
    # def onchange_od_check_print(self):
    # 	if self.od_check_print:
    # 		check_to = self.partner_id and self.partner_id.name or ''
    # 		self.od_check_to = check_to
    #
    # TODO:  removed in newer Odoo; refactor for recordsets

    def od_get_amount_in_words(self):
        check_amount_in_words = amount_to_text_en.amount_to_text(math.floor(self.amount), lang='en', currency='')
        check_amount_in_words = check_amount_in_words.replace(' and Zero Cent', '')  # Ugh
        decimals = self.amount % 1
        if decimals >= 10 ** -2:
            check_amount_in_words += _(' and %s/100') % str(
                int(round(float_round(decimals * 100, precision_rounding=1))))
        check_amount_in_words = check_amount_in_words.replace(',', '')
        self.od_check_amount_in_words = check_amount_in_words.upper()


#
# 	def cancel(self):
# 		result = super(AccountPayment,self).cancel()
# 		if self.od_group_move_id:
# 			self.od_group_move_id.button_cancel()
# 			self.od_group_move_id.unlink()
# 		if self.od_inex_move_id:
# 			self.od_inex_move_id.button_cancel()
# 			self.od_inex_move_id.unlink()
# 	# TODO:  removed in newer Odoo; refactor for recordsets
# #
# 	def release(self):
#
# 		if not self.od_release_move_id and self.journal_id.type=='bank' and self.is_clearing==True and self.is_reverse==False and self.state=='posted' :
# 			print("::if not self.od_release_move_id")
# 			debit_account_id = False
# 			credit_account_id = False
# 			journal_id = self.journal_id and self.journal_id.id or False
# 			payment_type = self.payment_type
# 			partner_id = self.partner_id and self.partner_id.id
# 			if payment_type in ('expense','outbound'):
# 				debit_account_id = self.od_clearing_account and  self.od_clearing_account.id or False
# 				credit_account_id = self.od_bank_account and self.od_bank_account.id or False
# 			elif payment_type in ('income','inbound'):
# 				credit_account_id = self.od_clearing_account and  self.od_clearing_account.id or False
# 				debit_account_id = self.od_bank_account and self.od_bank_account.id or False
# 			check_date = self.od_check_date
# 			check_no = self.od_check_no
# 			name = self.name
# 			amount = self.amount
# 			move_vals = {'journal_id':journal_id,'date':check_date,'ref':name + _(' / ') + check_no}
# 			move_line = []
# 			debit_line_vals = (0,0,{'account_id':debit_account_id,'name':name,'credit':0.0,'debit':amount,'partner_id':partner_id})
# 			credit_line_vals =  (0,0,{'account_id':credit_account_id,'name':name,'credit':amount,'debit':0.0,'partner_id':partner_id})
# 			move_line.append(debit_line_vals)
# 			move_line.append(credit_line_vals)
# 			move_vals['line_ids'] = move_line
# 			move_pool = self.env['account.move']
# 			move = move_pool.create(move_vals)
# 			move_id = move.id
# 			move.post()
# 			self.write({'od_release_move_id':move_id,'od_released':True})
#
#
# 	# # TODO:  removed in newer Odoo; refactor for recordsets
# #
# 	# def group_pay(self):
# 	#     pass
#
# 	@api.onchange('journal_id')
# 	def _onchange_journal(self):
# 		if self.journal_id:
# 			self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
# 			# Set default payment method (we consider the first to be the default one)
# 			payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
# 			self.payment_method_id = payment_methods and payment_methods[0] or False
# 			# Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
# 			payment_type = self.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'
# 			self.od_bank_account = self.payment_type in ('outbound','transfer','debit_note') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id
# 			self.od_clearing_account = self.payment_type in ('outbound','transfer') and self.journal_id.od_cheque_out_acc_id.id or self.journal_id.od_cheque_in_acc_id.id
#
# 			return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}
# 		return {}
#
#
# 	def _get_liquidity_move_line_vals(self, amount):
# 		name = self.name
# 		acc_id = False
# 		if self.payment_type == 'transfer':
# 			name = _('Transfer to %s') % self.destination_journal_id.name
# 		clearing_id = self.od_clearing_account.id
# 		bank_id = self.od_bank_account.id
# 		if self.is_clearing:
# 			acc_id = clearing_id
# 		else:
# 			acc_id = bank_id
#
# 		vals = {
# 			'name': name,
# 			'account_id': acc_id,
# 			'payment_id': self.id,
# 			'journal_id': self.journal_id.id,
# 			'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
# 		}
#
# 		# If the journal has a currency specified, the journal item need to be expressed in this currency
# 		if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
# 			amount = self.currency_id.with_context(date=self.payment_date).compute(amount, self.journal_id.currency_id)
# 			debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(date=self.payment_date).compute_amount_fields(amount, self.journal_id.currency_id, self.company_id.currency_id)
# 			vals.update({
# 				'amount_currency': amount_currency,
# 				'currency_id': self.journal_id.currency_id.id,
# 			})
# 		return vals
#
# 	def gen_group_pay_line(self):
# 		if len(self.group_line) >0:
# 			if self.payment_type =='inbound':
# 				journal_id = self.journal_id.id
# 				line_total = 0
# 				move_vals = {'journal_id':journal_id,'date':self.payment_date,'ref': self.name + _(' / ') + str(self.od_check_no)}
# 				move_line = []
# 				for cline in self.group_line:
# 					partner = self.env['res.partner'].browse(cline.child_partner_id)
# 					cr_account_id = partner.property_account_receivable_id.id
# 					credit_line =  (0,0,{'ref':self.name,'journal_id':journal_id,'account_id':cr_account_id,'partner_id':cline.child_partner_id.id,'name':cline.name,'credit':cline.pay_amount,'debit':0.0})
# 					move_line.append(credit_line)
# 					line_total += cline.pay_amount
# 				groupco = self.env['res.partner'].browse(self.partner_id)
# 				dr_account_id = groupco.property_account_receivable_id.id
# 				debit_line = (0,0,{'ref':cline.name,'journal_id':journal_id,'account_id':dr_account_id,'partner_id':self.partner_id.id,'name':self.name,'credit':0.0,'debit':line_total})
# 				move_line.append(debit_line)
# 				move_vals['line_ids'] = move_line
# 				move_pool = self.env['account.move']
# 				move = move_pool.create(move_vals)
# 				move_id = move.id
# 				move.post()
# 				self.write({'od_group_move_id':move_id})
#
#
# 	def gen_income_expense_line(self):
# 		if len(self.od_income_expense_line)<0:
# 			raise UserError(_('no lines found'))
#
#
#
#
#
# 		if self.payment_type =='income':
# 			journal_id = self.journal_id.id
# 			line_total = 0
# 			move_vals = {'journal_id':journal_id,'date':self.payment_date,'ref': self.name + _(' / ') + str(self.od_check_no) or self.communication,'narration':self.od_internal_note}
# 			move_line = []
# 			for line in self.od_income_expense_line:
# 				debit = 0
# 				credit = line.amount
# 				if line.amount < 0:
# 					debit = abs(line.amount)
# 					credit = 0
#
# 				cr_account_id = line.account_id and line.account_id.id
#
# 				credit_line =  (0,0,{'ref':line.label or self.communication,'journal_id':journal_id,'account_id':cr_account_id,
# 					'name':line.label,'credit':credit,'debit':debit,'analytic_account_id':line.analytic_account_id and line.analytic_account_id.id,'orchid_cc_id':line.orchid_cc_id and line.orchid_cc_id.id,'partner_id':line.partner_id and line.partner_id.id})
# 				move_line.append(credit_line)
#
# 			dr_account_id = self.od_clearing_account and self.od_clearing_account.id or self.od_bank_account and self.od_bank_account.id
# 			debit_line = (0,0,{'ref':self.name or self.communication,'journal_id':journal_id,'account_id':dr_account_id,'name':self.name,'credit':0.0,'debit':self.amount})
# 			move_line.append(debit_line)
# 			move_vals['line_ids'] = move_line
# 			move_pool = self.env['account.move']
# 			move = move_pool.create(move_vals)
# 			move_id = move.id
# 			self.od_inex_move_id = move_id
# 			move.post()
# 			self.name = move.name
# 		if self.payment_type =='expense':
#
# 			journal_id = self.journal_id.id
# 			line_total = 0
# 			move_vals = {'journal_id':journal_id,'date':self.payment_date,'ref': self.name + _(' / ') + str(self.od_check_no)}
# 			move_line = []
# 			for line in self.od_income_expense_line:
# 				debit = line.amount
# 				credit = 0
# 				if line.amount < 0:
# 					credit = abs(line.amount)
# 					debit = 0
#
#
# 				dr_account_id = line.account_id and line.account_id.id
# 				debit_line =  (0,0,{'ref':line.label,'journal_id':journal_id,'account_id':dr_account_id,
# 					'name':line.label,'credit':credit,'debit':debit,'analytic_account_id':line.analytic_account_id and line.analytic_account_id.id,'orchid_cc_id':line.orchid_cc_id and line.orchid_cc_id.id,'partner_id':line.partner_id and line.partner_id.id})
# 				move_line.append(debit_line)
# 			cr_account_id = self.od_clearing_account and self.od_clearing_account.id or self.od_bank_account and self.od_bank_account.id
# 			credit_line = (0,0,{'ref':self.name,'journal_id':journal_id,'account_id':cr_account_id,'name':self.name,'credit':self.amount,'debit':0})
# 			move_line.append(credit_line)
# 			move_vals['line_ids'] = move_line
# 			move_pool = self.env['account.move']
# 			move = move_pool.create(move_vals)
# 			move_id = move.id
# 			self.od_inex_move_id = move_id
#
# 			move.post()
# 			self.name = move.name
#
# 	def post(self):
# 		if self.payment_type in ('income','expense'):
# 			self.gen_income_expense_line()
# 			self.state = 'posted'
# 			return True
# 		if self.is_group:
# 			self.gen_group_pay_line()
# 		return super(AccountPayment,self).post()
#
#
# 	def _create_payment_entry(self, amount):
# 		result = super(AccountPayment, self)._create_payment_entry(amount)
# 		self.name = result.name
# 		if self.od_check_no != "" and self.od_check_no:
# 			for line in result.line_ids:
# 				line.name = self.od_check_no
# 		return result
#
#
#
# 	def print_payment(self):
# 		self.ensure_one()
# 		return self.env['report'].get_action(self, 'orchid_account_enhancement.report_account_payment')
#

class OdIncomeExpenseLine(models.Model):
    _name = 'od.income.expense.line'
    _description = "od.income.expense.line"
    payment_id = fields.Many2one('account.payment', string='Payment')
    account_id = fields.Many2one('account.account', string='Account')
    partner_id = fields.Many2one('res.partner', string='Partner')
    label = fields.Char(string="Label")
    orchid_cc_id = fields.Many2one('orchid.account.cost.center', string='Cost Center')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    amount = fields.Float(string="Amount")


class OrchidGroupPayment(models.Model):
    _name = 'orchid.group.payment'
    _description = "Account Group Payment"

    name = fields.Char(string='Remarks', required=True, default='Group Pay : ')
    child_partner_id = fields.Many2one('res.partner', string='Group Co', required=True, help="Group Company")
    pay_amount = fields.Float(string="Amount", required=True, help="Amount to be Allocated")
    group_pay_id = fields.Many2one('account.payment', string='Group Pay', required=True, ondelete='cascade', index=True)


# Parent Group Added
class AccountGroup(models.Model):
    _name = "orchid.account.group"
    _parent_store = True
    _order = 'code_prefix'

    parent_id = fields.Many2one('orchid.account.group', index=True, ondelete='cascade')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)
    name = fields.Char(required=True)
    code_prefix = fields.Char()
    parent_path = fields.Char()

    # def name_get(self):
# 	result = []
# 	for group in self:
# 		name = group.name
# 		if group.code_prefix:
# 			name = group.code_prefix + ' ' + name
# 		result.append((group.id, name))
# 	return result
#
#
# def name_search(self, name='', args=None, operator='ilike', limit=100):
# 	if not args:
# 		args = []
# 	criteria_operator = ['|'] if operator not in expression.NEGATIVE_TERM_OPERATORS else ['&', '!']
# 	domain = criteria_operator + [('code_prefix', '=ilike', name + '%'), ('name', operator, name)]
# 	return self.search(domain + args, limit=limit).name_get()


class AccountAccount(models.Model):
    _inherit = "account.account"

    group_id = fields.Many2one('orchid.account.group')
