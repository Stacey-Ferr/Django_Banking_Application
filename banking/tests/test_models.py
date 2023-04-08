from django.test import TestCase
from banking.models import Banking

class TestModels(TestCase):

    def setUp(self):
        self.banking = Banking.objects.create(
            account_number = 1234,
            date = "2023-01-02",
            transaction_type = 'Withdrawal',
            amount_usd = 2010
        )

    def test_date_label(self):
        banking = self.banking
        field_label = banking._meta.get_field('date').verbose_name
        self.assertEqual(field_label, 'date')
    
    def test_transaction_type_length(self):
        banking = self.banking
        max_length = banking._meta.get_field('transaction_type').max_length
        self.assertEqual(max_length, 20)