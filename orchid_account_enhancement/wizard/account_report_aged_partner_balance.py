# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import xlwt
from io import StringIO
import base64
from pprint import pprint


class AccountAgedTrialBalance(models.TransientModel):

    _inherit = 'account.aged.trial.balance'

    period_length = fields.Integer(string='Period Length (days)',default=30)
    od_is_slab = fields.Boolean(string='Slabwise')
    
    od_period_lenght1 = fields.Integer(string='Period Length1')
    od_period_lenght2 = fields.Integer(string='Period Length2')
    od_period_lenght3 = fields.Integer(string='Period Length3')
    od_period_lenght4 = fields.Integer(string='Period Length4')
    od_period_lenght5 = fields.Integer(string='Period Length5')
    od_period_lenght6 = fields.Integer(string='Period Length6')
    
    od_partner_ids = fields.Many2many('res.partner',string='Partner')
    # od_group_id = fields.Many2one('orchid.partner.group',string='Group')
    # od_sub_group_id = fields.Many2one('orchid.partner.sub.group',string='Sub Group')
    # od_area_id = fields.Many2one('orchid.partner.area',string='Area')
    salesman_id = fields.Many2one('res.users','Salesman')
    od_account_id = fields.Many2one('account.account','Account')
    excel_file = fields.Binary(string='Dowload Report Excel',readonly=True)
    file_name = fields.Char(string='Excel File',readonly=True)
    od_is_invoice_date = fields.Boolean(string='Invoice Date')
    
    
    
###########################################################################
#{'model': 'ir.ui.menu', 'ids': [], 'form': {'od_is_slab': False, 'period_length': 30, 'od_period_lenght3': 0, 'od_period_lenght2': 0, 'date_from': '2017-05-17', 'result_selection': u'customer', 'journal_ids': [1, 2, 187, 4, 128, 137, 184, 138, 139, 140, 141, 142, 143, 144, 129, 130, 131, 185, 132, 133, 134, 186, 135, 136, 17, 18, 195, 16, 25, 190, 24, 26, 27, 191, 30, 29, 192, 28, 21, 20, 31, 32, 33, 193, 35, 34, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 19, 38, 39, 40, 41, 5, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 189, 194, 53, 55, 54, 58, 57, 56, 59, 61, 60, 196, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 182, 22, 23, 37, 188, 8, 36, 7, 11, 9, 10, 14, 13, 15, 12], 'used_context': {'lang': u'en_US', 'state': u'posted', 'strict_range': True, 'date_to': False, 'date_from': '2017-05-17', 'journal_ids': [1, 2, 187, 4, 128, 137, 184, 138, 139, 140, 141, 142, 143, 144, 129, 130, 131, 185, 132, 133, 134, 186, 135, 136, 17, 18, 195, 16, 25, 190, 24, 26, 27, 191, 30, 29, 192, 28, 21, 20, 31, 32, 33, 193, 35, 34, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 19, 38, 39, 40, 41, 5, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 189, 194, 53, 55, 54, 58, 57, 56, 59, 61, 60, 196, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 182, 22, 23, 37, 188, 8, 36, 7, 11, 9, 10, 14, 13, 15, 12]}, '1': {'start': '2017-01-18', 'stop': '2017-02-16', 'name': '90-120'}, '0': {'start': False, 'stop': '2017-01-17', 'name': '+120'}, '3': {'start': '2017-03-19', 'stop': '2017-04-17', 'name': '30-60'}, '2': {'start': '2017-02-17', 'stop': '2017-03-18', 'name': '60-90'}, 'od_period_lenght1': 0, '4': {'start': '2017-04-18', 'stop': '2017-05-17', 'name': '0-30'}, 'date_to': False, 'partner': [], 'od_period_lenght4': 0, 'id': 16, 'target_move': u'posted'}}












################################    
    def get_data_for_xls(self):
        data = {}
        res = {}
        if self.period_length<=0:
            raise UserError(_('You must set a period length greater than 0.'))
        if not self.date_from:
            raise UserError(_('You must set a start date.'))
        start = datetime.strptime(self.date_from, "%Y-%m-%d")
        
        for i in range(7)[::-1]:
            stop = start - relativedelta(days=self.period_length - 1)
            res[str(i)] = {
                'name': (i!=0 and (str((5-(i+1)) * self.period_length) + '-' + str((7-i) * self.period_length)) or ('+'+str(6 * self.period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        print("res>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",res)
        data['form']=res
        data['form']['od_is_slab']=self.od_is_slab
        data['form']['od_is_invoice_date']=self.od_is_invoice_date
        data['form']['period_length']=self.period_length
        data['form']['od_account_id']= self.od_account_id and self.od_account_id.id or False
        
        
        
        data['form']['od_period_lenght6']=self.od_period_lenght6
        data['form']['od_period_lenght5']=self.od_period_lenght5
        data['form']['od_period_lenght4']=self.od_period_lenght4

        data['form']['od_period_lenght3']=self.od_period_lenght3
        data['form']['od_period_lenght2']=self.od_period_lenght2
        data['form']['od_period_lenght1']=self.od_period_lenght1
       
        data['form']['date_from']=self.date_from
        data['form']['result_selection']=self.result_selection
        data['form']['target_move'] = self.target_move
        journal_ids = []
        for jou in self.journal_ids:
            journal_ids.append(jou.id)
        data['form']['journal_ids']=journal_ids
        partner = []
        partner_ids = self.od_partner_ids
        for part in partner_ids:
            partner.append(part.id)
        data['form']['partner'] = partner
        print('filters-------------------------------------------------------')
        print(data['form'])
        return data
        
    def get_header_details(self,data):
        period1 = str(data['form']['6']['name'])
        period2 = str(data['form']['5']['name'])
        period3 = str(data['form']['4']['name'])
        period4 = str(data['form']['3']['name'])
        period5 = str(data['form']['2']['name'])
        period6 = str(data['form']['1']['name'])
        period7 = str(data['form']['0']['name'])
        if self.od_is_slab:
            period7= '+'+str(self.od_period_lenght6)
            period6= ''+str(self.od_period_lenght5)+'-'+str(self.od_period_lenght6)
            period5 = ''+str(self.od_period_lenght4)+'-'+str(self.od_period_lenght5)
            period4 = ''+str(self.od_period_lenght3)+'-'+str(self.od_period_lenght4)
            period3 = ''+str(self.od_period_lenght2)+'-'+str(self.od_period_lenght3)
            period2 = ''+str(self.od_period_lenght1)+'-'+str(self.od_period_lenght2)
            period1 = ''+str(0)+'-'+str(self.od_period_lenght1)
        header = ['Partners','Not Due',period1,period2,period3,period4,period5,period6,period7,'Total']
        return header   

    def get_excel_filters(self,data,sheet,style2,style_filter):
        filter_col_index = 0
        sheet.write(0,0,'Filter By',style2)
        if self.od_group_id:
            group_name = self.od_group_id and self.od_group_id.name or 'None'
            sheet.write(2,filter_col_index,group_name,style_filter)
            sheet.write(1,filter_col_index,'Group',style2)
            filter_col_index += 1
        if self.od_sub_group_id:
            sub_group_name = self.od_sub_group_id and self.od_sub_group_id.name or 'None'
            sheet.write(2,filter_col_index,sub_group_name,style_filter)
            sheet.write(1,filter_col_index,'Sub Group',style2)
            filter_col_index += 1
        if self.salesman_id:
            salesman_name = self.salesman_id and self.salesman_id.name or 'None'
            sheet.write(2,filter_col_index,salesman_name,style_filter)
            sheet.write(1,filter_col_index,'Salesman',style2)
            filter_col_index += 1
        if self.od_area_id:
            area_name = self.od_area_id and self.od_area_id.name or 'None'
            sheet.write(2,filter_col_index,area_name,style_filter)
            sheet.write(1,filter_col_index,'Area',style2)
            filter_col_index += 1
        sheet.write(1,filter_col_index,'As On Date',style2)
        sheet.write(2,filter_col_index,data['form']['date_from'],style_filter)
        return sheet

    def print_excel_report(self):
        filename= 'PartnerAging.xls'
        data = self.get_data_for_xls()
        header = self.get_header_details(data)
        
        account_type = ['receivable']
        date_from = data['form']['date_from']
        target_move = data['form']['target_move']
        od_period_lenght1 = data['form']['od_period_lenght1']
        od_period_lenght2 = data['form']['od_period_lenght2'] 
        od_period_lenght3 = data['form']['od_period_lenght3']
        od_period_lenght4 = data['form']['od_period_lenght4']
        od_period_lenght5 = data['form']['od_period_lenght5']
        od_period_lenght6 = data['form']['od_period_lenght6']
        od_is_slab = data['form']['od_is_slab']
        od_is_invoice_date = data['form']['od_is_invoice_date']
        partner = data['form']['partner']      
        if data['form']['result_selection'] == 'customer':
            account_type = ['receivable']
        elif data['form']['result_selection'] == 'supplier':
            account_type = ['payable']
        else:
            account_type = ['payable', 'receivable']
        od_account_id = data['form']['od_account_id']
        
        movelines, total, dummy = self.env['report.account.report_agedpartnerbalance']._get_partner_move_lines(account_type, date_from, target_move, data['form']['period_length'],od_period_lenght1,od_period_lenght2,od_period_lenght3,od_period_lenght4,od_period_lenght5,od_period_lenght6,od_is_slab,od_is_invoice_date,data['form'],partner,od_account_id)
        
        print("move lines>>>>>>>>>>>>>>>>>>>>>>>>")
        pprint(movelines)
        
        workbook= xlwt.Workbook(encoding="UTF-8")
        sheet= workbook.add_sheet('Aging Report Report',cell_overwrite_ok=True)
        style = xlwt.easyxf('font:height 400, bold True, name Arial; align: horiz center, vert center;borders: top medium,right medium,bottom medium,left medium')
        style_filter = xlwt.easyxf('font:name Arial; align: horiz center, vert center;')
        a = list(range(1,10))
        row = 1
        col =0
        header = header
        style2 = xlwt.easyxf('font: bold 1')
        
        sheet = self.get_excel_filters(data,sheet,style2,style_filter)
        print('total------------------------------------------')
        print(total)    
        for index,data in enumerate(header):
            sheet.write(4,index,data,style2)
        # Total
        # sheet.write(5,1,total[6],style2)
        # sheet.write(5,2,total[4],style2)
        # sheet.write(5,3,total[3],style2)
        # sheet.write(5,4,total[2],style2)
        # sheet.write(5,5,total[1],style2)
        # sheet.write(5,6,total[0],style2)
        # sheet.write(5,7,total[5],style2)
        # Total end
        for index,data in enumerate(movelines):
            name = data.get('name')
            sheet.write(index+6,col,name)
            not_due = data.get('direction')
            sheet.write(index+6,col+1,not_due)
            
            period1 = data.get('6')
            sheet.write(index+6,col+2,period1)
            
            period2 = data.get('5')
            sheet.write(index+6,col+3,period2)
            
            
            period3 = data.get('4')
            sheet.write(index+6,col+4,period3)
            
            period4 = data.get('3')
            sheet.write(index+6,col+5,period4)
            
            period5 = data.get('2')
            sheet.write(index+6,col+6,period5)
            
            period6 = data.get('1')
            sheet.write(index+6,col+7,period6)
            
            
            period7 = data.get('0')
            sheet.write(index+6,col+8,period7)
            
            total = data.get('total')
            sheet.write(index+6,col+9,total)
        fp = StringIO()
        workbook.save(fp)
        excel_file = base64.encodestring(fp.getvalue())
        self.excel_file = excel_file
        self.file_name =filename
        fp.close()
        return {
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'account.aged.trial.balance',
              'res_id': self.id,
              'type': 'ir.actions.act_window',
              'target': 'new'
              }
    
    def _print_report(self, data):
        result = super(AccountAgedTrialBalance,self)._print_report(data)
        data = self.pre_print_report(data)
        partner = []
        partner_ids = self.od_partner_ids
        for part in partner_ids:
            partner.append(part.id)
        data['form'].update(self.read(['od_is_invoice_date'])[0])
        data['form'].update(self.read(['od_is_slab'])[0])
        data['form'].update(self.read(['od_period_lenght1'])[0])
        data['form'].update(self.read(['od_period_lenght2'])[0])
        data['form'].update(self.read(['od_period_lenght3'])[0])
        data['form'].update(self.read(['od_period_lenght4'])[0])
        data['form'].update(self.read(['od_period_lenght5'])[0])
        data['form'].update(self.read(['od_period_lenght6'])[0])

        data['form'].update(self.read(['od_account_id'])[0])
        data['form']['partner'] = partner
        if self.od_is_slab:
            if self.od_period_lenght1 < 0 or self.od_period_lenght2 <=0 or self.od_period_lenght3 <=0 or self.od_period_lenght4 <=0 and self.od_period_lenght5 <=0 and self.od_period_lenght6 <=0:
                raise UserError(_('period length must be positive values'))
        return result
        
    
    def list_partner(self):
        partner_ids = []
        search_cond = []
        if self.salesman_id:
            search_cond.append(('user_id','=',self.salesman_id and self.salesman_id.id))
        partner_obj = self.env['res.partner'].search(search_cond)   
        for part in partner_obj:
            partner_ids.append(part.id)
        self.od_partner_ids = [(6,0,partner_ids)]
        return {
            'name': _('Aged Partner Balance'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.aged.trial.balance',
            'res_id': self.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        } 

#    
