from odoo import fields, models, api,_


class ModelName(models.Model):
    _inherit = 'product.template'

    payment = fields.Boolean(default=False)
