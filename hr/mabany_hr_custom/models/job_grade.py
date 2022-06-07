from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class JobGrade(models.Model):
    _name = "job.grade"

    name = fields.Char('Name',required=True)