from django.urls import path
from . import api

urlpatterns = [
    path('my-files/', api.MyFilesList.as_view(), name='api_my_files'),
    path('my-files/<int:pk>/', api.MyFileDetail.as_view(), name='api_my_file_detail'),
]
