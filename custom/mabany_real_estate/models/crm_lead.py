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
    def create_request_reservation(self):
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
                         'sale_person_id_2': rec.user_id.id,
                         # 'custom_type': 'Reservation',
                         })
            res = self.env['request.reservation'].create(vals)
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
                'name': _("Create Request Reservation"),
                'view_mode': 'form',
                # 'view_id': view_id,
                'view_type': 'form',
                'res_id': res.id,
                'res_model': 'request.reservation',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
            }

    def action_open_leads(self):
        """ Open meeting's calendar view to schedule meeting on current opportunity.
            :return dict: dictionary value for created Meeting view
        """
        self.ensure_one()
        res_ids = self.env['res.reservation'].search([('lead_id', '=', self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("mabany_real_estate.reservation_list_action")
        action['context'] = {
            'default_lead_id': self.id,
        }
        action['domain'] = [('id', 'in', res_ids.ids)]
        return action
    def action_open_req(self):
        """ Open meeting's calendar view to schedule meeting on current opportunity.
            :return dict: dictionary value for created Meeting view
        """
        self.ensure_one()
        res_ids = self.env['request.reservation'].search([('lead_id', '=', self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("mabany_real_estate.rsreservation_list_action")
        action['context'] = {
            'default_lead_id': self.id,
        }
        action['domain'] = [('id', 'in', res_ids.ids)]
        return action
    count_reservation = fields.Integer(compute='count_reservation_recs')
    count_req_reservation = fields.Integer(compute='count_req_reservation_recs')

    def count_reservation_recs(self):
        for rec in self:
            count = self.env['res.reservation'].search_count([('lead_id', '=', rec.id)])
            rec.count_reservation = count
    def count_req_reservation_recs(self):
        for rec in self:
            count = self.env['request.reservation'].search_count([('lead_id', '=', rec.id)])
            rec.count_req_reservation = count




