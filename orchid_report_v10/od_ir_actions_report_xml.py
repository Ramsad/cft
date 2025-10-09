# -*- coding: utf-8 -*-
from odoo.osv import fields, osv
from odoo.tools.translate import _
class ir_actions_report_xml(osv.osv):
    _inherit = 'ir.actions.report.xml'
    _columns = {
        'avilable_in_ddl':fields.boolean('Available In DDL',help="Template Names Can be used,\naccount.report_partnerledger_od1,\naccount.report_partnerledger_od2\n,account.report_partnerledger_od3\n,account.report_partnerledger_od4")
    }
