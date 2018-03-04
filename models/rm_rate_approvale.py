from odoo import models, api, fields, exceptions, _
from odoo.addons import decimal_precision as dp


class RateApproval(models.Model):
    """
    Base Abstract model for Rate Approval 
    """
    _name = 'rate.approval'
    _description = 'Rate Approval'
    _order = 'date desc, id desc'

    READONLY_STATES = {
        'approved_rate': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    title = fields.Char('Title', required=True)
    strength = fields.Integer(string='Strength')
    partner_id = fields.Many2one('res.partner', string='Name Of The Client', required=True, states=READONLY_STATES, change_default=True, track_visibility='always')
    partner_delivery_location = fields.Char(string='Delivery Location', required=True, states=READONLY_STATES, help="Delivery address.")
    date = fields.Date('Date', default=fields.Date.today)
    material_line = fields.One2many('rate.approval.material.line', 'rate_approval_id', string='Material Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    admixture_line = fields.One2many('rate.approval.admixture.line', 'rate_approval_id', string='Admixture Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    fixed_expense_line = fields.One2many('rate.approval.fixed.expense.line', 'rate_approval_id', string='Fixed Expense Line', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    unit_cost_line = fields.One2many('rate.approval.unit.cost', 'rate_approval_id', string='Unit Cost Line', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, states=READONLY_STATES, default=lambda self: self.env.user.company_id.currency_id.id)
    design_volume = fields.Float(string='Design Volume', readonly=True, compute='_compute_volume')
    prime_cost = fields.Monetary(string='Prime Cost', readonly=True, compute='_compute_prime_cost', currency_field='currency_id')
    total_cost = fields.Monetary(string='Total Cost', readonly=True, compute='_compute_total_cost', currency_field='currency_id')
    grand_total_cost = fields.Monetary(string='Grand Total Cost', readonly=True, compute='_compute_total_cost', currency_field='currency_id')
    present_price = fields.Monetary(string='Present Price/cft', required=True, default=0.0)

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

    @api.depends('material_line.price_total', 'admixture_line.price_total')
    def _compute_prime_cost(self):
        for ra in self:
            material_total_price = admixture_total_price = 0.0
            for line in ra.material_line:
                material_total_price += line.price_total

            for line in ra.admixture_line:
                admixture_total_price += line.price_total

            ra.update({
                'prime_cost': material_total_price + admixture_total_price
            })

    @api.depends('prime_cost', 'fixed_expense_line.amount')
    def _compute_total_cost(self):
        for ra in self:
            total_fixed_expense = 0.0
            for line in ra.fixed_expense_line:
                total_fixed_expense += line.amount

            ra.update({
                'total_cost': total_fixed_expense + ra.prime_cost,
                'grand_total_cost': total_fixed_expense + ra.prime_cost
            })

    @api.multi
    def button_print(self):
        pass


class BaseRateApprovalLine(models.AbstractModel):
    _name = 'base.rate.approval.line'

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
    rate_approval_id = fields.Many2one('rate.approval', string='Rate Approval Reference', index=True, required=True,
                                       ondelete='cascade')
    partner_id = fields.Many2one('res.partner', related='rate_approval_id.partner_id', string='Partner', readonly=True,
                                 store=True)
    currency_id = fields.Many2one(related='rate_approval_id.currency_id', store=True, string='Currency', readonly=True)


class RateApprovalMaterialLine(models.Model):
    _name = 'rate.approval.material.line'
    _inherit = ['base.rate.approval.line']
    _description = 'Rate Approval Material Line'


class RateApprovalAdmixtureLine(models.Model):
    _name = 'rate.approval.admixture.line'
    _inherit = ['base.rate.approval.line']
    _description = 'Rate Approval Admixture Line'


class BaseDynamicAmount(models.AbstractModel):
    _name = 'base.dynamic.amount'

    label = fields.Char('label', required=True)
    amount = fields.Monetary('amount', required=True, currency_field='currency_id')
    rate_approval_id = fields.Many2one('rate.approval', string='Rate Approval Reference', index=True, required=True,
                                       ondelete='cascade')
    currency_id = fields.Many2one(related='rate_approval_id.currency_id', store=True, string='Currency', readonly=True)


class FixedExpenseLine(models.Model):
    _name = 'rate.approval.fixed.expense.line'
    _inherit = ['base.dynamic.amount']
    _description = 'Rate Approval Fixed Expense Line'


class UnitCostCalculation(models.Model):
    _name = 'rate.approval.unit.cost'
    _inherit = ['base.dynamic.amount']
    _description = 'Rate Approval Unit Cost Calculation'

