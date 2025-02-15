from rest_framework import serializers
from .models import YouTubeCaption


class YoutubeCaptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeCaption
        fields = '__all__'

