# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class usermodel(models.Model):
    email=models.EmailField()
    password=models.CharField(max_length=10)
    repeatpassword=models.CharField(max_length=10)
    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now=True)