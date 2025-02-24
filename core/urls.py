from django.urls import path, include
from .views import CreateCaptionView, YouTubeVideosViewSet
from rest_framework_nested import routers

# Initialize the router
router = routers.DefaultRouter()

# Register the ViewSet with the router
router.register('videos', YouTubeVideosViewSet)

# Define the urlpatterns
urlpatterns = [
    path('yt/', CreateCaptionView.as_view()),  # Add a trailing slash for consistency
    path('', include(router.urls)),  # Include the router's URLs
]