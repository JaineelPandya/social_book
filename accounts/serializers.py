from rest_framework import serializers
from .models import UploadedFile


class UploadedFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedFile
        fields = [
            'id', 'title', 'description', 'file_url', 'year_published',
            'cost', 'visibility', 'is_active', 'uploaded_at', 'file_size',
        ]

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request is not None:
            return request.build_absolute_uri(obj.file.url)
        if obj.file:
            return obj.file.url
        return None
