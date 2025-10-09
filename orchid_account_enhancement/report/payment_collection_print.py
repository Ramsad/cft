# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models, SUPERUSER_ID, _


class ReportPaymentCollection(models.AbstractModel):

    _name = 'report.orchid_account_enhancement.report_payment_collection'



    
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
       
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'lines':data.get('lines',[]),
            'time': time,
          
        }
        return self.env['report'].render('orchid_account_enhancement.report_payment_collection', docargs)
   
