# -*- coding: utf-8 -*-
{
    'name': "mabany_real_estate",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

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
    'depends': ['base', 'account', 'project', 'product', 'analytic', 'account',
                'sale', 'check_management_15', 'account_batch_payment','sale_crm','crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/property_view.xml',
        'views/project_views.xml',
        'views/building.xml',
        'views/level.xml',
        'views/generate_build.xml',
        'views/phase_views.xml',
        'wizard/cancel_res_views.xml',
        'wizard/copy_line_views.xml',
        'wizard/merge_view.xml',
        'views/res_reservation.xml',
        'views/address_pay_strategy.xml',
        'views/customer_payment.xml',
        'views/sequence.xml',
        'views/approval.xml',
        'views/crm.xml',
        'views/install_type.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
