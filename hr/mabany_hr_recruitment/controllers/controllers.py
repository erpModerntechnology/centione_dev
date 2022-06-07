# -*- coding: utf-8 -*-
# from odoo import http


# class MabanyHrRecruitment(http.Controller):
#     @http.route('/mabany_hr_recruitment/mabany_hr_recruitment', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mabany_hr_recruitment/mabany_hr_recruitment/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mabany_hr_recruitment.listing', {
#             'root': '/mabany_hr_recruitment/mabany_hr_recruitment',
#             'objects': http.request.env['mabany_hr_recruitment.mabany_hr_recruitment'].search([]),
#         })

#     @http.route('/mabany_hr_recruitment/mabany_hr_recruitment/objects/<model("mabany_hr_recruitment.mabany_hr_recruitment"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mabany_hr_recruitment.object', {
#             'object': obj
#         })
