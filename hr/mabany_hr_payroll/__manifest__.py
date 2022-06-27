# -*- coding: utf-8 -*-
{
    'name': "Mabany Payroll",

    'summary': """
       """,

    'description': """
        * Payslip batch report.
    """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll','mabany_hr_payroll_base','mabany_hr_attendance_base'],

    # always loaded
    'data': [
        'views/hr_payslip_run.xml',
        'views/hr_salary_rules.xml',
    ],
}