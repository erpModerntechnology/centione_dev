from odoo import fields, models, api,_
from odoo.exceptions import ValidationError



class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def create_reservation(self):
        vals = {}
        new_customer = 0
        for rec in self:
            # if not rec.partner_id:
            #     if rec.partner_name or rec.contact_name:
            vals.update({
                         'project_id': rec.market_plan_id.project_id.id,
                         'customer_id': rec.partner_id.id or False,
                         'broker_id': rec.broker_id.id,
                         'lead_id': rec.id,
                         'custom_type': 'Reservation',
                         })
            res = self.env['res.reservation'].create(vals)
            # new_customer_object = self.env['res.partner'].create(vals)
            #
            # new_customer = new_customer_object.id
            # rec.partner_id = new_customer

            # users = [user.id for user in rec.user_ids]
            # broker_ids = [broker.id for broker in rec.broker_ids]

            # res = self.env['ir.model.data'].get_object_reference('mabany_real_estate', 'reservation_form_view')
            # view_id = res and res[1] or False
            # print("rec.project_id.id :: %s", rec.project_id.id)
            # print("rec.team_id.user_id.partner_id.id :: %s", rec.team_id.user_id.partner_id.id)

            return {
                'name': _("Create Reservation"),
                'view_mode': 'form',
                # 'view_id': view_id,
                'view_type': 'form',
                'res_id': res.id,
                'res_model': 'res.reservation',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
            }


