# -*- coding: utf-8 -*-
# Part of TechUltra Solutions. See LICENSE file for full copyright and licensing details.

{
    'name': "Assign Salesperson Odoo",
    'version': '15.0.0.0',
    'author': "TechUltra Solutions",
    'website': "http://www.techultrasolutions.com",
    'category': 'API',
    'license': 'AGPL-3',
    'depends': ['crm'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/assign_salesperson_wizard.xml',
        'views/crm_stage.xml'

    ],
    'images': ['static/description/banner.jpg'],

    'installable': True,
    'application': True,
}
