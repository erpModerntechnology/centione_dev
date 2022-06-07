from odoo import models, fields, api, _


class missing_penalty_line(models.Model):
    _name = 'missing.penalty.line'
    _order = 'id asc, sequence asc'

    sequence = fields.Integer(required=True)
    penalty_rate = fields.Float()
    resource_calendar_id = fields.Many2one('resource.calendar')