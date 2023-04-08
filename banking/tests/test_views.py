from django.test import TestCase, Client
from django.urls import reverse
from banking.models import Banking
from django.contrib.auth.models import User, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import pandas as pd
import numpy as np
import csv
import os
from scipy.spatial.distance import cdist

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.relative_path = '/'
        test_user1 = User.objects.create_user(username='testuser1', password='ioi>jJWks-j928')
        test_user1.save()

        test_banking = Banking.objects.create(
            account_number = 1234,
            date = "2023-01-02",
            transaction_type = 'Withdrawal',
            amount_usd = 2010
        )
        test_banking.save()

    def test_upload_csv(self):
        response = self.client.get(reverse('upload_csv'))

        self.user = User.objects.get(username="testuser1")
        login = self.client.login(username='testuser1', password='ioi>jJWks-j928')
        self.assertTrue(login)
        self.assertEqual(self.user.username, 'testuser1')

        response = self.client.get(reverse('upload_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notAuthorized.html')

        self.assertFalse(self.user.has_perm('banking.add_banking'))
        self.user.user_permissions.add(Permission.objects.get(codename='add_banking'))

        self.user = User.objects.get(pk=self.user.pk)
        self.assertTrue(self.user.has_perm('banking.add_banking'))

        response = self.client.get(reverse('upload_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'uploadCsv.html')


        file_name = "test.csv"

        with open(file_name, "w") as file:
            writer = csv.writer(file)
            
            writer.writerow(["Account_Number", "Date", "Transaction_Type", "Amount_(USD)"])
            writer.writerow(
                [1234, "2022-12-18", "Deposit", 1082],
            )
            writer.writerow(
                [2879, "2012-04-20", "Transfer", 23000],
            )
            writer.writerow(
                [2980, "2017-10-29", "Withdrawal", 17982],
            )
        data = open(file_name, "rb")
        data = SimpleUploadedFile(
            content=data.read(), name=data.name, content_type="multipart/form-data"
        )

        
        url = self.relative_path + 'upload_csv/'
        res = self.client.put(url, {"file_name": data}, format="multipart")

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(response, 'uploadCsv.html')

        os.remove(file_name)


    def test_similar_transaction(self):
        response = self.client.get(reverse('similar_transaction'))

        self.user = User.objects.get(username="testuser1")
        login = self.client.login(username='testuser1', password='ioi>jJWks-j928')
        self.assertTrue(login)
        self.assertEqual(self.user.username, 'testuser1')

        response = self.client.get(reverse('similar_transaction'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notAuthorized.html')

        self.assertFalse(self.user.has_perm('banking.view_banking'))
        self.user.user_permissions.add(Permission.objects.get(codename='view_banking'))

        self.user = User.objects.get(pk=self.user.pk)
        self.assertTrue(self.user.has_perm('banking.view_banking'))

        response = self.client.get(reverse('similar_transaction'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'similarTransaction.html')

        db_records = [{'id': 70, 'account_number': 123456789, 'date': '2022-01-01', 'transaction_type': 'Deposit', 'amount_usd': 1000}, {'id': 71, 'account_number': 123456789, 'date': '2022-01-05', 'transaction_type': 'Withdrawal', 'amount_usd': 500}, {'id': 72, 'account_number': 123456789, 'date': '2022-01-07', 'transaction_type': 'Transfer', 'amount_usd': 250}, {'id': 73, 'account_number': 987654321, 'date': '2022-01-02', 'transaction_type': 'Deposit', 'amount_usd': 5000}, {'id': 74, 'account_number': 987654321, 'date': '2022-01-09', 'transaction_type': 'Withdrawal', 'amount_usd': 1000}, {'id': 75, 'account_number': 987654321, 'date': '2022-01-15', 'transaction_type': 'Transfer', 'amount_usd': 1500}, {'id': 76, 'account_number': 567890123, 'date': '2022-01-03', 'transaction_type': 'Deposit', 'amount_usd': 750}, {'id': 77, 'account_number': 567890123, 'date': '2022-01-08', 'transaction_type': 'Withdrawal', 'amount_usd': 200}, {'id': 78, 'account_number': 567890123, 'date': '2022-01-10', 'transaction_type': 'Transfer', 'amount_usd': 100}, {'id': 79, 'account_number': 345678901, 'date': '2022-01-04', 'transaction_type': 'Deposit', 'amount_usd': 2000}, {'id': 80, 'account_number': 345678901, 'date': '2022-01-11', 'transaction_type': 'Withdrawal', 'amount_usd': 800}, {'id': 81, 'account_number': 345678901, 'date': '2022-01-13', 'transaction_type': 'Transfer', 'amount_usd': 500}, {'id': 82, 'account_number': 890123456, 'date': '2022-01-06', 'transaction_type': 'Deposit', 'amount_usd': 3000}, {'id': 83, 'account_number': 890123456, 'date': '2022-01-12', 'transaction_type': 'Withdrawal', 'amount_usd': 1200}, {'id': 84, 'account_number': 890123456, 'date': '2022-01-16', 'transaction_type': 'Transfer', 'amount_usd': 1800}, {'id': 85, 'account_number': 234567890, 'date': '2022-01-07', 'transaction_type': 'Deposit', 'amount_usd': 1500}]
        db_records = pd.DataFrame.from_records(db_records)
        one_hot = pd.get_dummies(db_records['transaction_type'])
        temp_df = db_records.drop('id', axis=1)
        db_records = db_records.drop(['id', 'transaction_type'], axis=1)
        vector1 = pd.concat([db_records, one_hot], axis=1).to_numpy()
        numeric_dates = pd.to_datetime(vector1[:, 1]).astype(int)
        vector1 = np.column_stack((vector1[:, 0], numeric_dates, vector1[:, 2:]))
        vector1 = np.ascontiguousarray(vector1).astype('float32')

        new_array = [987654321, '2022-01-02', 1, 0, 0, 5000.0]
        vector2 = np.array(new_array)
        vector2 = vector2.reshape(1, -1)

        date_to_int = pd.to_datetime(vector2[:, 1]).astype(int)
        vector2 = np.column_stack((vector2[:, 0], date_to_int, vector2[:, 2:])).astype('float32')

        euclidean_dist = cdist(vector1, vector2, metric='euclidean')
        euclidean_dist = pd.DataFrame(euclidean_dist)
        indexes = euclidean_dist.nsmallest(4, 0).index
        similar_transactions = []
        for index in indexes:
            similar_transactions.append(temp_df.iloc[index])

        self.assertEqual(similar_transactions[0]['account_number'], 987654321)
        self.assertEqual(similar_transactions[0]['date'], '2022-01-02')
        self.assertEqual(similar_transactions[0]['transaction_type'], 'Deposit')
        self.assertEqual(similar_transactions[0]['amount_usd'], 5000.0)