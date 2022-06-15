# -*- coding: utf-8 -*-

{
    "name" : "Odoo Login With Microsoft Azure SSO",
    "version" : "15.0.0.0",
    "category": "Extra Tools",
    'summary': 'Microsoft Azure SSO Odoo Login Integration Microsoft Azure SSO Integration with Odoo Microsoft Azure SSO Integration Odoo login with Microsoft odoo login with Microsoft Azure SSO login on odoo Microsoft login Microsoft SSO Integration Microsoft Azure login',
    "description": """
                  	This odoo app helps user to integrate Microsoft Azure with Odoo, user can login into Odoo using Microsoft account using this microsoft sso integration odoo app, user can also see created partner with microsoft account details.
                    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.in",
    'price': 85,
    'currency': "EUR",
    "depends" : ['base','auth_oauth','auth_signup','web','portal'],
    "data": [
        'data/auth_oauth.xml'
    ],
    'live_test_url':'https://www.youtube.com/watch?v=ebUnHk_eStc&feature=youtu.be',
    "auto_install": False,
    "installable": True,
    'live_test_url':'https://youtu.be/IhEipFWvMzI',
    "images":['static/description/Banner.png'],

}

