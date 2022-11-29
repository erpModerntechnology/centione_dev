from odoo import fields, models, api


class SalesApprovals(models.Model):
    _name = 'res.approvals'
    _description = 'Approvals'

    type = fields.Selection([
        ("head_of_dep", "Head Of Department"),
        ("budget_control", "Budget Control"),
        ("finance_section_head", "Finance Section Head"),
    ])

    users = fields.Many2many('res.users')
