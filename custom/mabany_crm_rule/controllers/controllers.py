# -*- coding: utf-8 -*-
# from odoo import http


# class GoldenCrmRule(http.Controller):
#     @http.route('/golden_crm_rule/golden_crm_rule/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/golden_crm_rule/golden_crm_rule/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('golden_crm_rule.listing', {
#             'root': '/golden_crm_rule/golden_crm_rule',
#             'objects': http.request.env['golden_crm_rule.golden_crm_rule'].search([]),
#         })

#     @http.route('/golden_crm_rule/golden_crm_rule/objects/<model("golden_crm_rule.golden_crm_rule"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('golden_crm_rule.object', {
#             'object': obj
#         })
