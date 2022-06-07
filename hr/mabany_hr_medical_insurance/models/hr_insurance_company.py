from odoo import models, fields, api, _


class HrInsuranceCompany(models.Model):
    _name = 'hr.insurance.company'

    name = fields.Char()
