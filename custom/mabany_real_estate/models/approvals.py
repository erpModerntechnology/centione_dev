from odoo import fields, models, api


class SalesApprovals(models.Model):
    _name = 'reservation.approvals'
    _description = 'Approvals'

    type = fields.Selection([
        ('reserved', 'Reserved'),
        ('finance_approval', 'Finance Approval'),
        ('request_approval', 'Request Approval'),
        ('contracted', 'Contracted'),
        ('operation_signature', 'Operation Signature'),
        ('legal', 'Legal'),
        ('finance_delivered', 'Finance Delivered'),
        ('engineering_comment', 'Engineering Comment'),
        ('co_approval', 'Co Approval'),
        ('customer_service', 'Customer Service'),
        ('legal_final_accept', 'Legal Final Accept')
    ])

    users = fields.Many2many('res.users')
