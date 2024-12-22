from django.urls import include, path
from rest_framework import routers
from courses.views import ReviewViewSet

router = routers.DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
