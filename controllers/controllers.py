# -*- coding: utf-8 -*-
from odoo import http


class RateApproval(http.Controller):
    @http.route('/test', auth='public')
    def index(self, **kw):
        return "Hello from Ergo Ventures!!"

#     @http.route('/rate_approval/rate_approval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rate_approval.listing', {
#             'root': '/rate_approval/rate_approval',
#             'objects': http.request.env['rate_approval.rate_approval'].search([]),
#         })

#     @http.route('/rate_approval/rate_approval/objects/<model("rate_approval.rate_approval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rate_approval.object', {
#             'object': obj
#         })