from odoo import models, fields, api, _
from odoo.exceptions import UserError

from odoo.http import request
import base64


class hr_leave_allocation_inherit(models.Model):
    _inherit = 'hr.leave.allocation'

    rest_leaves = fields.Float(compute='_compute_rest_leaves')

    @api.depends('max_leaves', 'leaves_taken')
    def _compute_rest_leaves(self):
        for allocation in self:
            allocation.rest_leaves = allocation.max_leaves - allocation.leaves_taken
