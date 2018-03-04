# -*- coding: utf-8 -*-
from odoo import models, api, fields, exceptions, _
from odoo.addons import decimal_precision as dp


class BlockRateApproval(models.Model):
    """
       Base Abstract model for Rate Approval 
       """
    _name = 'rate.approval.block'
    _description = 'Block Rate Approval'
    _order = 'date desc, id desc'

    READONLY_STATES = {
        'approved_rate': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char(string='Product Name')
    piece = fields.Integer(string='Piece per Batch')
    reference = fields.Char(string='Ref')
    strength = fields.Integer(string='Strength')
    partner_id = fields.Many2one('res.partner', string='Name Of The Client', required=True, states=READONLY_STATES,
                                 change_default=True, track_visibility='always')
    partner_delivery_location = fields.Char(string='Delivery Location', required=True, states=READONLY_STATES,
                                            help="Delivery address.")
    date = fields.Date('Date', default=fields.Date.today)
    material_line = fields.One2many('rate.approval.block.material.line', 'rate_approval_id', string='Material Lines',
                                    states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)

    unit_cost_line = fields.One2many('rate.approval.block.unit.cost', 'rate_approval_id', string='Unit Cost Line',
                                     states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, states=READONLY_STATES,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    overhead_percentage = fields.Float(string='Overhead Percentage')
    overhead = fields.Monetary(compute='_compute_overhead', string='Overhead Amount', store=True,
                               currency_field='currency_id')
    making_cost = fields.Monetary(compute='_compute_making_cost', string='Making Cost Per Batch', store=True,
                                  currency_field='currency_id')

    design_volume = fields.Float(string='Design Volume', readonly=True, compute='_compute_volume')
    prime_cost = fields.Monetary(string='Prime Cost', readonly=True, compute='_compute_prime_cost',
                                 currency_field='currency_id')
    final_cost = fields.Monetary(string='Final Cost Per Pcs', required=True, default=0.0)
    selling_price = fields.Monetary(string='Selling Price Per Pcs', required=True, default=0.0)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Rate Confirmed'),
        ('rate_approve', 'Rate Approved'),
        ('done', 'Lock'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def button_cancel(self):
        self.write({'write': 'cancel'})

    @api.multi
    def button_approve(self):
        if not self.user_has_groups('rate_approval.group_md'):
            raise exceptions.ValidationError(_("You do not have rights to approve this item."))
        self.write({'state': 'done'})

    @api.multi
    def button_confirm(self):
        for rate in self:
            if rate.state not in ['draft']:
                continue
            if rate.user_has_groups('rate_approval.group_md'):
                rate.button_approve()
            else:
                rate.write({'state': 'rate_approve'})
        return True

    @api.depends('material_line.product_qty')
    def _compute_volume(self):
        for ra in self:
            volume = 0.0
            for line in ra.material_line:
                volume += line.product_qty

            ra.update({
                'design_volume': volume
            })

    @api.depends('material_line.price_total')
    def _compute_prime_cost(self):
        for ra in self:
            material_total_price = 0.0
            for line in ra.material_line:
                material_total_price += line.price_total

            ra.update({
                'prime_cost': material_total_price
            })

    @api.depends('overhead_percentage', 'prime_cost')
    def _compute_overhead(self):
        for oh in self:
            overhead = (oh.overhead_percentage / 100) * oh.prime_cost
            oh.update({
                'overhead': round(overhead, 2)
            })

    @api.depends('overhead', 'prime_cost')
    def _compute_making_cost(self):
        for oh in self:
            oh.update({
                'making_cost': round(oh.overhead + oh.prime_cost, 2)
            })



    @api.multi
    def button_print(self):
        pass


class BaseRateApprovalLine(models.Model):
    _name = 'rate.approval.block.material.line'
    _description = 'Rate Approval Material Line - Block'

    @api.depends('product_qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.update({
                'price_total': line.product_qty * line.price_unit,
            })

    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom = fields.Many2one('product.uom', string='Unit Volume', required=True)
    product_id = fields.Many2one('product.product', string='Product', change_default=True, required=True)
    price_unit = fields.Float(string='Rate, Taka', required=True, digits=dp.get_precision('Product Price'))
    price_total = fields.Monetary(compute='_compute_amount', string='Total Amount', store=True,
                                  currency_field='currency_id')
    rate_approval_id = fields.Many2one('rate.approval.block', string='Rate Approval Reference', index=True, required=True,
                                       ondelete='cascade')
    partner_id = fields.Many2one('res.partner', related='rate_approval_id.partner_id', string='Partner', readonly=True,
                                 store=True)
    currency_id = fields.Many2one(related='rate_approval_id.currency_id', store=True, string='Currency', readonly=True)


class BaseDynamicAmount(models.Model):
    _name = 'rate.approval.block.unit.cost'
    _description = 'Rate Approval Unit Cost Calculation'

    label = fields.Char('label', required=True)
    amount = fields.Monetary('amount', required=True, currency_field='currency_id')
    rate_approval_id = fields.Many2one('rate.approval.block', string='Rate Approval Reference', index=True, required=True,
                                       ondelete='cascade')
    currency_id = fields.Many2one(related='rate_approval_id.currency_id', store=True, string='Currency', readonly=True)

