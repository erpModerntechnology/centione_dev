# -*- coding: utf-8 -*-
{
    'name': "Invoice Taxes Report XLSX",

    'author': "Centione",
    'website': "http://www.centione.com",

    'depends': ['base', 'account'],

    'data': [
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/res_partner.xml',
        'views/account_tax.xml',
        'reports/report_wiz.xml',
        'reports/with_holding_tax_report.xml',
    ],
}
