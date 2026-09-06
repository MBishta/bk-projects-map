from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import Project
from .serializers import PublicProjectSerializer


class PublicProjectListView(ListAPIView):
    serializer_class = PublicProjectSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = Project.objects.filter(is_public=True)