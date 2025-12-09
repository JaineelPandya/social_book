from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from .models import UploadedFile
from .serializers import UploadedFileSerializer


class MyFilesList(APIView):
    """Return a list of files uploaded by the authenticated user.

    Authentication: Token (djoser + rest_framework.authtoken)
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        files = UploadedFile.objects.filter(user=request.user, is_active=True)
        serializer = UploadedFileSerializer(files, many=True, context={'request': request})
        return Response(serializer.data)


class MyFileDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            file_obj = UploadedFile.objects.get(pk=pk)
        except UploadedFile.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Only allow owner or if visibility allows
        if file_obj.user != request.user and file_obj.visibility == 'private':
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UploadedFileSerializer(file_obj, context={'request': request})
        return Response(serializer.data)
