# -*- coding: utf-8 -*-
{
    'name': "Mabany HR Medical Insurance",

    'summary': """
        """,

    'description': """
    """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mabany_hr', 'hr_payroll'],

    # always loaded
    'data': [
        'data/salary_rule.xml',
        'views/hr_employee.xml',
        'views/hr_medical_insurance.xml',
        'views/hr_insurance_company.xml',
        'views/hr_life_insurance.xml',
        'security/ir.model.access.csv',
    ],
}