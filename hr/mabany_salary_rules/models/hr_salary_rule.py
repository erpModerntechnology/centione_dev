from odoo import models, fields, api



class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    terminated = fields.Boolean('Terminated')