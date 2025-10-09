# Odoo v10 → v18 Migration Audit & Scaffold

**Modules detected:** 11

## orchid_account_enhancement
- Manifest: normalized __manifest__.py
- Depends: account, report
- Python files: 28 (2to3 applied to 18)
- ⚠️ API flags:
  -  used (deprecated)
  -  used (removed; refactor)
  - iteritems/itervalues used
- 📦 XML/Assets flags:
  - Old <openerp> tag in views/account_branch.xml
  - Old <openerp> tag in views/account_cost_center.xml
  - Old <openerp> tag in views/account_division.xml
  - Old <openerp> tag in views/account_move_view.xml
  - Old <openerp> tag in wizard/od_overdue.xml

## orchid_account_reports_v10
- Manifest: normalized __manifest__.py
- Depends: account, orchid_account_enhancement
- Python files: 7 (2to3 applied to 2)

## orchid_asset_v10
- Manifest: normalized __manifest__.py
- Depends: base, account_asset, orchid_account_enhancement
- Python files: 8 (2to3 applied to 5)
- ⚠️ API flags:
  -  used (deprecated)
  - openerp import (rewritten to odoo)
  - osv legacy API used
- 📦 XML/Assets flags:
  - Old <openerp> tag in account_asset_view.xml

## orchid_bank_reconciliation_v10
- Manifest: normalized __manifest__.py
- Depends: account_accountant
- Python files: 5 (2to3 applied to 5)
- ⚠️ API flags:
  -  used (deprecated)
  -  used (removed; refactor)
  - openerp import (rewritten to odoo)
- 📦 XML/Assets flags:
  - Old <openerp> tag in views/account_bank_recon.xml
  - Old <openerp> tag in views/account_view.xml
  - Old <openerp> tag in views/bank_reconciliation_view.xml

## orchid_enterprise_theme
- Manifest: converted from __openerp__.py to __manifest__.py
- Depends: web
- Python files: 2 (2to3 applied to 0)
- 📦 XML/Assets flags:
  - Legacy assets bundle reference in views/assets.xml
- 🧩 JS flags:
  - Old JS module pattern in static/src/js/web_responsive.js

## orchid_prepayment_v10
- Manifest: normalized __manifest__.py
- Depends: account_accountant, orchid_account_enhancement
- Python files: 7 (2to3 applied to 5)
- ⚠️ API flags:
  -  used (deprecated)
  -  used (removed; refactor)
  - openerp import (rewritten to odoo)

## orchid_printscreen_v10
- Manifest: normalized __manifest__.py
- Depends: web
- Python files: 3 (2to3 applied to 0)
- 📦 XML/Assets flags:
  - Legacy assets bundle reference in views/orchid_printscreen_v10_view.xml
- 🧩 JS flags:
  - Old JS module pattern in static/src/js/orchid_printscreen_v10.js

## orchid_report_v10
- Manifest: normalized __manifest__.py
- Depends: report
- Python files: 5 (2to3 applied to 3)
- ⚠️ API flags:
  -  used (removed; refactor)
  - openerp import (rewritten to odoo)
  - osv legacy API used
- 📦 XML/Assets flags:
  - Old <openerp> tag in company_view.xml
  - Old <openerp> tag in od_ir_actions_report_xml_view.xml

## orchid_sports_v10
- Manifest: normalized __manifest__.py
- Depends: base, analytic, account, orchid_account_enhancement, orchid_vat_v10
- Python files: 39 (2to3 applied to 24)
- ⚠️ API flags:
  -  used (deprecated)
  -  used (removed; refactor)
  - iteritems/itervalues used
  - openerp import (rewritten to odoo)
  - osv legacy API used
- 📦 XML/Assets flags:
  - Old <openerp> tag in report/od_sports_activity_analysis_view.xml
  - Old <openerp> tag in report/od_sports_student_analysis_view.xml
  - Old <openerp> tag in report/payment_print_inherit.xml
  - Old <openerp> tag in views/od_activity_seq_view.xml
  - Old <openerp> tag in views/od_registration_from_program_view.xml
  - Old <openerp> tag in views/od_registration_seq_view.xml
  - Old <openerp> tag in views/od_registration_view.xml
  - Old <openerp> tag in views/od_schedule_view.xml
  - Old <openerp> tag in views/od_sports_receipt_seq_view.xml

## orchid_vat_v10
- Manifest: normalized __manifest__.py
- Depends: base, sale, account, purchase
- Python files: 9 (2to3 applied to 4)
- ⚠️ API flags:
  -  used (deprecated)
  -  used (removed; refactor)
  - openerp import (rewritten to odoo)

## orchid_year_closing_v10
- Manifest: normalized __manifest__.py
- Depends: base, account
- Python files: 5 (2to3 applied to 0)


---
## Next steps & common v10→v18 updates to complete manually

1. **Remove deprecated decorators**: Replace `` methods with recordset-safe implementations. Use `for rec in self:` or `self.ensure_one()` where needed.
2. **Drop ``**: Methods should support multiple records by default; the decorator is no longer used.
3. **Legacy API**: If any `osv`/`orm` remnants exist, port to `models.Model` with the environments API (`self.env`, `@api.depends`, `@api.constrains`).
4. **Python 3 nuances**: After auto 2to3, check string/bytes boundaries (`.decode()/.encode()`), iterators vs lists, and `super()` calls.
5. **Views/XML**: Ensure all root tags are `<odoo>`. Re-test view `xpath` targets against v18 base views; many got renamed/refactored.
6. **Assets**: The web asset pipeline changed. If you reference `web.assets_*`, move to the v18 `assets` manifest key and proper bundle slots.
7. **JS**: OWL is now standard. Legacy `odoo.define()` modules often need a rewrite to OWL components/services.
8. **Security**: Re-check ACL/record rules; models or fields renamed upstream can break rules silently.
9. **Accounting**: If modules touch `account`, expect **major** changes in models/taxes/reconciliation across versions. Plan dedicated testing.
10. **Testing**: Add basic tests using `odoo.tests` and run them under v18 to catch regressions early.
