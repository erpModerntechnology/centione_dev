# -*- coding: utf-8 -*-
# from odoo import http


# class MabanyCrmCustomization(http.Controller):
#     @http.route('/mabany_crm_customization/mabany_crm_customization', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mabany_crm_customization/mabany_crm_customization/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mabany_crm_customization.listing', {
#             'root': '/mabany_crm_customization/mabany_crm_customization',
#             'objects': http.request.env['mabany_crm_customization.mabany_crm_customization'].search([]),
#         })

#     @http.route('/mabany_crm_customization/mabany_crm_customization/objects/<model("mabany_crm_customization.mabany_crm_customization"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mabany_crm_customization.object', {
#             'object': obj
#         })
