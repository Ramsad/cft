from datetime import datetime, timedelta
import time
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
# from odoo.osv import fields, osv
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import odoo.addons.decimal_precision as dp


class od_camp_type(models.Model):
    _inherit = 'od.camp.type'

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     """
    #     v18-compliant _search override that:
    #       - Reads flags from context (collection / activities_id / product_id)
    #       - If collection is set and we have activities_id, restrict results to the
    #         type_ids referenced in that activity's camp_line
    #       - If collection is set but we have neither activities_id nor product_id,
    #         return no records
    #     """
    #     ctx = dict(self.env.context or {})
    #     dom = list(domain or [])
    #
    #     if ctx.get("collection"):
    #         activities_id = ctx.get("activities_id")
    #         product_id = ctx.get("product_id")
    #         # If collection and no activities_id/product_id → empty result
    #         if not activities_id and not product_id:
    #             dom.append(("id", "=", 0))
    #         elif activities_id:
    #             activity = self.env["od.activities"].browse(activities_id)
    #             type_ids = activity.camp_line.mapped("type_id").ids
    #             if type_ids:
    #                 dom.append(("id", "in", type_ids))
    #             else:
    #                 dom.append(("id", "=", 0))
    #
    #     return super()._search(dom, offset=offset, limit=limit, order=order, )
