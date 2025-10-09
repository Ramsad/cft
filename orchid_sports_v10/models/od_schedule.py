# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class OdSchedule(models.Model):
    _name = 'od.schedule'
    _description = 'Schedule'
    _order = 'date_from, id'

    activities_id = fields.Many2one('od.activities', string='Program', index=True)
    coach_id = fields.Many2one('res.partner', string='Coach', required=True)
    fees = fields.Float(string='Fees', default=0.0)
    hourly_rate = fields.Float(string='Hourly Rate', default=0.0)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)

    # keep as-is if you really want free-text times
    time_from = fields.Char(string='Time From')
    time_to   = fields.Char(string='Time To')

    date_from = fields.Datetime(string="Date From", index=True)
    date_to   = fields.Datetime(string="Date To", index=True)

    # Optional extra date range
    x_date_from = fields.Date(string="Date From (X)")
    x_date_to   = fields.Date(string="Date To (X)")

    duration = fields.Float(
        string="Duration (hours)",
        compute="_compute_duration",
        store=True,
        help="(date_to - date_from) in hours."
    )
    total = fields.Float(
        string='Total',
        compute="_compute_total",
        store=True,
        help="fees + (duration * hourly_rate)."
    )
    venue_id = fields.Many2one('od.venue', string='Venue')

    # ---------------------------
    # Computes
    # ---------------------------
    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to >= rec.date_from:
                delta = rec.date_to - rec.date_from
                rec.duration = delta.total_seconds() / 3600.0
            else:
                rec.duration = 0.0

    @api.depends('fees', 'hourly_rate', 'duration')
    def _compute_total(self):
        for rec in self:
            fee = rec.fees or 0.0
            hrs = rec.duration or 0.0
            rate = rec.hourly_rate or 0.0
            rec.total = fee + (hrs * rate)

    # ---------------------------
    # Onchanges
    # ---------------------------
    @api.onchange('activities_id')
    def _onchange_activities_id(self):
        """When a program is chosen, prefill coach/venue if available."""
        if self.activities_id:
            self.coach_id = self.activities_id.coach_id or False
            self.venue_id = getattr(self.activities_id, 'venue_id', False) or False

    # ---------------------------
    # Constraints
    # ---------------------------
    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError(_("End datetime must be on or after start datetime."))

    @api.constrains('fees', 'hourly_rate', 'duration')
    def _check_non_negative_numbers(self):
        for rec in self:
            if (rec.fees or 0.0) < 0 or (rec.hourly_rate or 0.0) < 0 or (rec.duration or 0.0) < 0:
                raise ValidationError(_("Fees, Hourly Rate, and Duration cannot be negative."))
