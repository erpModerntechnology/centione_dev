# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrMedicalInsuranceInherit(models.Model):
    _inherit = 'hr.medical.insurance'

    family_grade_ids = fields.One2many('medical.grade.family', 'medical_id', string='Family Grade')


class HrMedicalLines(models.Model):
    _name = 'medical.grade.family'

    grade_id = fields.Many2one('hr.grade', string='Grade', required=1)
    medical_id = fields.Many2one('hr.medical.insurance', string='Medical Insurance')
    spouse = fields.Float('Spouse')
    child = fields.Float('Child')
    on_company = fields.Boolean()
