from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError


from datetime import date


class HrJob(models.Model):
    _inherit = 'hr.job'

    budget = fields.Float('Budget')
    job_hired = fields.One2many('job.hire','job_hire_id','Job Hire')