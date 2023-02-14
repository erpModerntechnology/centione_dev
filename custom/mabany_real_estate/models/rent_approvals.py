from odoo import fields, models, api


class SalesApprovals(models.Model):
    _name = 'rent.approvals'
    _description = 'Approvals'

    type = fields.Selection([
        ('initial_rent', 'Initial Rent'),
        ('operation_approval', 'Operation Approval'),
        ('sales_manger', 'Sales Manager Approval'),
        ('finance_approval', 'Finance Approval'),
        ('rented', 'Rented')
    ])

    users = fields.Many2many('res.users')
