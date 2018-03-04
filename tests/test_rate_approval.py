from odoo.exceptions import AccessError
from odoo.tests import TransactionCase


class TestRateApproval(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super(TestRateApproval, self).setUp(*args, **kwargs)
        user_demo = self.env.ref('base.user_demo')
        self.env = self.env(user=user_demo)

        return result

    def test_per_user_record_rules(self):
        RateApproval = self.env(['rate.approval'])
        rate_approval = RateApproval.sudo().create({'title': 'test', 'strength': 300, 'partner_id': 4, 'partner_delivery_location': 'Dhaka'})
        with self.assertRaises(AccessError):
            RateApproval.browse(['rate_approval.id']).title
