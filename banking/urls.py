from django.urls import path
from .views import *
from django.views.generic import TemplateView

urlpatterns = [
    path("upload_csv/", upload_csv, name="upload_csv"),
    path("similar_transaction/", similar_transaction, name="similar_transaction"),
]