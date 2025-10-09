#-*- coding:utf-8 -*-
# from odoo import tools
# from odoo.osv import osv, fields
# from odoo.tools.translate import _
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError




class od_venue(models.Model):
    _name = 'od.venue'
    _description = 'Venue'


    # def _get_image(self):
    #     result = dict.fromkeys(ids, False)
    #     for obj in self.env['od.venue'].browse(self._ids):
    #         result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
    #     return result

    # def _set_image(self):
    #     return self.write({'image': tools.image_resize_image_big(value)})

    
    name = fields.Char(string='Name',required="1",)
    commission = fields.Float(string='Commission',)
    management_id = fields.Many2one('res.partner', string='Management',domain=[('supplier_rank', '>=', 1)])
    analytic_acc_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    owner = fields.Many2one('res.partner', string='Owner',domain=[('supplier_rank', '>=', True)])
    image =  fields.Binary("Image",help="This field holds the image used as image for the facility, limited to 1024x1024px.")
    image_medium =  fields.Binary(
        string="Medium-sized image",
        help="Medium-sized image of the Facility. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved, "\
             "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")
    image_small =  fields.Binary(
        string="Small-sized image",
        help="Small-sized image of the Facility. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")


    def unlink(self):
        unlink_ids = []
        for obj in self.env['od.venue'].browse(self._ids):
            activities_ids = self.env['od.activities'].search([('venue_id','=',obj.id)])
            if activities_ids:
                raise AccessError(_('You cannot Delete it,it is already used in activities'))
            scheduled_ids = self.env['od.scheduled'].search([('venue_id','=',obj.id)])
            if scheduled_ids:
                raise AccessError(_('You cannot Delete it,it is already used in schedule'))
            unlink_ids.append(obj.id)
        # return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        return super(od_venue, self).unlink()



    def create(self, vals):
        if vals.get('name'):
            analytic_acc_id = self.env['account.analytic.account'].create({'name':vals.get('name'),'plan_id':1,
                                                                                        'code':vals.get('name')
                                                                                        })
            vals['analytic_acc_id'] = analytic_acc_id.id
        return super(od_venue, self).create(vals)

    def write(self, vals):
        if vals.get('name'):
            analytic_rec = self.env['od.venue'].browse(self._ids)[0].analytic_acc_id
            analytic_acc_id = analytic_rec and analytic_rec.id
            name = vals.get('name') or self.env['od.venue'].browse(self._ids)[0].name
            self.env['account.analytic.account'].write({'name':name,'code':name})
        return super(od_venue, self).write(vals)

