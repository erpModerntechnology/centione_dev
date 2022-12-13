from odoo import fields, models, api
import xlsxwriter
from io import BytesIO
import base64


class ErrandName(models.Model):
    _name = 'errand.name'

    name = fields.Char(required=True)


class accountMoveInh(models.Model):
    _inherit = 'account.move'

    errand_id = fields.Many2one(
        comodel_name='errand.name',
        string='اسم المامورية',
        required=False)



class accountTaxInh(models.Model):
    _inherit = 'account.tax'

    is_report = fields.Boolean(
        string='Value added tax',
        required=False)
