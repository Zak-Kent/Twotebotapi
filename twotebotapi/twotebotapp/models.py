from django.db import models
from django.contrib.postgres.fields import ArrayField
from datetime import datetime, timedelta


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

    def save(self, *args, **kwargs):
        """
        Will calc and write tweet scheduled time when a tweet is approved
        """
        if self.approved == 1 and self.scheduled_time is None:
            if self.time_interval is None:
                try:
                    # if the AppConfig table is empty this will throw DoesNotExist
                    wait_time = AppConfig.objects.latest("id").default_send_interval   
                except:
                    # if no wait_time in AppConfig default to 15 mins
                    wait_time = 15
            else: 
                wait_time = self.time_interval
            eta = datetime.utcnow() + timedelta(minutes=wait_time)
            self.scheduled_time = eta
        super(Tweets, self).save(*args, **kwargs)

class AppConfig(BaseModel):
    auto_send = models.BooleanField()
    default_send_interval = models.IntegerField(default=15)
    ignore_users = ArrayField(models.BigIntegerField())


# ----------------------------------------------------------------------
# models needed for streaming tweets and saving those objects
class StreamedTweet(BaseModel):
    id_str = models.CharField(max_length=256, db_index=True, default='')
    user = models.ForeignKey('User', blank=True, null=True)
    source = models.CharField(max_length=256, blank=True, null=True)
    text = models.CharField(max_length=256, blank=True, null=True)
    location = models.CharField(max_length=256, blank=True, null=True)
    favorite_count = models.IntegerField(default=-1, null=True)


class User(models.Model):
    id = models.AutoField(primary_key=True)
    id_str = models.CharField(max_length=256, db_index=True, default='')
    screen_name = models.CharField(max_length=256, blank=True, null=True)
    verified = models.IntegerField(blank=True, null=True)
    time_zone = models.CharField(max_length=256, blank=True, null=True)
    utc_offset = models.IntegerField(blank=True, null=True)
    protected = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=256, blank=True, null=True)
    lang = models.CharField(max_length=256, blank=True, null=True)
    followers_count = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(null=True)
    statuses_count = models.IntegerField(blank=True, null=True)
    friends_count = models.IntegerField(blank=True, null=True)
    favourites_count = models.IntegerField(default=-1, null=True)

    