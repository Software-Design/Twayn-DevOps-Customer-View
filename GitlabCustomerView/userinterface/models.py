from tkinter import CASCADE
from django.db import models


class Customer(models.Model):

    def __str__(self):
        return '{} ({})'.format(self.name, self.email)

    name = models.CharField(max_length=200)
    email = models.EmailField()


class Project(models.Model):

    def __str__(self):
        return '{} ({})'.format(self.name, self.gitlabProjectId)

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    assignees = models.ManyToManyField('Employee')
    name = models.CharField(max_length=200)
    gitlabProjectId = models.CharField(max_length=200)
    gitlabAccessToken = models.CharField(max_length=256)


class Employee(models.Model):

    def __str__(self):
        return '{} ({})'.format(self.name, self.gitlabUsername)

    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    gitlabUsername = models.CharField(max_length=200)