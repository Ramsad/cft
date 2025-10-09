# Auto-upgraded manifest for Odoo 18 scaffolding
{'name': 'orchid Prepayment',
 'version': '18.1',
 'summary': 'Orchid Prepayment',
 'author': 'orchiderp',
 'website': 'http://www.yourcompany.com',
 'license': 'LGPL-3',
 'depends': ['account_accountant',
             'orchid_account_enhancement'],
 'data': [
     'security/ir.model.access.csv',
     'views/prepayment_lines_view.xml',
          'views/prepayment_lines_board_view.xml',
          'views/account_view.xml',
          'wizard/prepayment_wizard_view.xml',
          'views/prepaid_analysis_view.xml'],
 'demo': [],
 'qweb': []}
