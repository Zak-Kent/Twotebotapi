from django.db import models
import datetime

APPROVAL_CHOICES = (
    (0, 'Needs_action'),
    (1, 'Approved'),
    (2, 'Denied'),
)

class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Tweets(BaseModel):
    # still need to add original tweet id from Tweet table foriegn key relation 
    tweet = models.CharField(max_length=255)
    approved = models.IntegerField(choices=APPROVAL_CHOICES, default=0)
    time_interval = models.IntegerField(null=True, blank=True)
    scheduled_time = models.DateTimeField(default=None, null=True, blank=True)
    task_scheduled = models.BooleanField(default=False)
    sent_time = models.DateTimeField(default=None, null=True, blank=True)


class AppConfig(BaseModel):
    auto_send = models.BooleanField()
    default_send_interval = models.IntegerField(default=15)
    
