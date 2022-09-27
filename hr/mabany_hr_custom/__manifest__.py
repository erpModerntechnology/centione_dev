# -*- coding: utf-8 -*-
{
    'name': "Mabany Hr Employee Customizations",

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
    'depends': ['base','hr','mabany_hr','hr_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
        'views/job_grade.xml',
        'views/job_divison.xml',
        'views/job_level.xml',
        'views/hr_contract.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}