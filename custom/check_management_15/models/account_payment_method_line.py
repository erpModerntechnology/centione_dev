from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class accountPaymentMethodLine(models.Model):
    _inherit = 'account.payment.method.line'

    is_base = fields.Boolean(string="Is Base",  )
