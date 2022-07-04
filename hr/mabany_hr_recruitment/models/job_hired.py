from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError


from datetime import date


class JobHired(models.Model):
    _name = 'job.hire'

    date = fields.Date('Date')
    count = fields.Char('Count')
    job_hire_id = fields.Many2one('hr.job')