# -*- coding: utf-8 -*-
{
    'name': "Mabany Hr Recruitment",

    'summary': """
    Module for recuritment customizations
        """,

    # any module necessary for this one to work correctly
    'depends': ['base','hr_recruitment','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_applicant_inherit.xml',
        'views/hr_job.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
