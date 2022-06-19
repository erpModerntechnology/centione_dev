from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class JobDivison(models.Model):
    _name = "job.divison"

    name = fields.Char('Name',required=True)