# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, SUPERUSER_ID, _

class od_sports_receipt_analysis_view(models.Model):
	_name = "od.sports.receipt.analysis.view"
	_description = "od.sports.receipt.analysis.view"
	_auto = False
	_rec_name = 'receipt_id'
	


	receipt_id = fields.Many2one('od.sports.receipt', string='Name')
	activities_id = fields.Many2one('od.activities',string='Program')
	coach_id = fields.Many2one('res.partner', string='Coach')   
	venue_id = fields.Many2one('od.venue', string='Venue')
	venue_comm = fields.Float(string='Venue Commission') 
	date = fields.Date('Date')
	term_id = fields.Many2one('od.terms', string='Term')  
	
	rv_no = fields.Char(string='RV/Number')
	
	
	partner_id = fields.Many2one('res.partner',string='Student')
	account_id = fields.Many2one('account.account',string='Account')
	type_id = fields.Many2one('od.camp.type',string='Fees Type')
	remarks = fields.Char(string='Cheque No')
	cheque_date = fields.Date('Cheque Date')
	amount = fields.Float(string='Fees')
	no_of_class = fields.Integer(string='No. Of Class')
	transportation = fields.Float(string='Reg.Fee')
	total = fields.Float(string='Total')
	cost_centre_id = fields.Many2one('orchid.account.cost.center',string='Cost Centre')

	od_commission_perc = fields.Float(string='Comm. %')
	od_venue_commission = fields.Float(string='Venue Comm.')
	coach_commision = fields.Float(string='Coach Comm.')
	od_vat_amount = fields.Float(string='Vat Amount')
	od_invoice_no = fields.Char(string='Inv No',default='/')
	od_refund_amount = fields.Float(string='Refund Fee')
	od_reg_refund_amount = fields.Float(string='Refund Reg. Fee')
	od_refund_total = fields.Float('Refund Total')
	od_refund_vat_amount = fields.Float(string='Refund Vat')
	od_refund_subtotal = fields.Float(string='Refund Grandtotal')
	od_refund_coach_comm = fields.Float(string='Refund coach comm.')
	od_refund_venue_comm = fields.Float(string='Refund venue comm.')
	grand_total = fields.Float(string='Grand Total')

	# def _select(self):
	# 	select_str = """
	# 		 SELECT ROW_NUMBER () OVER (ORDER BY osrl.id ) AS id,
	# 			osrl.receipt_id as receipt_id,
	# 			osr.activities_id as activities_id,
	# 			osr.coach_id  as coach_id,
	# 			osr.venue_id as venue_id,
	# 			osr.venue_comm as venue_comm,
	# 			osr.date as date,
	# 			osr.term_id as term_id,
	# 			osrl.rv_no as rv_no,
	# 			osrl.partner_id as partner_id,
	# 			osrl.payment_type_account_id as account_id,
	# 			osrl.type_id as type_id,
	# 			osrl.remarks as remarks,
	# 			osrl.date as cheque_date,
	# 			osrl.amount as amount,
	# 			osrl.no_of_clases as no_of_class,
	# 			osrl.transportation as transportation,
	# 			osrl.total as total,
	# 			oct.cost_centre_id as cost_centre_id,
	# 			osrl.od_commission_perc as od_commission_perc,
	# 			osrl.od_venue_commission as od_venue_commission,
	# 			osrl.coach_commision as coach_commision,
	# 			osrl.od_vat_amount as od_vat_amount,
	# 			osrl.od_invoice_no as od_invoice_no,
	# 			osrl.grand_total as grand_total,
	# 			orel.od_refund_amount as od_refund_amount,
	# 			orel.od_reg_refund_amount as od_reg_refund_amount,
	# 			orel.od_refund_total as od_refund_total,
	# 			orel.od_refund_vat_amount as od_refund_vat_amount,
	# 			orel.od_refund_subtotal as od_refund_subtotal,
	# 			orel.od_refund_coach_comm as od_refund_coach_comm,
	# 			orel.od_refund_venue_comm as od_refund_venue_comm
    #
	#
    #
	# 	"""
	# 	return select_str
    #
	# def _from(self):
	# 	from_str = """
	# 			od_sports_receipt_line   osrl
	#
	# 	"""
	# 	return from_str
	# def _group_by(self):
	# 	group_by_str = """
	# 		GROUP BY osrl.id,
	# 			osrl.receipt_id,
	# 			osr.activities_id,
	# 			osr.coach_id,
	# 			osr.venue_id,
	# 			osr.venue_comm,
	# 			osr.date,
	# 			osr.term_id,
	# 			osrl.rv_no,
	# 			osrl.partner_id,
	# 			osrl.payment_type_account_id,
	# 			osrl.type_id,
	# 			osrl.remarks,
	# 			osrl.date,
	# 			osrl.amount,
	# 			osrl.no_of_clases,
	# 			osrl.transportation,
	# 			osrl.total,
	# 			oct.cost_centre_id,
	# 			osrl.od_commission_perc,
	# 			osrl.od_venue_commission,
	# 			osrl.coach_commision,
	# 			osrl.od_vat_amount,
	# 			osrl.od_invoice_no,
	# 			orel.od_refund_amount,
	# 			orel.od_reg_refund_amount,
	# 			orel.od_refund_total,
	# 			orel.od_refund_vat_amount,
	# 			orel.od_refund_subtotal,
	# 			orel.od_refund_coach_comm,
	# 			orel.od_refund_venue_comm
    #
	# 	"""
	# 	return group_by_str
	#
	#
	# def init(self):
	# 	tools.drop_view_if_exists(self._cr, self._table)
	# 	self._cr.execute("""CREATE or REPLACE VIEW %s as (
	# 		%s
	# 		FROM  %s
	# 		left join od_sports_receipt osr ON (osrl.receipt_id = osr.id)
	# 		left join od_refund_entry_line orel ON (orel.od_collection_line_id = osrl.id)
	# 		left join account_account account ON (osrl.payment_type_account_id = account.id)
	# 		left join od_activities act ON (osr.activities_id = act.id)
	# 		left join od_camp_type oct on (osrl.type_id = oct.id)
	# 		)""" % (self._table, self._select(), self._from()))
