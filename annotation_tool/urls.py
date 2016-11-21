from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^projects/$', views.projects, name='projects'),
    url(r'^wavs/$', views.wavs, name='wavs'),
    url(r'^segments/$', views.segments, name='segments'),
    url(r'^annotations/$', views.annotations, name='annotations'),
    url(r'^events/$', views.events, name='events'),
    url(r'^classes/$', views.classes, name='classes'),
    url(r'^upload_data/$', views.UploadFileView.as_view(), name='upload_data'),
    url(r'^successful_upload/$', views.successful_upload, name='successful_upload'),
    url(r'^loginsignup/$', views.loginsignup, name='loginsignup'),
    url(r'^new_annotation/$', views.new_annotation, name='new_annotation'),
    url(r'^resume_annotation/$', views.resume_annotation, name='resume_annotation'),
    url(r'^my_annotations/$', views.my_annotations, name='my_annotations'),
    url(r'^save_annotation/$', views.save_annotation, name='save_annotation'),
    
]