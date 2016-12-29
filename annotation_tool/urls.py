from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^projects/$', views.ProjectsView.as_view(), name='projects'),
    url(r'^project/(?P<id>\d+)/$', views.ProjectView.as_view(), name='project'),
    url(r'^wavs/$', views.WavsView.as_view(), name='wavs'),
    url(r'^wav/(?P<id>\d+)/$', views.WavView.as_view(), name='wav'),
    url(r'^segments/$', views.SegmentsView.as_view(), name='segments'),
    url(r'^segment/(?P<id>\d+)/$', views.SegmentView.as_view(), name='segment'),
    url(r'^annotations/$', views.AnnotationsView.as_view(), name='annotations'),
    url(r'^annotation/(?P<id>\d+)/$', views.AnnotationView.as_view(), name='annotation'),
    url(r'^events/$', views.EventsView.as_view(), name='events'),
    url(r'^event/(?P<id>\d+)/$', views.EventView.as_view(), name='event'),
    url(r'^classes/$', views.ClassesView.as_view(), name='classes'),
    url(r'^class/(?P<id>\d+)/$', views.ClassView.as_view(), name='class'),
    url(r'^upload_data/$', views.UploadFileView.as_view(), name='upload_data'),
    url(r'^successful_upload/$', views.successful_upload, name='successful_upload'),
    url(r'^loginsignup/$', views.LoginSignup.as_view(), name='loginsignup'),
    url(r'^new_annotation/$', views.NewAnnotationView.as_view(), name='new_annotation'),
    url(r'^my_annotations/$', views.MyAnnotations.as_view(), name='my_annotations'),
    url(r'^create_event/$', views.create_event, name='create_event'),
    url(r'^update_event/$', views.update_event, name='update_event'),
    url(r'^update_end_event/$', views.update_end_event, name='update_end_event'),
    url(r'^remove_event/$', views.remove_event, name='remove_event'),
    url(r'^submit_annotation/$', views.submit_annotation, name='submit_annotation'),
    
]