# -*- coding: utf-8 -*-
{
    'name': "Mabany Portal Termination",

    'summary': """
        Submit and Review Termination for portal users""",

    'description': """
        Submit and Review Termination for portal users,

    """,

    'author': "Centione",
    'website': "http://www.centione.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web','portal','website','hr','mabany_hr_end_service'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode

    # 'qweb': [
    #     'static/src/xml/timestamp_button.xml',
    # ],

    'js': ['static/src/js/timestamp_button.js'],
}
