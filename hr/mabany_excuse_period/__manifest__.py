# -*- coding: utf-8 -*-
{
    'name': "Mabany Ecuse Period",

    'summary': """
        Module for only max excuse period for specific situations 
        """,

    # any module necessary for this one to work correctly
    'depends': ['base','hr','mabany_hr_self_service'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_excuse.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
