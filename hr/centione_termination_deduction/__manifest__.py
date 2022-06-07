# -*- coding: utf-8 -*-
{
    'name': "Centione Termination Deduction",

    'summary': """
        Module for deducing basic and allowances from terminated employee contract
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','centione_hr_payroll_base','hr_payroll','hr','hr_work_entry_contract','hr_contract'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/hr_salary_rule.xml',
        'views/hr_salary_rule.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
