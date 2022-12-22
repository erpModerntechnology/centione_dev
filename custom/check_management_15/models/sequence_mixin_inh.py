# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from collections import defaultdict
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import ast
import json
import re
import warnings



class sequenceMixin(models.AbstractModel):
    _inherit = 'sequence.mixin'

    def _constrains_date_sequence(self):
        # Make it possible to bypass the constraint to allow edition of already messed up documents.
        # /!\ Do not use this to completely disable the constraint as it will make this mixin unreliable.
        constraint_date = fields.Date.to_date(self.env['ir.config_parameter'].sudo().get_param(
            'sequence.mixin.constraint_start_date',
            '1970-01-01'
        ))
        for record in self:
            date = fields.Date.to_date(record[record._sequence_date_field])
            sequence = record[record._sequence_field]
            if sequence and date and date > constraint_date:
                format_values = record._get_sequence_format_param(sequence)[1]
                if (
                    format_values['year'] and format_values['year'] != date.year % 10**len(str(format_values['year']))
                    or format_values['month'] and format_values['month'] != date.month
                ):
                    print("dddddddddddddddeweqeqw")
                    print("dddddddddddddddeweqeqw",format_date(self.env, date))
                    print("dddddddddddddddeweqeqw",record._fields[record._sequence_date_field]._description_string(self.env))
                    print("dddddddddddddddeweqeqw",record._fields[record._sequence_field]._description_string(self.env))
                    print("dddddddddddddddeweqeqw",sequence)
                    pass_con = False
                    account_move_obj = self.env['account.move']
                    account_move  = account_move_obj.search([('name', '=', sequence)], limit=1)
                    print("dddd",account_move)
                    for line in account_move.line_ids:
                        print("dddd", line.payment_id.payment_method_id.code)
                        print("dddd", line.payment_id.partner_type)
                        if line.payment_id.payment_method_id.code == 'check_printing' and line.payment_id.partner_type == 'supplier':
                            pass_con = True
                        elif line.payment_id.payment_method_id.code == 'batch_payment' and line.payment_id.partner_type == 'customer':
                            pass_con = True
                    if not account_move :
                        raise ValidationError(_(
                            "The %(date_field)s (%(date)s) doesn't match the %(sequence_field)s (%(sequence)s).\n"
                            "You might want to clear the field %(sequence_field)s before proceeding with the change of the date.ddddd",
                            date=format_date(self.env, date),
                            sequence=sequence,
                            date_field=record._fields[record._sequence_date_field]._description_string(self.env),
                            sequence_field=record._fields[record._sequence_field]._description_string(self.env),
                        ))
