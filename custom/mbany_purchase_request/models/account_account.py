from odoo import fields, models, api


class Account_account(models.Model):
    _inherit = 'account.account'

    custody = fields.Boolean(default=False)
