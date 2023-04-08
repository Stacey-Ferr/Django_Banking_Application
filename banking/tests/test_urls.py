from django.test import SimpleTestCase
from django.urls import reverse, resolve
from banking.views import upload_csv, similar_transaction

class TestUrls(SimpleTestCase):

    def test_upload_csv_url(self):
        url = reverse('upload_csv')
        self.assertEquals(resolve(url).func, upload_csv)

    def test_similar_transaction_url(self):
        url = reverse('similar_transaction')
        self.assertEquals(resolve(url).func, similar_transaction)