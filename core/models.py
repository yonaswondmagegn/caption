from django.db import models
from django.utils import timezone

from cloudinary_storage.storage import RawMediaCloudinaryStorage

class YouTubeCaption(models.Model):
    url = models.CharField(max_length=225)
    caption = models.FileField(upload_to='captions',storage=RawMediaCloudinaryStorage())
    date = models.DateTimeField(default=timezone.now)
    



