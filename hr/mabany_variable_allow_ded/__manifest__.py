# -*- coding: utf-8 -*-
{
    'name': "Hr Variable Allowance Deduction",

    'summary': """
        """,

    'description': """
    """,

    'author': "Centione",
    'website': "www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mabany_hr_payroll_base', 'mabany_hr_contract', 'mabany_hr_variable_allowance_deduction'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
