from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class JobLevel(models.Model):
    _name = "job.level"

    name = fields.Char('Name',required=True)