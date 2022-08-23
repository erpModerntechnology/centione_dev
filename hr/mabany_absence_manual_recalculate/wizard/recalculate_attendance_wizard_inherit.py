# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime
import datetime as delta
import datetime as time


class recalculate_attendance_wizard_inherit(models.TransientModel):
    _inherit = 'recalculate.attendance.wizard'

    recalculate_absence=fields.Boolean(string='Absence')


    def recalculate_data(self):
        self=self.sudo()

        super(recalculate_attendance_wizard_inherit, self).recalculate_data()
        self.env.cr.commit()

        #recalculate absence
        if self.recalculate_absence:
            self.env['hr.attendance'].manual_recalculate_absence(self.start_date)
            self.env.cr.commit()





