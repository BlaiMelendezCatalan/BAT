import json
import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, DestroyAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from annotation_tool import models
from annotation_tool.mixins import SuperuserRequiredMixin

from annotation_tool.serializers import ProjectSerializer, ClassSerializer, UploadDataSerializer, LoginSerializer, \
    UserRegistrationSerializer, RegionSerializer, ClassProminenceSerializer
import utils
from django.contrib.auth import authenticate, login, logout


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


class AnnotationFinishView(LoginRequiredMixin, GenericAPIView):
    queryset = models.Annotation.objects.all()
    lookup_field = 'id'

    def post(self, request, *args, **kwargs):
        annotation = self.get_object()
        utils.update_annotation_status(annotation,
                                       new_status=models.Annotation.FINISHED)

        # find unfinished annotation for current project
        project = annotation.get_project()
        segments = models.Segment.objects.filter(wav__project=project)
        next_annotation = models.Annotation.objects.filter(user__id=request.user.id,
                                                           segment__in=segments,
                                                           status=models.Annotation.UNFINISHED).first()

        next_annotation_url = ''
        if next_annotation:
            next_annotation_url = '{}?project={}&annotation={}'.format(reverse('new_annotation'),
                                                                       project.id,
                                                                       next_annotation.id)
        return Response(data={'next_annotation_url': next_annotation_url}, status=status.HTTP_200_OK)


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
        # add opacity for color
        data = request.data.copy()
        opacity = '0.5'
        data['color'] = re.sub(r'rgb\((\d{1,3}),(\d{1,3}),(\d{1,3})\)',
                               r'rgba(\1, \2, \3, %s)' % opacity,
                               data['color'])

        serializer = self.get_serializer(data=data)
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


# @login_required(login_url='../loginsignup')
# @user_passes_test(superuser_check)
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
        context = {'filters': self._filters(), 'error': ''}
        for v in context['filters'].values():
            v['available'] = models.Project.objects.all().order_by(v['route'])
        selected_project = request.GET.get('project')

        context['query_data'] = models.Project.objects.all().order_by('-id')

        if not selected_project:
            return Response(context)

        annotation_id = request.GET.get('annotation')
        project = get_object_or_404(models.Project, id=request.GET.get('project'))
        segment = utils.pick_segment_to_annotate(project.name, request.user.id)
        if not annotation_id and not segment:
            context['error'] = 'There are no more segments to annotate.'
            return Response(context)

        # if new annotation so create it and redirect to edit page
        if not annotation_id:
            annotation = utils.create_annotation(segment, request.user)
            url = '%s?project=%d&annotation=%d' % (reverse('new_annotation'), project.id, annotation.id)
            return HttpResponseRedirect(url)

        try:
            context['annotation'] = models.Annotation.objects.get(id=annotation_id, user=request.user)
            context['events'] = models.Event.objects.filter(annotation=annotation_id)
            context['regions'] = models.Region.objects.filter(annotation=annotation_id)
            segment = context['annotation'].segment
        except models.Annotation.DoesNotExist:
            return HttpResponseRedirect(reverse('new_annotation'))

        context['classes'] = models.Class.objects.filter(project=project).values_list('name',
                                                                                      'color',
                                                                                      'shortcut')
        context['prominence_choices'] = models.ClassProminence.PROMINENCE_CHOICES
        context['class_dict'] = json.dumps(list(context['classes']), cls=DjangoJSONEncoder)
        context['project'] = project

        # create tmp file
        utils.delete_tmp_files()
        context['tmp_segment_path'] = utils.create_tmp_file(segment)

        context['base_template'] = 'annotation_tool/base.html' if request.user.is_superuser else \
            'annotation_tool/base_normal.html'
        self.template_name = 'annotation_tool/tool.html'

        context['visualization'] = self._get_visualization(request)

        return Response(context)

    def _get_visualization(self, request):
        if request.GET.get('visualization') == '1':
            return 'spectrogram'
        return 'waveform'


class MyAnnotationsView(LoginRequiredMixin, GenericAPIView):
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


class RegionsView(LoginRequiredMixin, ListCreateAPIView):
    queryset = models.Region.objects.all()
    serializer_class = RegionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # check exists regions with same time
        data = serializer.validated_data
        models.Region.objects.filter(
            annotation=data['annotation']).filter(Q(start_time=data['start_time'])
                                                  | Q(end_time=data['end_time'])).delete()

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        try:
            annotation_id = request.data['annotation_id']
            annotation = models.Annotation.objects.get(id=annotation_id)
        except KeyError, models.Annotation.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        regions = queryset.filter(annotation=annotation)
        models.ClassProminence.objects.filter(region__in=regions).delete()
        regions.delete()

        utils.update_annotation_status(annotation,
                                       new_status=models.Annotation.UNFINISHED)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClassProminenceView(LoginRequiredMixin, GenericAPIView):
    queryset = models.ClassProminence.objects.all()
    serializer_class = ClassProminenceSerializer

    def post(self, request, *args, **kwargs):
        try:
            region = models.Region.objects.get(id=request.data['region_id'])
            class_obj = models.Class.objects.get(name=request.data['class_name'],
                                                 project=region.get_project())
            prominence = request.data['prominence']
        except (models.Region.DoesNotExist, models.ClassProminence.DoesNotExist):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        models.ClassProminence.objects.update_or_create(region=region,
                                                        class_obj=class_obj,
                                                        defaults={'prominence': prominence})
        return Response(status=status.HTTP_201_CREATED)


class LogoutView(LoginRequiredMixin, APIView):
    def post(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('loginsignup'))


def create_event(request):
    print("create_event")
    region_data = json.loads(request.POST.get('region_data'))
    try:
        annotation = models.Annotation.objects.get(name=region_data['annotation'])
    except models.Annotation.DoesNotExist:
        return JsonResponse({'error': 'Annotation does not exist'})
    event = models.Event(annotation=annotation)
    event.color = region_data['color']
    event.start_time = region_data['start_time']
    event.end_time = region_data['end_time']
    if region_data['event_class'] != "None":
        event_class = models.Class.objects.get(name=region_data['event_class'],
                                               project=annotation.get_project())
        event.event_class = event_class
    for t in region_data['tags']:
        tag = models.Tag.objects.get_or_create(name=t)
        event.tags.add(tag[0])
    event.save()

    utils.update_annotation_status(annotation,
                                   new_status=models.Annotation.UNFINISHED)

    return JsonResponse({'event_id': event.id})


def update_end_event(request):
    print("update_end_event")
    region_data = json.loads(request.POST.get('region_data'))

    if 'event_id' in region_data.keys():
        try:
            event = models.Event.objects.get(id=region_data['event_id'])
        except models.Event.DoesNotExist:
            return JsonResponse({'error': 'Event does not exist'})
        annotation = event.annotation
    else:
        try:
            annotation = models.Annotation.objects.get(id=region_data['annotation'])
        except models.Annotation.DoesNotExist:
            return JsonResponse({'error': 'Annotation does not exist'})
        event = models.Event(annotation=annotation)
        event.color = region_data['color']

    utils.update_annotation_status(annotation,
                                   new_status=models.Annotation.UNFINISHED)

    event.start_time = region_data['start_time']
    event.end_time = region_data['end_time']
    event.save()

    return JsonResponse({'event_id': event.id})


def update_event(request):
    print("update_event")
    region_data = json.loads(request.POST.get('region_data'))
    try:
        event = models.Event.objects.get(id=region_data['event_id'])
    except models.Event.DoesNotExist:
        return JsonResponse({'error': 'Event does not exist'})

    if 'tags' in region_data:
        event.tags.clear()
        for tag_name in region_data['tags']:
            if not tag_name:
                continue
            tag, _ = models.Tag.objects.get_or_create(name=tag_name)
            event.tags.add(tag)

    if 'event_class' in region_data and region_data['event_class'] and region_data['event_class'] != 'None':
        event_class = models.Class.objects.get(name=region_data['event_class'],
                                               project=event.get_project())
        event.event_class = event_class
        event.color = region_data['color']

    event.start_time = region_data['start_time']
    event.end_time = region_data['end_time']
    event.save()
    print event.start_time
    print event.end_time

    utils.update_annotation_status(event.annotation,
                                   new_status=models.Annotation.UNFINISHED)

    return JsonResponse({})


def remove_event(request):
    print("remove_event")
    region_data = json.loads(request.POST.get('region_data'))

    try:
        event = models.Event.objects.get(id=region_data['event_id'])
    except models.Event.DoesNotExist:
        return JsonResponse({'error': 'Event does not exist'})
    print region_data['event_id']
    event.delete()

    utils.update_annotation_status(event.annotation,
                                   new_status=models.Annotation.UNFINISHED)

    return JsonResponse({})
