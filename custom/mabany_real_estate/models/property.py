# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)
class PropertyCategory(models.Model):
    _name = "property.exception"
    _description = "Unit Exception"

    name = fields.Text('Name', required=True, translate=True)


class PropertyCategory(models.Model):
    _name = "property.category"
    _description = "Unit Category"

    name = fields.Char('Name', required=True, translate=True)

class PropertyType(models.Model):
    _name = "property.type"
    _description = "Unit Types"

    name = fields.Char('Name', required=True, translate=True)
    cate_id = fields.Many2one(comodel_name="property.category", string="Property Type", required=True, )
    multi_image = fields.Boolean(string="Add  Multiple Images?")
    images_type = fields.One2many('biztech.product.images', 'type_id',
                              string='Images')
    sellable = fields.Float(string="Sellable BUA m²",  required=False, )

class PropertyLocation(models.Model):
    _name = "property.location"
    _description = "Unit Locations"

    name = fields.Char('Unit location', required=True, translate=True)


class PropertyLocation(models.Model):
    _name = "property.finished.type"
    _description = "Unit Finishing Type"

    name = fields.Char('Finishing Type', required=True, translate=True)


class PropertyDesign(models.Model):
    _name = "property.design"
    _description = "Unit Design"

    name = fields.Char('Unit Design', required=True, translate=True)

class latlng_line(models.Model):
    _name = "latlng.line"
    lat= fields.Float('Latitude', digits=(9, 6),required=True)
    lng= fields.Float('Longitude', digits=(9, 6),required=True)
    url= fields.Char('URL', digits=(9, 6),required=True)
    city_id= fields.Many2one('res.country.state', 'City')
    unit_id= fields.Many2one('product.product', 'Unit')


class ProductImages(models.Model):
    _name = 'biztech.product.images'
    _description = "Add Multiple Image in Product"

    name = fields.Char(string='Title', translate=True)
    alt = fields.Char(string='Alt', translate=True)
    attach_type = fields.Selection([('image', 'Image'), ('video', 'Video')],
                                   default='image',
                                   string="Type")
    image = fields.Binary(string='Image')
    video_type = fields.Selection([('youtube', 'Youtube'),
                                   ('vimeo', 'Vimeo'),
                                   ('html5video', 'Html5 Video')],
                                  default='youtube',
                                  string="Video media player")
    cover_image = fields.Binary(string='Cover image',
                                # required=True,
                                help="Cover Image will be show untill video is loaded.")
    video_id = fields.Char(string='Video ID')
    video_ogv = fields.Char(string='Video OGV', help="Link for ogv format video")
    video_webm = fields.Char(string='Video WEBM', help="Link for webm format video")
    video_mp4 = fields.Char(string='Video MP4', help="Link for mp4 format video")
    sequence = fields.Integer(string='Sort Order')
    product_tmpl_id = fields.Many2one('product.product', string='Product')
    type_id = fields.Many2one('property.type', string='Unit Type')
    more_view_exclude = fields.Boolean(string="More View Exclude")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_product_template_type(self):
        res = super(ProductTemplate, self)._get_product_template_type()
        if 'property' not in [item[0] for item in res]:
            res.append(('property', _('Property')))
        return res

    type = fields.Selection(selection_add=[('property', 'Property')], tracking=True,
                            )


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _description = 'Real estate Unit'

    is_property = fields.Boolean(string="Is Unit", )
    property_code = fields.Char(string="Unit Code", required=False, )
    is_name = fields.Boolean(string="", compute="_compute_name")

    # @api.onchange('property_code')
    # def onchange_method_property_code(self):
    #     self.name = self.property_code

    def _compute_name(self):
        for rec in self:
            rec.name = rec.property_code

    # @api.multi
    def available_property(self):
        for rec in self:
            if rec.state == 'blocked':
                rec.state = 'available'
            else:
                raise UserError('Please Check Selected Lines, Only Properties in Blocked Status Can be Available')

    property_no = fields.Integer(string="Unit Number", copy=False)
    project_id = fields.Many2one('project.project', _('Project'))
    phase_id = fields.Many2one('project.phase', _('Phase'), store=True)

    # @api.depends("project_id")
    # @api.onchange('phase_id', 'project_id')
    # def onchange_method_phase_id(self):
    #     for rec in self:
    #         _logger.info("self.project_id.id :: %s", rec.project_id.id)
    #         state = self.env['res.country.state'].search([('projects_ids', '=', rec.project_id.id),
    #                                                       ], limit=1)
    #         property_account_income_id = self.env['account.account'].search(
    #             [('id', '=', rec.project_id.property_account_income_id.id),
    #              ], limit=1)
    #         rec.state_id = state.id
    #         rec.country_id = state.country_id.id
    #
    #         rec.property_account_income_id = property_account_income_id.id
    #
    #         return {
    #             'domain': {'phase_id': [('project_id', '=', rec.project_id.id)]}
    #         }

    cate_id = fields.Many2one(comodel_name="property.category", string="Category", )
    exception_id = fields.Many2one(comodel_name="property.exception", string="Exception")

    state = fields.Selection(
        [('draft', _('Draft')),
         ('available', _('Available')),
         ('reserved', _('Reserved')),
         ('contracted', _('Contracted')),
         ('blocked', _('Holded'))], string="Status", default='draft', copy=False)
    is_contracted = fields.Boolean(string="is Contracted", compute="_compute_is_contract")
    north = fields.Float('North')
    view = fields.Float('View')
    ch_view = fields.Float('C.H View')
    ch_distance = fields.Float('C .H Distance')
    floor = fields.Float('Floor')
    bldg_type = fields.Float('Bldg. Type')
    un_area = fields.Float('Un .Area')
    advantage = fields.Float(compute='calc_advantage',store=True)
    pricelist_ids = fields.One2many('unit.pricelist','product_id')
    @api.depends('north','view','ch_view','ch_distance','floor','bldg_type','un_area','unit_price')
    def calc_advantage(self):
        for r in self:
            percent = r.north+r.view+r.ch_view+r.ch_distance+r.floor+r.bldg_type+r.un_area
            r.advantage = r.unit_price * (percent/100)

    pricing_after_premium = fields.Float(compute='calc_pricing_after_premium',store=True)

    @api.depends('unit_price','advantage')
    def calc_pricing_after_premium(self):
        for r in self:
            r.pricing_after_premium = r.unit_price + r.advantage

    def _compute_is_contract(self):
        for rec in self:
            rec.is_contracted = True
            account_move_line = self.env['account.move.line'].search([('product_id', '=', rec.id),
                                                                      ], limit=1)
            if account_move_line.move_id.state == 'posted':
                rec.state = "contracted"

    type_of_property_id = fields.Many2one('property.type', _('Unit Type'))

    @api.onchange('type_of_property_id')
    def onchange_method_type_of_property_id(self):
        for rec in self:
            if rec.type_of_property_id:
                rec.multi_image = rec.type_of_property_id.multi_image
                rec.images = rec.type_of_property_id.images_type
                rec.cate_id = rec.type_of_property_id.cate_id
                rec.sellable = rec.type_of_property_id.sellable
                # rec.name = rec.type_of_property_id.name
                # for line in rec.type_of_property_id.images_type:

    multi_image = fields.Boolean(string="Add  Multiple Images?")
    images = fields.One2many('biztech.product.images', 'product_tmpl_id',
                             string='Images')
    # part city country
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')

    @api.onchange('state_id')
    def _onchange_state(self):
        # self._onchange_compute_probability(optional_field_name='state_id')
        if self.state_id:
            self.country_id = self.state_id.country_id.id

    @api.onchange('country_id')
    def _onchange_country_id(self):
        # self._onchange_compute_probability(optional_field_name='country_id')
        # self.state_id = []
        res = {'domain': {'state_id': []}}
        if self.country_id:
            res['domain']['state_id'] = [('country_id', '=', self.country_id.id)]
        return res

    latlng_ids = fields.One2many('latlng.line', 'unit_id', string='LatLng List', copy=True)
    map = fields.Char('Map', digits=(9, 6))

    last_gps_latitude = fields.Float(string="", required=False, )
    last_gps_longitude = fields.Float(string="", required=False, )

    # part Area calculation part
    plot_area = fields.Float(string="Outdoor Area m²", required=False, )
    sellable = fields.Float(string="Gross Area", required=False, )
    # sellable = fields.Float(string="Gross Area", required=False, compute='get_gross', inverse='inverse_gross')
    price_m_a = fields.Float(string="Outdoor Price m²", required=False, )
    # price_m = fields.Float(string="BUA Price m²", required=False, )
    price_m = fields.Float(string="BUA Price m²", required=False, store=True)
    total_garden_area = fields.Float(string="Total Garden Area m²", required=False, )
    price_garden_new = fields.Float(string="Garden Price m²", store=True)
    price_garden_2 = fields.Float(string="Garden Price m²", compute="_compute_price_garden_2")
    price_garden_3 = fields.Float(string="Garden Price m²", )

    def inverse_gross(self):
        pass

    @api.onchange('ground_floor_area', 'first_floor_area', 'total_ground', 'total_first')
    def get_gross_area(self):
        for r in self:
            if r.is_duplex:
                sellable = r.ground_floor_area + r.first_floor_area
                if sellable == 0:
                    raise ValidationError('Gross Area must be greater than zero')
                else:
                    r.update({
                        'sellable': sellable,
                        'price_m': (r.total_ground + r.total_first) / sellable
                    })


    # @api.depends('total_ground', 'total_first', 'sellable')
    # def get_gross(self):
    #     for r in self:
    #         if r.is_duplex:
    #             if r.sellable == 0:
    #                 raise ValidationError('Gross Area must be greater than zero')
    #             else:
    #                 r.price_m = (r.total_ground + r.total_first) / r.sellable

    def _compute_price_garden_2(self):
        for rec in self:
            rec.price_garden_2 = rec.price_garden_new

    # price_garden2 = fields.Float(string="Garden Price m²",  required=False, )

    is_garage = fields.Boolean(string="Is Park ?", )
    price_garage_for_one = fields.Float(string="Price Per Park", required=False, )
    number_of_garage = fields.Integer(string="Number Of Park", required=False, default=1)
    back_yard = fields.Float(string="Back Yard m²", required=False, )
    front_yard = fields.Float(string="Front Yard m²", required=False, )
    maintenance_percent = fields.Float(string="Maintenance Percent", required=False, default=10)
    maintenance_amount = fields.Float(string="Maintenance Amount", required=False,
                                      compute='_compute_maintenance_amount')
    location_of_property_id = fields.Many2one('property.location', _('Unit Location'))
    is_finish = fields.Boolean(string="Are you going to finish?", )
    finish_of_property_id = fields.Many2one('property.finished.type', _('Finishing Type'))
    price_finishing_for_m = fields.Float(string="Price Finish For m²", required=False, )
    design_of_property_id = fields.Many2one('property.design', _('Unit Design'))
    is_pool = fields.Boolean(string="Is Pool ?", )
    price_pool_for_one = fields.Float(string="Price Per Pool", required=False, )
    number_of_pool = fields.Integer(string="Number Of Pool", required=False, default=1)
    price_profile = fields.Char(string="Pricing Profile ", required=False, )
    # finish calculation
    unit_price = fields.Float(string="Unit Price ", required=False, compute="_compute_unit_price", store=True)
    unit_price2 = fields.Float(string="Unit Price ", required=False, )
    is_garden = fields.Boolean(default=False)
    is_clubhouse = fields.Boolean(default=False)
    garden_amount = fields.Float()
    clubhouse_amount = fields.Float()

    @api.depends('price_m', 'sellable', 'unit_price2')
    def _compute_unit_price(self):
        for rec in self:
            if rec.price_m > 0:
                rec.unit_price = rec.price_m * rec.sellable
                if rec.unit_price != rec.unit_price2:
                    rec.update({
                        'unit_price2': rec.unit_price
                    })
                    rec.unit_price2 == rec.unit_price
            else:
                rec.unit_price = 0

    # @api.depends('maintenance_percent', 'final_unit_price')
    def _compute_maintenance_amount(self):
        for rec in self:
            rec.maintenance_amount = (rec.maintenance_percent / 100) * rec.final_unit_price

    finishing_price = fields.Float(string="Finishing Price ", required=False, compute="_compute_finishing_price",
                                   store=True)
    finishing_price2 = fields.Float(string="Finishing Price ", required=False)

    def _compute_finishing_price(self):
        for rec in self:
            if rec.is_finish == True:
                if rec.price_finishing_for_m > 0:
                    print('f1')
                    rec.finishing_price = rec.price_finishing_for_m * rec.sellable
                    if rec.finishing_price != rec.finishing_price2:
                        print('f2')
                        rec.update({
                            'finishing_price2': rec.finishing_price
                        })
                        rec.finishing_price2 == rec.finishing_price
                else:
                    print('f3')
                    rec.finishing_price = 0
            else:
                print('f4')
                rec.finishing_price = 0

    pool_price = fields.Float(string="Pool Price ", required=False, compute="_compute_pool_price", store=True)
    pool_price2 = fields.Float(string="Pool Price ", required=False)

    def _compute_pool_price(self):
        for rec in self:
            if rec.is_pool == True:
                if rec.price_pool_for_one > 0:
                    rec.pool_price = rec.price_pool_for_one * rec.number_of_pool
                    if rec.pool_price != rec.pool_price2:
                        rec.update({
                            'pool_price2': rec.pool_price
                        })
                        rec.pool_price2 == rec.pool_price
                else:
                    rec.pool_price = 0
            else:
                rec.pool_price = 0

    garage_price = fields.Float(string="Park Price ", required=False, compute="_compute_garage_price")
    garage_price2 = fields.Float(string="Park Price ", required=False)

    def _compute_garage_price(self):
        for rec in self:
            if rec.is_garage == True:
                if rec.price_garage_for_one > 0:
                    rec.garage_price = rec.price_garage_for_one * rec.number_of_garage
                    if rec.garage_price != rec.garage_price2:
                        rec.update({
                            'garage_price2': rec.garage_price
                        })
                        rec.garage_price2 == rec.garage_price
                else:
                    rec.garage_price = 0
            else:
                rec.garage_price = 0

    plot_price = fields.Float(string="Gross Price ", required=False, compute="_compute_area_price", store=True)
    outdoor_price = fields.Float(string="Outdoor Price ", required=False, compute="_compute_outdoor_price", store=True)
    plot_price2 = fields.Float(string="Outdoor Price ", required=False, )
    build_id = fields.Many2one('res.build')
    level = fields.Many2one('res.level','Level')
    sales_price_percentage = fields.Float()
    sales_price = fields.Float(compute='calc_sales_price',store=True)
    sales_pricelist = fields.Float()

    @api.depends('final_unit_price','sales_price_percentage')
    def calc_sales_price(self):
        for r in self:
            r.sales_price = (r.final_unit_price * r.sales_price_percentage) + r.final_unit_price
    def calc_sales_pricelist(self):
        for r in self.search([('state','not in',['reserved','contracted'])]):
                project_unit = self.env['product.product'].search([('project_id','=',self.project_id.id),('state','=','contracted')])
                unit_count = len(project_unit)
                for l in r.pricelist_ids:
                    if date.today() >= l.date_from and date.today() <= l.date_to and unit_count >= l.no_unit:
                        r.sales_pricelist = l.new_salesprice





    @api.depends('plot_area', 'price_m_a')
    def _compute_outdoor_price(self):
        for r in self:
            r.outdoor_price = r.plot_area * r.price_m_a

    @api.depends('plot_area', 'price_m_a', 'plot_price2')
    def _compute_area_price(self):
        for rec in self:
            rec.plot_price = rec.plot_area * rec.price_m_a
            if rec.plot_price != rec.plot_price2:
                rec.update({
                    'plot_price2': rec.plot_price
                })
                rec.plot_price2 == rec.plot_price

    @api.constrains('price_garage_for_one', 'is_garage')
    def validation_price_garage_for_one(self):
        print("self.is_garage :: %s", self.is_garage)
        if self.is_garage == True:
            if self.price_garage_for_one == 0.0:
                raise ValidationError(_(
                    "you must Enter Price For Garage!!"))

    @api.constrains('price_pool_for_one', 'is_pool')
    def validation_price_pool_for_one(self):
        if self.is_pool == True:
            if self.price_pool_for_one == 0.0:
                raise ValidationError(_(
                    "you must Enter Price For Pool!!"))

    @api.model
    def create(self, vals):

        vals['unit_price2'] = self.unit_price
        vals['finishing_price2'] = self.finishing_price
        vals['pool_price2'] = self.pool_price
        vals['plot_price2'] = self.plot_price
        vals['price_garden_3'] = self.price_garden_new
        vals['garage_price2'] = self.garage_price
        vals['detailed_type'] = 'service'

        picking_type = super(ProductProduct, self).create(vals)
        return picking_type

    final_unit_price = fields.Float(string="Final Unit Price ", required=False, compute="_compute_final_unit_price",
                                    store=True)

    @api.depends('price_m', 'sellable', 'finishing_price', 'pool_price', 'price_garden_new', 'outdoor_price',
                 'price_garage_for_one', 'number_of_garage','advantage','garden_amount','clubhouse_amount')
    def _compute_final_unit_price(self):
        for rec in self:
            rec.final_unit_price = ((rec.total_ground + rec.total_first) if rec.is_duplex else (
                    rec.price_m * rec.sellable))+rec.advantage+rec.garden_amount+rec.clubhouse_amount + rec.finishing_price + rec.pool_price + rec.price_garden_new +\
                                   rec.outdoor_price + (rec.price_garage_for_one * rec.number_of_garage)

    def update_state_to_available(self):
        for rec in self:
            rec.sudo().write({'state': 'available', 'resp_user_id': False})

    def update_state_to_blocked(self):
        for rec in self:
            rec.write({'state': 'blocked'})

    # @api.
    def update_state_to_not_available(self):
        for rec in self:
            rec.sudo().write({'state': 'not_available'})


    analytic_account_id = fields.Many2one(comodel_name="account.analytic.account", string="Analytic Account",
                                          required=False, readonly=True)

    def set_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def convert_to_available(self):
        for rec in self:
            # if rec.state in ['draft']:
            rec.state = 'available'
            req_id = self.env['account.analytic.account'].create({
                'name': self.name,
            })
            rec.analytic_account_id = req_id.id

    def convert_to_block(self):
        for rec in self:
            if rec.state in ['available', 'draft']:
                rec.state = 'blocked'

    def convert_to_draft(self):
        for rec in self:
            if rec.state in ['available']:
                rec.state = 'draft'

    def exception_do(self):
        for rec in self:
            rec.state = 'exception'

    def request_to_available(self):
        for rec in self:
            rec.state = 'available'
            req_id = self.env['account.analytic.account'].create({
                'name': self.name,
            })
            rec.analytic_account_id = req_id.id


    def request_to_rented(self):
        for rec in self:
            rec.state = 'rented'

    def approved_to_available(self):
        for rec in self:
            rec.state = 'approve'

    def create_request_reservation(self):
        _logger.info("create_request_reservation")

        req_id = self.env['request.reservation'].create({
            'date': datetime.now(),
            'project_id': self.project_id.id,
            'phase_id': self.phase_id.id,
            'property_id': self.id,
        })

        return {'name': (
            'Request Reservation'),
            'type': 'ir.actions.act_window',
            'res_model': 'request.reservation',
            'res_id': req_id.id,
            'view_type': 'form',
            'view_mode': 'form',
        }

    def create_reservation(self):
        res_res = self.env['res.reservation'].search([('property_id', '=', self.id),
                                                      ('state', 'in', ['reserved'])])
        if len(res_res) != 0:
            raise ValidationError(_(
                "Sorry .. you must Create One Reservation Form For Request Reservation for This Unit  %s!!") % self.property_id.name)

        req_id = self.env['res.reservation'].create({
            'date': datetime.now(),
            'project_id': self.project_id.id,
            'phase_id': self.phase_id.id,
            'property_id': self.id,
            'custom_type': 'Reservation',
            'state': 'draft',
        })
        # req_id.onchange_method_state()

        return {'name': ('Reservation'),
                'type': 'ir.actions.act_window',
                'res_model': 'res.reservation',
                'res_id': req_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                }

    def create_rent(self):
        _logger.info("create_rent")
        res_res = self.env['res.rent'].search([('property_id', '=', self.id),
                                               ('state', 'in', ['reserved'])])
        if len(res_res) != 0:
            raise ValidationError(_(
                "Sorry .. you must Create One Rent Form For Request Rent for This Unit  %s!!") % self.property_id.name)

        req_id = self.env['res.rent'].create({
            'date': datetime.now(),
            'project_id': self.project_id.id,
            'phase_id': self.phase_id.id,
            'property_id': self.id,
            'custom_type': 'rent',
            'state': 'draft',
        })
        # req_id.onchange_method_state()

        return {'name': (
            'Rent'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.rent',
            'res_id': req_id.id,
            'view_type': 'form',
            'view_mode': 'form',
        }

    counter_reservation = fields.Integer(string="", required=False, compute="_compute_counter_reservation")

    def _compute_counter_reservation(self):
        for rec in self:
            res = self.env['res.reservation'].search(
                [('property_id', '=', rec.id)])
            rec.counter_reservation = len(res)

    def action_view_partner_reservation(self):
        # self.ensure_one()
        print("enter here L>action_view_partner_reservation")
        action = self.env.ref('mabany_real_estate.reservation_list_action').read()[0]
        action['domain'] = [
            ('property_id', '=', self.id),
        ]
        action['context'] = {'default_property_id': self.id}
        print("action %s", action)
        return action

    def action_view_partner_reservation_new(self):
        # self.ensure_one()
        print("enter here L>action_view_partner_reservation")
        # action = self.env.ref('mabany_real_estate.reservation_list_action').read()[0]
        # action['domain'] = [
        #     ('property_id', '=', self.id),
        # ]
        # print("action %s",action)
        # return action
        return {
            'name': _('Reservation'),
            'view_mode': 'tree,form',
            'res_model': 'res.reservation',
            'type': 'ir.actions.act_window',
            'domain': [('property_id', '=', self.id), ('custom_type', '=', 'Reservation')],
            'target': 'current',
        }

    def action_show_rules(self):
        self.ensure_one()
        return {
            'name': _('Record Rules'),
            'view_mode': 'tree,form',
            'res_model': 'ir.rule',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False},
            'domain': [('id', 'in', self.groups_id.rule_groups.ids)],
            'target': 'current',
        }

    propert_account_id = fields.Many2one(comodel_name="account.account", string="Income Account", required=False, )

    is_req_res = fields.Boolean(string="Is Request Resveration", compute="_compute_view_button_create")
    is_res = fields.Boolean(string="Is Request Resveration", compute="_compute_view_button_create")
    #
    def _compute_view_button_create(self):
        for rec in self:
            req = self.env['request.reservation'].search(
                [('property_id', '=', rec.id), ("state", '!=', 'blocked')
                 ], limit=1)
            res = self.env['res.reservation'].search(
                [('property_id', '=', rec.id), ("state", '!=', 'blocked')
                 ], limit=1)
            if len(req) > 0:
                rec.is_req_res = True
            else:
                rec.is_req_res = False

            if len(res) > 0:
                rec.is_res = True
            else:
                rec.is_res = False
            print("rec.is_res :: %s", rec.is_res)
    net_sellable_bua = fields.Float(string='Net Area', compute='calc_net_sellable_bua', store=True)
    load_percentage = fields.Float(string='نسبه التحميل%')

    @api.depends('load_percentage', 'sellable')
    def calc_net_sellable_bua(self):
        for rec in self:
            rec.net_sellable_bua = ((100 - rec.load_percentage)/100) * rec.sellable
    is_duplex = fields.Boolean(string='Is Duplex')
    first_floor_area = fields.Float(string='First Floor Area')
    first_floor_prices = fields.Float(string='First Floor Prices')
    total_first = fields.Float(compute='calc_total_first')
    ground_floor_area = fields.Float(string='Ground Floor Area')
    ground_floor_prices = fields.Float(string='Ground Floor Price', store=True)
    total_ground = fields.Float(compute='calc_total_ground', store=True)

    @api.depends('first_floor_area', 'first_floor_prices')
    def calc_total_first(self):
        for r in self:
            r.total_first = r.first_floor_area * r.first_floor_prices

    @api.depends('ground_floor_area', 'ground_floor_prices')
    def calc_total_ground(self):
        for r in self:
            r.total_ground = r.ground_floor_area * r.ground_floor_prices


