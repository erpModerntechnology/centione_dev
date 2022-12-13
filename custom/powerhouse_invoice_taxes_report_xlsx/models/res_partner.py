# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerInh(models.Model):
    _inherit = 'res.partner'

    national_id = fields.Char(
        string='ID', )

    errand_name = fields.Char()

    tax_file_no = fields.Char()
