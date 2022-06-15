# # -*- coding: utf-8 -*-
#
# import logging
# import re
# import time
# import datetime
# from datetime import datetime as dt
# from datetime import timedelta as t_d
# from collections import namedtuple
# from openerp.exceptions import Warning
# from openerp.exceptions import UserError
# from odoo.exceptions import ValidationError
# from odoo import models, fields, api , _
# from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
# _logger = logging.getLogger(__name__)
# _logger2 = logging.getLogger(__name__)
#
# class HolidaysTypePortal(models.Model):
#     _inherit = "hr.leave.type"
#
#     def _compute_leaves_portal(self):
#         data_days = {}
#         employee_id = self.env['hr.employee'].search([('user_id', '=', self._context.get('uid'))], limit=1).id
#
#         if employee_id:
#             data_days = self._get_days_request()
#
#         for holiday_status in self:
#             result = data_days[1] if data_days else {}
#             holiday_status.max_leaves = result.get('max_leaves', 0)
#             holiday_status.leaves_taken = result.get('leaves_taken', 0)
#             holiday_status.remaining_leaves = result.get('remaining_leaves', 0)
#             holiday_status.virtual_remaining_leaves = result.get('virtual_remaining_leaves', 0)
#
#     def name_get_portal(self):
#         res = []
#         for record in self:
#             name = record.name
#             if not record.max_leaves:
#                 name = "%(name)s (%(count)s)" % {
#                     'name': name,
#                     'count': _('%g remaining out of %g') % (
#                     record.virtual_remaining_leaves or 0.0, record.max_leaves or 0.0)
#                 }
#             res.append((record.id, name))
#         return res