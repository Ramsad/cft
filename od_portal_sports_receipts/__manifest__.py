# -*- coding: utf-8 -*-
{
    "name": "Portal: Sports Receipts",
    "summary": "Expose od.sports.receipt to portal users (venue owners) with search & filters",
    "version": "18.0.1.0.3",
    "category": "Website/Portal",
    "author": "Your Team",
    "license": "LGPL-3",
    # IMPORTANT: Replace 'od_sports' below with the actual module that defines the model `od.sports.receipt`
    "depends": ["portal", "website", "mail", "analytic", "orchid_sports_v10"],
    "data": [
        "security/od_portal_security.xml",
        "security/ir.model.access.csv",
        "views/portal_templates.xml",
    ],
    "assets": {},
    "installable": True,
    "application": False,
}
