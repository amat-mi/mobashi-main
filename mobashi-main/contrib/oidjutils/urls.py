# coding: utf-8

from django.urls import re_path
from .views import qrcode_view

app_name = 'oidjutils'

urlpatterns = [
    re_path(r'^qrcode/(?P<key>.+)/$', qrcode_view, name='qrcode'),
    re_path(r'^qrcode/$', qrcode_view, name='qrcode'),
]
