from tkinter import CASCADE
from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()


class Project(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    gitlabProjectId = models.CharField(max_length=200)
    gitlabAccessToken = models.CharField(max_length=256)
