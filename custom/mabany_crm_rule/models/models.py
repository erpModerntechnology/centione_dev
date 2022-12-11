from odoo import models, fields, api, _


class CRMRule(models.Model):
    _inherit = 'crm.lead'

    users = fields.Many2many('res.users', 'crm_user_rel', string='Users', tracking=True)
