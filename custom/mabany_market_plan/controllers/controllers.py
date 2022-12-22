# -*- coding: utf-8 -*-
# from odoo import http


# class MabanyMarketPlan(http.Controller):
#     @http.route('/mabany_market_plan/mabany_market_plan', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mabany_market_plan/mabany_market_plan/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mabany_market_plan.listing', {
#             'root': '/mabany_market_plan/mabany_market_plan',
#             'objects': http.request.env['mabany_market_plan.mabany_market_plan'].search([]),
#         })

#     @http.route('/mabany_market_plan/mabany_market_plan/objects/<model("mabany_market_plan.mabany_market_plan"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mabany_market_plan.object', {
#             'object': obj
#         })
