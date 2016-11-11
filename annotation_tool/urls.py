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
]