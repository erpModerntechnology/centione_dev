# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def passport_end_date_notify(self):
        for rec in self.search([]):
            if rec.passport_end_date:
                date_diff = abs(rec.passport_end_date - date.today())
                days = date_diff.days
                if days <= 30:
                    user = rec.env['res.users'].search([])
                    notification_ids = []
                    for emp in user:
                        if emp.has_group('mabany_hr_notifications.notify_user'):
                            notification_ids.append((0, 0, {
                                'res_partner_id': emp.partner_id.id,
                                'notification_type': 'inbox'
                            }))

                    rec.message_post(record_name='Passport End ',
                                      body="""Employee""" + ' ' + rec.name + """
                                <br> Passport Expiring after <br>""" + str(days) + ' ' + "Days"
                                      , message_type="notification",
                                      subtype_xmlid="mail.mt_comment",
                                      author_id=self.env.user.partner_id.id,
                                      notification_ids=notification_ids)


    def license_end_date_notify(self):
        for rec in self.search([]):
            if rec.license_end_date:
                date_diff = abs(rec.license_end_date - date.today())
                days = date_diff.days
                if days <= 30:
                    user = rec.env['res.users'].search([])
                    notification_ids = []
                    for emp in user:
                        if emp.has_group('mabany_hr_notifications.notify_user'):
                            notification_ids.append((0, 0, {
                                'res_partner_id': emp.partner_id.id,
                                'notification_type': 'inbox'
                            }))

                    rec.message_post(record_name='License End ',
                                      body="""Employee""" + ' ' + rec.name + """
                                <br> License Expiring after <br>""" + str(days) + ' ' + "Days"
                                      , message_type="notification",
                                      subtype_xmlid="mail.mt_comment",
                                      author_id=self.env.user.partner_id.id,
                                      notification_ids=notification_ids)

    def identify_end_date_notify(self):
        for rec in self.search([]):
            if rec.identify_end_date:
                date_diff = abs(rec.identify_end_date - date.today())
                days = date_diff.days
                if days <= 30:
                    user = rec.env['res.users'].search([])
                    notification_ids = []
                    for emp in user:
                        if emp.has_group('mabany_hr_notifications.notify_user'):
                            notification_ids.append((0, 0, {
                                'res_partner_id': emp.partner_id.id,
                                'notification_type': 'inbox'
                            }))

                    rec.message_post(record_name='Identification End ',
                                      body="""Employee""" + ' ' + rec.name + """
                                <br> Identification NO. Expiring after <br>""" + str(days) + ' ' + "Days"
                                      , message_type="notification",
                                      subtype_xmlid="mail.mt_comment",
                                      author_id=self.env.user.partner_id.id,
                                      notification_ids=notification_ids)

