# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class project_type(models.Model):
    _name = 'project.type'
    _rec_name = 'project_type'

    project_type = fields.Char(string="Project Type")


class status(models.Model):
    _name = 'status'
    _rec_name = 'status'

    status = fields.Char(string="Status")


class no_of_floors(models.Model):
    _name = 'no.of.floors'
    _rec_name = 'no_of_floors'

    no_of_floors = fields.Char(string="No. of Floors")
    description = fields.Text(string="Description")
    relation_field = fields.Many2one('project.project')


class ProjectProjectInherit(models.Model):
    _inherit = 'project.project'

    project_type = fields.Many2one('project.type', string='Project Type')
    location = fields.Char(string='Location')
    built_up_area = fields.Float(string='Built Up Area')
    land_area = fields.Float(string='Land Area')
    bg_image = fields.Binary(string='Background Image')
    no_of_floors = fields.One2many('no.of.floors', 'relation_field', string='No. of Floors')
    status = fields.Many2one('status', string='Status')
    licence = fields.Binary('Licence', attachment=True)
    prochure = fields.Binary('Prochure', attachment=True)
    contracts = fields.Binary('Contracts', attachment=True)
    units_plans = fields.Binary('Units Plans', attachment=True)
    reservation_form = fields.Binary('Reservation Form', attachment=True)
    layout = fields.Binary('Layout', attachment=True)

# class resan_project(models.Model):
#     _name = 'resan_project.resan_project'
#     _description = 'resan_project.resan_project'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
