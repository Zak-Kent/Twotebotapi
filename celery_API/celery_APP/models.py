from django.db import models

class Tweets(models.Model):
    id = models.AutoField(primary_key=True) 
    tweet = models.CharField(max_length=255)
    needs_approval = models.BooleanField()
    approved = models.IntegerField(null=True, blank=True)
