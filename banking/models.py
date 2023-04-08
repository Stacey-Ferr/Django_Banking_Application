from django.db import models

# Create your models here.
class Banking(models.Model):
    account_number = models.IntegerField()
    date = models.DateField('date')
    transaction_type = models.CharField(max_length=20)
    amount_usd = models.IntegerField()