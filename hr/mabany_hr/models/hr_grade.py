from odoo import models, fields, api, _


class HrGrade(models.Model):
    _name = 'hr.grade'

    name = fields.Char()
