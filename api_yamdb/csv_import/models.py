from django.db import models


class Anyimport(models.Model):
    id = models.CharField(max_length=150)
    name = models.CharField(max_length=150, blank=True, null=True)
    slug = models.CharField(max_length=150, blank=True, null=True)
    author = models.CharField(max_length=150, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    text = models.TextField(
        max_length=1000, blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    pub_date = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
