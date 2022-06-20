# -*- coding: utf-8 -*-
{
    'name': "Mabany Hr Reports",

    'summary': """
    Mabany Reports module
       """,

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'report/hr_payslip_new.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
