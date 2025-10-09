# -*- coding: utf-8 -*-
import copy
import math
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
import datetime
import dateutil.relativedelta
from datetime import date, timedelta
import itertools
from lxml import etree
import odoo.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta



class booking_sheet_report_new(models.Model):
    _name = 'booking.sheet.report.new'
    _order = "id desc"
    date = fields.Date(string="Date")
    day = fields.Char(string="Day")
    coach_id = fields.Many2one('res.partner',string="Coach")
    venue_id = fields.Many2one('od.venue',string='Venue')
    duration = fields.Float(string="Time")
    schedule_id = fields.Many2one('od.scheduled',string='Schedule')
    partner_id = fields.Many2one('res.partner',string='Student',) 
    activities_id = fields.Many2one('od.activities',string='Program',required="1")
    amount = fields.Float(string="Amount")
    booked_lesson = fields.Float(string="Booked Lesson")
    
    no_of_lesson = fields.Float(string="No.of Lesson")
    pending_lesson = fields.Float(string="Pending Lesson")
    
