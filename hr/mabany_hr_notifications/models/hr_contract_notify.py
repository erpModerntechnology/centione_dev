from datetime import date

from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def contract_end_date_notify(self):
        for rec in self.search([]):
            if rec.date_end:
                date_diff = abs(rec.date_end - date.today())
                days = date_diff.days
                if days <= 90:
                    user = rec.env['res.users'].search([])
                    notification_ids = []
                    for emp in user:
                        if emp.has_group('mabany_hr_notifications.notify_user'):
                            notification_ids.append((0, 0, {
                                'res_partner_id': emp.partner_id.id,
                                'notification_type': 'inbox'
                            }))

                    rec.message_post(record_name='Contract End ',
                                      body="""Employee""" + ' ' + rec.name + """
                                <br> Contract Expiring after <br>""" + str(days) + ' ' + "Days"
                                      , message_type="notification",
                                      subtype_xmlid="mail.mt_comment",
                                      author_id=self.env.user.partner_id.id,
                                      notification_ids=notification_ids)