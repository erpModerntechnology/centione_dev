from odoo import fields, models, api


class AccountTaxInh(models.Model):
    _inherit = 'account.tax'

    with_holding_tax = fields.Boolean()
