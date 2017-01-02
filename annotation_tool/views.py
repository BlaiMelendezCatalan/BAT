import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponseRedirect
from rest_framework.generics import GenericAPIView, DestroyAPIView
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse

from annotation_tool import models
from annotation_tool.mixins import SuperuserRequiredMixin

from annotation_tool.serializers import ProjectSerializer, ClassSerializer, UploadDataSerializer, LoginSerializer, \
    UserRegistrationSerializer
import utils
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test


class ProjectsView(SuperuserRequiredMixin, GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/projects.html'
    serializer_class = ProjectSerializer
    queryset = models.Project.objects.all()

    def get(self, request, *args, **kwargs):
        return Response({'query_data': self.get_queryset(),
                         'serializer': self.get_serializer(),
                         'errors': None})

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return HttpResponseRedirect('./')
        return Response({'query_data': self.get_queryset(),
                         'serializer': serializer,
                         'errors': serializer.errors})


class ProjectView(SuperuserRequiredMixin, DestroyAPIView):
    queryset = models.Project.objects.all()
    lookup_field = 'id'


class WavsView(SuperuserRequiredMixin, GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/wavs.html'

    def _filters(self):
        return {'Projects': {'route': 'project__name', 'name': 'project'}}

    def get(self, request, *args, **kwargs):
        # Define filters, extract possibles values and store selections
        context = {'filters': self._filters()}
        for v in context['filters'].values():
            v['available'] = models.Wav.objects.values_list(v['route'], flat=True) \
                .order_by(v['route']).distinct()
        selected_values = {}
        for v in context['filters'].values():
            v['selected'] = request.GET.get(v['name'])
            if v['selected']:
                selected_values[v['route']] = v['selected']

        context['query_data'] = models.Wav.objects.filter(**selected_values) \
            .order_by('-id')
        return Response(context)


class WavView(SuperuserRequiredMixin, DestroyAPIView):
    queryset = models.Wav.objects.all()
    lookup_field = 'id'


class SegmentsView(SuperuserRequiredMixin, GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/segments.html'

    def _filters(self):
        return {
            'Projects': {'route': 'wav__project__name',
                         'name': 'project'},
            'Wavs': {'route': 'wav__name',
                     'name': 'wav'},
        }

    def get(self, request, *args, **kwargs):
        # Define filters, extract possibles values and store selections
        context = {'filters': self._filters()}
        for v in context['filters'].values():
            v['available'] = models.Segment.objects.values_list(v['route'], flat=True) \
                .order_by(v['route']).distinct()
        selected_values = {}
        for v in context['filters'].values():
            v['selected'] = request.GET.get(v['name'])
            if v['selected']:
                selected_values[v['route']] = v['selected']

        context['query_data'] = models.Segment.objects.filter(**selected_values) \
            .order_by('-id')
        return Response(context)


class SegmentView(SuperuserRequiredMixin, DestroyAPIView):
    queryset = models.Segment.objects.all()
    lookup_field = 'id'


class AnnotationsView(SuperuserRequiredMixin, GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/annotations.html'
    queryset = models.Annotation.objects.all()

    def _filters(self):
        return {
            'Projects': {'route': 'segment__wav__project__name',
                         'name': 'project'},
            'Wavs': {'route': 'segment__wav__name',
                     'name': 'wav'},
            'Segments': {'route': 'segment__name',
                         'name': 'segment'},
            'Users': {'route': 'user__username',
                      'name': 'user'},
            'Status': {'route': 'status',
                       'name': 'status'}
        }

    def get(self, request, *args, **kwargs):
        # Define filters, extract possibles values and store selections
        context = {'filters': self._filters()}
        for v in context['filters'].values():
            v['available'] = models.Annotation.objects.values_list(v['route'], flat=True) \
                .order_by(v['route']).distinct()
        selected_values = {}
        for v in context['filters'].values():
            v['selected'] = request.GET.get(v['name'], "")
            if v['selected']:
                selected_values[v['route']] = v['selected']

        context['query_data'] = self.get_queryset().filter(**selected_values) \
            .order_by('-id')
        return Response(context)


class AnnotationView(SuperuserRequiredMixin, DestroyAPIView):
    queryset = models.Annotation.objects.all()
    lookup_field = 'id'


class EventsView(SuperuserRequiredMixin, GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/events.html'

    def _filters(self):
        return {
            'Projects': {'route': 'annotation__segment__wav__project__name',
                         'name': 'project'},
            'Wavs': {'route': 'annotation__segment__wav__name',
                     'name': 'wav'},
            'Segments': {'route': 'annotation__segment__name',
                         'name': 'segment'},
            'Annotations': {'route': 'annotation__name',
                            'name': 'annotation'},
            'Tags': {'route': 'tags__name',
                     'name': 'tag'},
        }

    def get(self, request, *args, **kwargs):
        # Define filters, extract possibles values and store selections
        context = {'filters': self._filters()}
        for v in context['filters'].values():
            v['available'] = models.Event.objects.values_list(v['route'], flat=True) \
                .order_by(v['route']).distinct()
        selected_values = {}
        for v in context['filters'].values():
            v['selected'] = request.GET.get(v['name'], "")
            if v['selected']:
                selected_values[v['route']] = v['selected']

        context['query_data'] = models.Event.objects.filter(**selected_values) \
            .order_by('-id')
        return Response(context)


class EventView(SuperuserRequiredMixin, DestroyAPIView):
    queryset = models.Event.objects.all()
    lookup_field = 'id'


class ClassesView(SuperuserRequiredMixin, GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/classes.html'
    serializer_class = ClassSerializer
    queryset = models.Class.objects.all()

    def get(self, request, *args, **kwargs):
        return Response({'query_data': self.get_queryset(),
                         'serializer': self.get_serializer(),
                         'tags_names': ','.join(models.Tag.get_tag_names()),
                         'errors': None})

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return HttpResponseRedirect('./')
        return Response({'query_data': self.get_queryset(),
                         'serializer': serializer,
                         'tags_names': ','.join(models.Tag.get_tag_names()),
                         'errors': serializer.errors})


class ClassView(SuperuserRequiredMixin, DestroyAPIView):
    queryset = models.Class.objects.all()
    lookup_field = 'id'


#@login_required(login_url='../loginsignup')
#@user_passes_test(superuser_check)
def successful_upload(request):
    context = {}

    return render(request, 'annotation_tool/successful_upload.html', context)


class LoginSignup(GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/loginsignup.html'

    def redirect_after_login(self, user):
        path = reverse('projects') if user.is_superuser else reverse('new_annotation')
        return HttpResponseRedirect(path)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return self.redirect_after_login(request.user)
        return Response({'login_serializer': LoginSerializer(),
                         'signup_serializer': UserRegistrationSerializer(),
                         'login_tab': True})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return self.redirect_after_login(request.user)
        username = request.data.get('username')

        if 'login' in request.POST:
            password = request.POST.get('password')
            serializer = LoginSerializer(data=request.data)
            user = authenticate(username=username, password=password)
            context = {'login_serializer': serializer,
                       'signup_serializer': UserRegistrationSerializer(),
                       'login_tab': True}
            if serializer.is_valid():
                if user:
                    login(request, user)
                else:
                    context['login_error'] = 'Invalid login or password.'
                    return Response(context)
            else:
                return Response(context)
            return self.redirect_after_login(user)

        elif 'signup' in request.POST:
            serializer = UserRegistrationSerializer(data=request.data)
            context = {'login_serializer': LoginSerializer(),
                       'signup_serializer': serializer,
                       'signup_tab': True}
            if serializer.is_valid():
                u = serializer.save()
                utils.set_user_permissions(u)
                return self.redirect_after_login(u)
            if 'non_field_errors' in serializer.errors:
                context['signup_error'] = serializer.errors['non_field_errors'][0]
            return Response(context)


class UploadFileView(SuperuserRequiredMixin, GenericAPIView):
    serializer_class = UploadDataSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/upload_data.html'
    parser_classes = (MultiPartParser, FileUploadParser)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        project_id = request.data.get('project')
        segments_length = request.data.get('segments_length')
        files = request.FILES.getlist('upload_file_field')

        if serializer.is_valid():
            project = models.Project.objects.get(pk=project_id)
            for f in files:
                w = utils.create_wav(project=project, file=f, name=f.name, upload_date=timezone.now())
                duration = utils.get_wav_duration(w)
                utils.create_segments(wav=w, duration=duration, segments_length=segments_length)
            return HttpResponseRedirect('./')
        else:
            return Response({'serializer': serializer})

    def get(self, request, *args, **kwargs):
        return Response({'serializer': self.get_serializer()})


class NewAnnotationView(LoginRequiredMixin, GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/new_annotation.html'

    def _filters(self):
        return {
            'Projects': {'route': 'name',
                         'name': 'project'},
        }

    def get(self, request, *args, **kwargs):
        # Define filters, extract possibles values and store selections
        context = {'filters': self._filters(), 'error': False}
        for v in context['filters'].values():
            v['available'] = models.Project.objects.values_list(v['route'], flat=True) \
                .order_by(v['route']).distinct()
        selected_values = {}
        for v in context['filters'].values():
            v['selected'] = request.GET.get(v['name'])
            if v['selected']:
                selected_values[v['route']] = v['selected']

        context['query_data'] = models.Project.objects.filter(**selected_values) \
            .order_by('-id')

        if not v['selected']:
            return Response(context)
        else:
            segment = utils.pick_segment_to_annotate(request.GET['project'], request.user.id)
            if segment:
                project = models.Project.objects.get(name=request.GET['project'])
                context['annotation'] = utils.create_annotation(segment, request.user)
                context['classes'] = models.Class.objects.filter(project=project).values_list('name',
                                                                                              'color',
                                                                                              'shortcut')
                context['class_dict'] = json.dumps(list(context['classes']), cls=DjangoJSONEncoder)
                utils.delete_tmp_files()
                context['tmp_segment_path'] = utils.create_tmp_file(segment)
                self.template_name = 'annotation_tool/annotation_tool.html'
            else:
                # There are no more segments to annotate
                context['error'] = True
            return Response(context)


class MyAnnotations(LoginRequiredMixin, GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/my_annotations.html'

    def _filters(self):
        return {
            'Projects': {'route': 'segment__wav__project__name',
                         'name': 'project'},
            'Wavs': {'route': 'segment__wav__name',
                     'name': 'wav'},
            'Segments': {'route': 'segment__name',
                         'name': 'segment'},
            'Status': {'route': 'status',
                       'name': 'status'}
        }

    def get(self, request, *args, **kwargs):
        # Define filters, extract possibles values and store selections
        context = {'filters': self._filters()}
        for v in context['filters'].values():
            v['available'] = models.Annotation.objects.values_list(v['route'], flat=True) \
                .order_by(v['route']).distinct()
        selected_values = {}
        for v in context['filters'].values():
            v['selected'] = request.GET.get(v['name'])
            if v['selected']:
                selected_values[v['route']] = v['selected']
        selected_values['user__id'] = request.user.id

        context['query_data'] = models.Annotation.objects.filter(**selected_values) \
            .order_by('-id')

        return Response(context)


def submit_annotation(request):
    context = {}
    # Set annotation to finished
    data = json.loads(request.POST.get('data'))
    annotation = models.Annotation.objects.get(name=data['annotation'])
    annotation.status = "finished"
    annotation.save()
    project = models.Project.objects.get(name=annotation.segment.wav.project.name)
    submitted_segment = models.Segment.objects.get(name=annotation.segment.name)
    # Compute new priority values
    utils.modify_segment_priority(submitted_segment)
    # Create next annotation
    #next_segment = utils.pick_segment_to_annotate(project.name, request.user.id)
    #context['annotation'] = utils.create_annotation(next_segment, request.user)
    #context['classes'] = Class.objects.values_list('name', 'color', 'shortcut')
    #context['class_dict'] = json.dumps(list(context['classes']), cls=DjangoJSONEncoder)
    #utils.delete_tmp_files()
    #context['tmp_segment_path'] = utils.create_tmp_file(next_segment)
    #print "REACH"
    return render(request, 'annotation_tool/annotation_tool.html', context)


def create_event(request):
    print("create_event")
    region_data = json.loads(request.POST.get('region_data'))
    annotation = models.Annotation.objects.get(name=region_data['annotation'])
    event = models.Event(annotation=annotation)
    event.color = region_data['color']
    event.start_time = region_data['start_time']
    event.end_time = region_data['end_time']
    if region_data['event_class'] != "None":
        event_class = models.Class.objects.get(name=region_data['event_class'])
        event.event_class = event_class
    for t in region_data['tags']:
        tag = models.Tag.objects.get_or_create(name=t)
        event.tags.add(tag[0])
    event.save()

    return JsonResponse({'event_id': event.id})


def update_end_event(request):
    print("update_end_event")
    region_data = json.loads(request.POST.get('region_data'))

    if 'event_id' in region_data.keys():
        event = models.Event.objects.get(id=region_data['event_id'])
    else:
        annotation = models.Annotation.objects.get(name=region_data['annotation'])
        event = models.Event(annotation=annotation)
        event.color = region_data['color']
        
    event.start_time = region_data['start_time']
    event.end_time = region_data['end_time']
    event.save()

    return JsonResponse({'event_id': event.id})


def update_event(request):
    print("update_event")
    region_data = json.loads(request.POST.get('region_data'))
    event = models.Event.objects.get(id=region_data['event_id'])

    for t in region_data['tags']:
        tag = models.Tag.objects.get_or_create(name=t)
        event.tags.add(tag[0])

    if region_data['event_class'] != "None":
        event_class = models.Class.objects.get(name=region_data['event_class'])
        event.event_class = event_class
        event.color = region_data['color']

    event.start_time = region_data['start_time']
    event.end_time = region_data['end_time']
    event.save()
    print event.start_time
    print event.end_time

    return JsonResponse({})


def remove_event(request):
    print("remove_event")
    region_data = json.loads(request.POST.get('region_data'))

    event = models.Event.objects.get(id=region_data['event_id'])
    print region_data['event_id']
    event.delete()

    return JsonResponse({})
