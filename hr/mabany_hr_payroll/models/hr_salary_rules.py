from odoo import api, fields, models, _

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    new_seq = fields.Integer('New Sequence')