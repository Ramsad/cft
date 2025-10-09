# -*- coding: utf-8 -*-
##############################################################################

from odoo import fields,models,api,_
from odoo.tools.translate import _
from odoo.exceptions import UserError, AccessError

class booking_sheet_report_wizard(models.TransientModel):
    _name = "booking.sheet.report.wizard"
    _description = "Booking Sheet Report"
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    
    coach_id = fields.Many2one('res.partner',string='Coach')

    def get_booking_sheets(self,date_from,date_to,coach_id,model_booking_sheet):


        booking_sheet_objs = model_booking_sheet.search([('date','>=',date_from),('date','<=',date_to),('coach_id','=',coach_id)])
        return booking_sheet_objs


        #    
        #    def get_booking_sheetlines(self,booking_sheets_obj):
        #        attendance_lines = []
        #        for obj in booking_sheets_obj:
        #            lines = obj.attendance_line
        #            for line in lines:
        #                attendance_lines.append(line)
        #        return attendance_lines




        booking_sheet_objs = model_booking_sheet.search([('date','>=',date_from),('date','<=',date_to),('coach_id','=',coach_id)])
        return booking_sheet_objs



    def get_no_of_lines(self,booking_line):
        lines = []
        for line in booking_line:
            lines.append(line.id)
        return len(lines)
    
    def get_booking_sheet_ids(self,booking_sheets_obj):
        booking_ids = []
        for booking in booking_sheets_obj:
            booking_ids.append(booking.id)
        return booking_ids


    
    def get_data_form(self):
        date_from = self.date_from
        date_to = self.date_to
        coach_id = self.coach_id and self.coach_id.id

        model_booking_sheet = self.env['od.sports.attendance']
        existing_ids = self.env['booking.sheet.report.new'].search([])
        existing_ids.unlink()
        booking_sheets_obj = self.get_booking_sheets(date_from,date_to,coach_id,model_booking_sheet)
        booking_sheet_ids = self.get_booking_sheet_ids(booking_sheets_obj)
        #        booking_sheet_lines = self.get_booking_sheetlines(booking_sheets_obj)
        #        for line in booking_sheet_lines:
        #            vals = {'partner_id':}

        for booking in booking_sheets_obj:
            booking_line = booking.attendance_line
            #            no_of_lines = self.get_no_of_lines(booking_line)
            for bl in booking_line:
                activities_id = bl.attendance_id.activities_id and bl.attendance_id.activities_id.id
                term = bl.attendance_id.term_id and bl.attendance_id.term_id.name
                partner_id = bl.partner_id and bl.partner_id.id
                type_id = bl.type_id and bl.type_id.id
                no_of_lessons = len(self.env['od.sports.attendance.line'].search([('partner_id','=',partner_id),('type_id','=',type_id),('attendance_id','in',booking_sheet_ids)]))
                schedule_id = bl.attendance_id.od_scheduled and bl.attendance_id.od_scheduled.id

                amount = 0
                booked_lessons = 0
                schedule_line = self.env['od.scheduled.line'].search([('scheduled_id','=',schedule_id),('partner_id','=',partner_id),('type_id','=',type_id)])
                if schedule_line:
                    schedule_line = schedule_line[0]
                    booked_lessons = schedule_line.no_of_classes



                pending_lessons = booked_lessons - no_of_lessons
                fee_structure = self.env['od.activities.camp.line'].search([('activities_id','=',activities_id),('type_id','=',type_id)])
                if fee_structure:
                    fee_structure = fee_structure[0]
                    if term == 'Term-1':
                        amount = float(fee_structure.t1_fee)


                vals = {'partner_id':partner_id,
                        'date':bl.attendance_id.date,
                        'day':bl.attendance_id.day,
                        'coach_id':bl.attendance_id.coach_id and bl.attendance_id.coach_id.id,
                        'venue_id':bl.attendance_id.venue_id and bl.attendance_id.venue_id.id,
                        'duration':float(bl.attendance_id.duration),
                        'schedule_id':schedule_id,
                        'activities_id':activities_id,
                        'amount':amount,
                        'booked_lesson':booked_lessons,
                        'no_of_lesson':no_of_lessons,
                        'pending_lesson':pending_lessons

                        }


                self.env['booking.sheet.report.new'].create(vals)


    
    def get_data_for_pdf(self):
        raise UserError(_('Under Construction,Please Wait,we will Release Soon'))
        date_from = self.date_from
        datas = []
        date_to = self.date_to
        coach_id = self.coach_id and self.coach_id.id
        model_booking_sheet = self.env['od.sports.attendance']
        booking_sheets_obj = self.get_booking_sheets(date_from,date_to,coach_id,model_booking_sheet)
        booking_sheet_ids = self.get_booking_sheet_ids(booking_sheets_obj)
        #        booking_sheet_lines = self.get_booking_sheetlines(booking_sheets_obj)
        #        for line in booking_sheet_lines:
        #            vals = {'partner_id':}

        for booking in booking_sheets_obj:
            booking_line = booking.attendance_line
            #            no_of_lines = self.get_no_of_lines(booking_line)
            for bl in booking_line:
                activities_id = bl.attendance_id.activities_id and bl.attendance_id.activities_id.id
                term = bl.attendance_id.term_id and bl.attendance_id.term_id.name
                partner_id = bl.partner_id and bl.partner_id.id
                type_id = bl.type_id and bl.type_id.id
                no_of_lessons = len(self.env['od.sports.attendance.line'].search([('partner_id','=',partner_id),('type_id','=',type_id),('attendance_id','in',booking_sheet_ids)]))
                schedule_id = bl.attendance_id.od_scheduled and bl.attendance_id.od_scheduled.id

                amount = 0
                booked_lessons = 0
                schedule_line = self.env['od.scheduled.line'].search([('scheduled_id','=',schedule_id),('partner_id','=',partner_id),('type_id','=',type_id)])
                if schedule_line:
                    schedule_line = schedule_line[0]
                    booked_lessons = schedule_line.no_of_classes



                pending_lessons = booked_lessons - no_of_lessons
                fee_structure = self.env['od.activities.camp.line'].search([('activities_id','=',activities_id),('type_id','=',type_id)])
                if fee_structure:
                    fee_structure = fee_structure[0]
                    if term == 'Term-1':
                        amount = float(fee_structure.t1_fee) / float(fee_structure.t1)


                vals = {'partner_id':partner_id,
                        'date':bl.attendance_id.date,
                        'day':bl.attendance_id.day,
                        'coach_id':bl.attendance_id.coach_id and bl.attendance_id.coach_id.id,
                        'venue_id':bl.attendance_id.venue_id and bl.attendance_id.venue_id.id,
                        'duration':float(bl.attendance_id.duration),
                        'schedule_id':schedule_id,
                        'activities_id':activities_id,
                        'amount':amount,
                        'booked_lesson':booked_lessons,
                        'no_of_lesson':no_of_lessons,
                        'pending_lesson':pending_lessons

                        }


                datas.append(vals)
        return data

    
    def generate_report(self):
        data = self.get_data_form()
        action = self.env.ref('orchid_sports_v10.action_booking_sheet_report_new')
        result = action.read()[0]
        return result 
