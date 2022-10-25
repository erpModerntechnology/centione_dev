# -*- coding: utf-8 -*-
# from odoo import http


# class PowerhouseHrPortalDesign(http.Controller):
#     @http.route('/mabany_hr_portal_design/mabany_hr_portal_design', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mabany_hr_portal_design/mabany_hr_portal_design/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mabany_hr_portal_design.listing', {
#             'root': '/mabany_hr_portal_design/mabany_hr_portal_design',
#             'objects': http.request.env['mabany_hr_portal_design.mabany_hr_portal_design'].search([]),
#         })

#     @http.route('/mabany_hr_portal_design/mabany_hr_portal_design/objects/<model("mabany_hr_portal_design.mabany_hr_portal_design"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mabany_hr_portal_design.object', {
#             'object': obj
#         })
