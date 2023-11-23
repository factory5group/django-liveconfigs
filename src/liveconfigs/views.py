from rest_framework import status as http_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ConfigRow
from .serializers import ConfigRowSerializer


class ConfigRowViewSet(viewsets.ViewSet):
    serializer_class = ConfigRowSerializer
    queryset = ConfigRow.objects.all()
    permission_classes = (IsAuthenticated,)

    @action(methods=['post'], url_name='import_config', url_path='import_config', detail=False)
    def import_config(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.update_configs()
        return Response(status=http_status.HTTP_200_OK, data={})
