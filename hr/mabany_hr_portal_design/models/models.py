# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class mabany_hr_portal_design(models.Model):
#     _name = 'mabany_hr_portal_design.mabany_hr_portal_design'
#     _description = 'mabany_hr_portal_design.mabany_hr_portal_design'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
