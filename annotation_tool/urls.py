from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^projects/$', views.projects, name='projects'),
    url(r'^wavs/$', views.wavs, name='wavs'),
    url(r'^segments/$', views.segments, name='segments'),
    url(r'^annotations/$', views.annotations, name='annotations'),
    url(r'^events/$', views.events, name='events'),
    url(r'^upload_data/$', views.UploadFileView.as_view(), name='upload_data'),
    url(r'^successful_upload/$', views.successful_upload, name='successful_upload'),
    url(r'^loginsignup/$', views.loginsignup, name='loginsignup'),
    url(r'^new_annotation/$', views.new_annotation, name='new_annotation'),
    url(r'^completed_annotations/$', views.completed_annotations, name='completed_annotations'),
    url(r'^annotation_tool/$', views.annotation_tool, name='annotation_tool'),
]