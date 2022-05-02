from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import PosLog
from .serializers import PosLogSerializer

class PoslogListView(APIView):
    '''
    작성자 : 남기윤
    (POST) /api/pos
    '''

    def post(self, request):
        data = request.data
        serializer = PosLogSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)