# -*- coding: utf-8 -*-
# from odoo import http


# class MabanySalaryRules(http.Controller):
#     @http.route('/mabany_salary_rules/mabany_salary_rules', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mabany_salary_rules/mabany_salary_rules/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mabany_salary_rules.listing', {
#             'root': '/mabany_salary_rules/mabany_salary_rules',
#             'objects': http.request.env['mabany_salary_rules.mabany_salary_rules'].search([]),
#         })

#     @http.route('/mabany_salary_rules/mabany_salary_rules/objects/<model("mabany_salary_rules.mabany_salary_rules"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mabany_salary_rules.object', {
#             'object': obj
#         })
