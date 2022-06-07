from odoo import fields, models, api, _
from datetime import datetime, timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    automatic_overtime = fields.Boolean('Automatic Overtime')
