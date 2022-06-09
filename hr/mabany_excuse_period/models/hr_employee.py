from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

from datetime import datetime,timedelta
import calendar


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    max_excuse_period = fields.Float(default=6.0)