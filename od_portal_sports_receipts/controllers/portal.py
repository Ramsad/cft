# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class PortalSportsReceipt(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        Receipt = request.env['od.sports.receipt'].sudo()
        receipt_count = Receipt.search_count([])
        values.update({
            'receipt_count': receipt_count,
        })
        return values

    def _get_receipt_search_domain(self, kwargs):
        domain = []
        state = kwargs.get('state')
        if state in ('draft', 'confirm', 'cancel'):
            domain.append(('state', '=', state))

        search = kwargs.get('search')
        if search:
            domain.append(('name', 'ilike', search))

        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))

        return domain

    @http.route(['/my/collections', '/my/collections/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_collections(self, page=1, **kwargs):
        Receipt = request.env['od.sports.receipt'].sudo()
        domain = self._get_receipt_search_domain(kwargs)

        sortby = kwargs.get('sortby') or 'date_desc'
        sortings = {
            'date_desc': {'label': _('Date (newest first)'), 'order': 'date desc,id desc'},
            'date_asc':  {'label': _('Date (oldest first)'), 'order': 'date asc,id asc'},
            'name_asc':  {'label': _('Name (A→Z)'), 'order': 'name asc'},
            'name_desc': {'label': _('Name (Z→A)'), 'order': 'name desc'},
        }
        order = sortings[sortby]['order'] if sortby in sortings else 'id desc'

        receipts_count = Receipt.search_count(domain)
        page_size = 20
        pager = portal_pager(
            url="/my/collections",
            url_args=kwargs,
            total=receipts_count,
            page=page,
            step=page_size,
        )

        receipts = Receipt.search(domain, order=order, limit=page_size, offset=pager['offset'])

        values = self._prepare_portal_layout_values()
        values.update({
            'receipts': receipts,
            'page_name': 'collections',
            'pager': pager,
            'search': kwargs.get('search', ''),
            'date_from': kwargs.get('date_from', ''),
            'date_to': kwargs.get('date_to', ''),
            'state': kwargs.get('state', ''),
            'sortby': sortby,
            'sortings': sortings,
        })
        return request.render("od_portal_sports_receipts.portal_my_collections", values)
