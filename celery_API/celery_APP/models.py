from django.db import models
import datetime


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Tweets(BaseModel):
    # still need to add original tweet id from Tweet table foriegn key relation 

    tweet = models.CharField(max_length=255)
    # choices field, dict of choices pull down 
    approved = models.IntegerField(null=True, blank=True)
    scheduled_time = models.DateTimeField(default=None)
    sent_time = models.DateTimeField(default=None, null=True, blank=True)


class AppConfig(BaseModel):
    auto_send = models.BooleanField()
    
