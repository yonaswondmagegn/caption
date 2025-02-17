from rest_framework.views import APIView
from django.core.files.base import ContentFile
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from rest_framework.response import Response
from rest_framework import status
from .models import YouTubeCaption
from .serializer import YoutubeCaptionSerializer
import requests


class CreateCaptionView(APIView):
    def post(self, request):
        video_id = request.data.get('url')
        if not video_id:
            return Response({'error': "url not found"}, status=status.HTTP_400_BAD_REQUEST)
   
            
        available_caption = YouTubeCaption.objects.filter(url = video_id).first()
        if available_caption:
            serialized_data = YoutubeCaptionSerializer(available_caption)
            return Response(data= serialized_data.data,status= status.HTTP_200_OK)


        def get_youtube_captions(video_id, languages=['en']):

            try:
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id, languages=languages)
                return transcript
            except TranscriptsDisabled:
                return []
            except Exception as e:  # Catch other potential errors
                return None

        def format_time(seconds):
            milliseconds = int((seconds * 1000) % 1000)
            seconds = int(seconds)
            minutes = seconds // 60
            seconds %= 60
            hours = minutes // 60
            minutes %= 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

        captions = get_youtube_captions(video_id)

        if captions is None:
            return Response({"error": "1 Can't found caption"}, status=status.HTTP_400_BAD_REQUEST)

        if not captions:
            print(video_id,'video id of 2')
            return Response({"error": " 2 Can't found caption"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            srt_content = ""
            for i, caption in enumerate(captions):
                start_time = caption['start']
                duration = caption['duration']
                end_time = start_time + duration

                # Format timestamps for SRT (HH:MM:SS,milliseconds)
                start_time_str = format_time(start_time)
                end_time_str = format_time(end_time)

                srt_content += f"{i + 1}\n"  # Caption number
                srt_content += f"{start_time_str} --> {end_time_str}\n"
                # Caption text and two newlines
                srt_content += f"{caption['text']}\n\n"

            # Save the .srt file to the database
            srt_file_name = f"{video_id}.srt"
            srt_file = ContentFile(
                srt_content.encode('utf-8'), name=srt_file_name)

            # Create a new YouTubeCaption instance
            youtube_caption = YouTubeCaption(url=video_id)
            youtube_caption.caption.save(srt_file_name, srt_file, save=True)

            return Response(
                {
                    "success": "Captions saved to database",
                    "caption": youtube_caption.caption.url
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
