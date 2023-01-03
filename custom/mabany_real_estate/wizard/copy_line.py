# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
import datetime
from datetime import datetime, date,timedelta

class CopyLine(models.TransientModel):
    _name = 'copy.line'



    number = fields.Integer(
        string='Number', 
        required=False)

    # @api.multi
    def action_apply(self):
        self.ensure_one()
        res = self.env['payment.strg'].browse(self._context.get('active_ids', []))
        for line in range(self.number):
            res.copy()