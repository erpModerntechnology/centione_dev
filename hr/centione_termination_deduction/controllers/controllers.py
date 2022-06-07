# -*- coding: utf-8 -*-
# from odoo import http


# class CentioneTerminationDeduction(http.Controller):
#     @http.route('/centione_termination_deduction/centione_termination_deduction', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/centione_termination_deduction/centione_termination_deduction/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('centione_termination_deduction.listing', {
#             'root': '/centione_termination_deduction/centione_termination_deduction',
#             'objects': http.request.env['centione_termination_deduction.centione_termination_deduction'].search([]),
#         })

#     @http.route('/centione_termination_deduction/centione_termination_deduction/objects/<model("centione_termination_deduction.centione_termination_deduction"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('centione_termination_deduction.object', {
#             'object': obj
#         })
