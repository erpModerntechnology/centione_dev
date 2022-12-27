# -*- coding: utf-8 -*-
# from odoo import http


# class ResanProject(http.Controller):
#     @http.route('/mabany_project/mabany_project/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/resan_project/resan_project/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('resan_project.listing', {
#             'root': '/resan_project/resan_project',
#             'objects': http.request.env['resan_project.resan_project'].search([]),
#         })

#     @http.route('/resan_project/resan_project/objects/<model("resan_project.resan_project"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('resan_project.object', {
#             'object': obj
#         })
