# -*- coding: utf-8 -*-
{
    'name': "Mabany Hr Notifications",

    'summary': """
    Module responsible for notifying users 
        """,

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_contract'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/groups.xml',
        'views/hr_employee_notify.xml',
        'views/hr_contract_notify.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
