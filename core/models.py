from django.db import models
from django.utils import timezone


class YouTubeCaption(models.Model):
    url = models.CharField(max_length=225)
    caption = models.FileField(upload_to='captions')
    type = models.CharField(choices=(('A','AUTO-GENERATED'),('W','WRITEN-CAPTION')),default='A')
    date = models.DateTimeField(default=timezone.now)
    



