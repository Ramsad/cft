# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT


class od_duplicate_entry(models.TransientModel):
    _name = 'od.duplicate.entry'
    _description = 'Duplicate Entry Wizard'
    
    freq = fields.Integer(string="No Of Entries")
    auto_post = fields.Boolean(string="Autopost")
    
    def duplicate(self):
        context = self.env.context 
        active_id = context.get('active_id')
        move = self.env['account.move']
        move_obj = move.browse(active_id)
        date = move_obj.date
        ref = move_obj.ref
        date = datetime.strptime(date,"%Y-%m-%d") 
        freq = self.freq
        auto_post = self.auto_post
        move_ids = []
        for x in range(0,freq):
            date = date + relativedelta(months=1)
            new_move =move_obj.copy({'date':str(date)})
            new_move.write({'ref':ref})
            for line in new_move.line_ids:
                line['date'] = str(date)
                line['date_maturity'] = str(date)
            
            move_ids.append(new_move.id )
        if auto_post:
            for move_id in move_ids:
                move_ob = move.browse(move_id)
                move_ob.post()
        domain = [('id','in',move_ids)]
        return  {
            'domain': domain,
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window'
             }
