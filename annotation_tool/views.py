import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from annotation_tool.models import Project, Wav, Segment, Annotation, Event, Class, Tag
from django.contrib.auth.models import User
from django.views.generic.edit import FormView

from annotation_tool.serializers import ProjectSerializer, ClassSerializer, UploadDataSerializer
from .forms import UploadDataForm, LoginForm
import django.core.exceptions as e
import utils
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator


def superuser_check(user):
    return user.is_superuser


def index(request):
    return HttpResponse("Hello, world. You're at the annotation tool index.")


class Projects(LoginRequiredMixin, GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/projects.html'
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def get(self, request, *args, **kwargs):
        return Response({'query_data': self.get_queryset(),
                         'serializer': self.get_serializer()})

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            utils.create_project(
                name=serializer.data['project_name'],
                creation_date=timezone.now()
            )
            return HttpResponseRedirect('./')
        return Response({'query_data': self.get_queryset(), 'serializer': serializer})


class Wavs(LoginRequiredMixin, GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/wavs.html'

    def _filters(self):
        return {'Projects': {'route': 'project__name', 'name': 'project'}}

    def get(self, request, *args, **kwargs):
        # Define filters, extract possibles values and store selections
        context = {'filters': self._filters()}
        for v in context['filters'].values():
            v['available'] = Wav.objects.values_list(v['route'], flat=True) \
                .order_by(v['route']).distinct()
        selected_values = {}
        for v in context['filters'].values():
            v['selected'] = request.GET.get(v['name'])
            if v['selected']:
                selected_values[v['route']] = v['selected']

        context['query_data'] = Wav.objects.filter(**selected_values) \
            .order_by('-id')
        return Response(context)


class Segments(LoginRequiredMixin, GenericAPIView):
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
            v['available'] = Segment.objects.values_list(v['route'], flat=True) \
                .order_by(v['route']).distinct()
        selected_values = {}
        for v in context['filters'].values():
            v['selected'] = request.GET.get(v['name'])
            if v['selected']:
                selected_values[v['route']] = v['selected']

        context['query_data'] = Segment.objects.filter(**selected_values) \
            .order_by('-id')
        return Response(context)


class Annotations(LoginRequiredMixin, GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/annotations.html'

    def _filters(self):
        return {
            'Projects': {'route': 'segment__wav__project__name',
                         'name': 'project'},
            'Wavs': {'route': 'segment__wav__name',
                     'name': 'wav'},
            'Segments': {'route': 'segment__name',
                         'name': 'segment'},
            'Users': {'route': 'user__username',
                      'name': 'user'}
        }

    def get(self, request, *args, **kwargs):
        # Define filters, extract possibles values and store selections
        context = {'filters': self._filters()}
        for v in context['filters'].values():
            v['available'] = Annotation.objects.values_list(v['route'], flat=True) \
                .order_by(v['route']).distinct()
        selected_values = {}
        for v in context['filters'].values():
            v['selected'] = request.GET.get(v['name'], "")
            if v['selected']:
                selected_values[v['route']] = v['selected']

        context['query_data'] = Annotation.objects.filter(**selected_values) \
            .order_by('-id')
        return Response(context)


class Events(LoginRequiredMixin, GenericAPIView):
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
            v['available'] = Event.objects.values_list(v['route'], flat=True) \
                .order_by(v['route']).distinct()
        selected_values = {}
        for v in context['filters'].values():
            v['selected'] = request.GET.get(v['name'], "")
            if v['selected']:
                selected_values[v['route']] = v['selected']

        context['query_data'] = Event.objects.filter(**selected_values) \
            .order_by('-id')
        return Response(context)


class Classes(LoginRequiredMixin, GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/classes.html'
    serializer_class = ClassSerializer
    queryset = Class.objects.all()

    def get(self, request, *args, **kwargs):
        return Response({'query_data': self.get_queryset(),
                         'serializer': self.get_serializer()})

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            utils.create_class(name=serializer.data['class_name'])
            return HttpResponseRedirect('./')
        return Response({'query_data': self.get_queryset(),
                         'serializer': serializer})

#@login_required(login_url='../loginsignup')
@user_passes_test(superuser_check)
def successful_upload(request):
    context = {}

    return render(request, 'annotation_tool/successful_upload.html', context)


def loginsignup(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')

        if 'login' in request.POST:
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
            else:
                return HttpResponseRedirect('./')
            context['form_login'] = LoginForm(request.POST)
            context['form_signup'] = UserCreationForm()
            if user.is_superuser:
                return HttpResponseRedirect('../projects')
            else:
                return HttpResponseRedirect('../new_annotation')

        elif 'signup' in request.POST:
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                u = User(username=username, password=password1)
                u.save()
                utils.set_user_permissions(u)
                
            else:
                # better redirect to signup with message
                raise e("Passwords do not match")
            context['form_login'] = LoginForm()
            context['form_signup'] = UserCreationForm(request.POST)

            return HttpResponseRedirect('../new_annotation')

    else:
        context['form_login'] = LoginForm()
        context['form_signup'] = UserCreationForm()

    return render(request, 'annotation_tool/loginsignup.html', context)


class UploadFileView(LoginRequiredMixin, GenericAPIView):
    serializer_class = UploadDataSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'annotation_tool/upload_data.html'
    parser_classes = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        project_name = request.data.get('project_name')
        segments_length = request.data.get('segments_length')
        files = request.FILES.getlist('upload_file_field')
        p = utils.get_project(name=project_name)

        if serializer.is_valid():
            for f in files:
                w = utils.create_wav(project=p, file=f, name=f.name, upload_date=timezone.now())
                duration = utils.get_wav_duration(w)
                utils.create_segments(wav=w, duration=duration, segments_length=segments_length)
            return HttpResponseRedirect('./')
        else:
            return Response({'serializer': serializer})

    def get(self, request, *args, **kwargs):
        return Response({'serializer': self.get_serializer()})


#@login_required(login_url='../loginsignup')
def new_annotation(request):
    context = {}

    # Define filters, extract possibles values and store selections
    context['filters'] = {
        'Projects': {'route': 'name',
                     'name': 'project'},
    }
    for v in context['filters'].values():
        v['available'] = Project.objects.values_list(v['route'], flat=True) \
            .order_by(v['route']).distinct()
    selected_values = {}
    for v in context['filters'].values():
        v['selected'] = request.GET.get(v['name'], "")
        if v['selected']:
            selected_values[v['route']] = v['selected']

    context['query_data'] = Project.objects.filter(**selected_values) \
                                            .order_by('-id')

    if v['selected'] == '':
        return render(request, 'annotation_tool/new_annotation.html', context)
    else:
        segment = utils.pick_segment_to_annotate(request.GET['project'], request.user.id)
        context['annotation'] = utils.create_annotation(segment, request.user)
        context['classes'] = Class.objects.values_list('name', 'color', 'shortcut')
        context['class_dict'] = json.dumps(list(context['classes']), cls=DjangoJSONEncoder)
        utils.delete_tmp_files()
        context['tmp_segment_path'] = utils.create_tmp_file(segment)

        return render(request, 'annotation_tool/annotation_tool.html', context)


#@login_required(login_url='../loginsignup')
def my_annotations(request):
    context = {}

    # Define filters, extract possibles values and store selections
    context['filters'] = {
        'Projects': {'route': 'segment__wav__project__name',
                     'name': 'project'},
        'Wavs': {'route': 'segment__wav__name',
                 'name': 'wav'},
        'Segments': {'route': 'segment__name',
                     'name': 'segment'},
        'Status': {'route': 'status',
                   'name': 'status'}
    }
    for v in context['filters'].values():
        v['available'] = Annotation.objects.values_list(v['route'], flat=True) \
            .order_by(v['route']).distinct()
    selected_values = {}
    for v in context['filters'].values():
        v['selected'] = request.GET.get(v['name'], "")
        if v['selected']:
            selected_values[v['route']] = v['selected']
    selected_values['user__id'] = request.user.id

    context['query_data'] = Annotation.objects.filter(**selected_values) \
                                            .order_by('-id')
    
    return render(request, 'annotation_tool/my_annotations.html', context)


def resume_annotation(request):
    context = {}

    # Define filters, extract possibles values and store selections
    context['filters'] = {
        'Annotations': {'route': 'name',
                        'name': 'annotation'},
    }
    for v in context['filters'].values():
        v['available'] = Annotation.objects.values_list(v['route'], flat=True) \
            .order_by(v['route']).distinct()
    selected_values = {}
    for v in context['filters'].values():
        v['selected'] = request.GET.get(v['name'], "")
        if v['selected']:
            selected_values[v['route']] = v['selected']
    selected_values['status'] = "unfinished"

    context['query_data'] = Annotation.objects.filter(**selected_values) \
                                            .order_by('-id')

    if v['selected'] == '':
        return render(request, 'annotation_tool/resume_annotation.html', context)
    else:
        context['annotation'] = Annotation.objects.get(name=request.GET['annotation'])
        context['events'] = Event.objects.filter(annotation=context['annotation'])
        segment = context['annotation'].segment
        context['classes'] = Class.objects.values_list('name', 'color', 'shortcut')
        context['class_dict'] = json.dumps(list(context['classes']), cls=DjangoJSONEncoder)
        utils.delete_tmp_files()
        context['tmp_segment_path'] = utils.create_tmp_file(segment)
        
        return render(request, 'annotation_tool/annotation_tool.html', context)


def submit_annotation(request):
    context = {}
    # Set annotation to finished
    data = json.loads(request.POST.get('data'))
    annotation = Annotation.objects.get(name=data['annotation'])
    annotation.status = "finished"
    annotation.save()
    project = Project.objects.get(name=annotation.segment.wav.project.name)
    submitted_segment = Segment.objects.get(name=annotation.segment.name)
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
    annotation = Annotation.objects.get(name=region_data['annotation'])
    event = Event(annotation=annotation)
    event.color = region_data['color']
    event.start_time = region_data['start_time']
    event.end_time = region_data['end_time']
    if region_data['event_class'] != "None":
        event_class = Class.objects.get(name=region_data['event_class'])
        event.event_class = event_class
    for t in region_data['tags']:
        tag = Tag.objects.get_or_create(name=t)
        event.tags.add(tag[0])
    event.save()

    return JsonResponse({'event_id': event.id})


def update_end_event(request):
    print("update_end_event")
    region_data = json.loads(request.POST.get('region_data'))

    if 'event_id' in region_data.keys():
        event = Event.objects.get(id=region_data['event_id'])
    else:
        annotation = Annotation.objects.get(name=region_data['annotation'])
        event = Event(annotation=annotation)
        event.color = region_data['color']
        
    event.start_time = region_data['start_time']
    event.end_time = region_data['end_time']
    event.save()

    return JsonResponse({'event_id': event.id})


def update_event(request):
    print("update_event")
    region_data = json.loads(request.POST.get('region_data'))
    event = Event.objects.get(id=region_data['event_id'])

    for t in region_data['tags']:
        tag = Tag.objects.get_or_create(name=t)
        event.tags.add(tag[0])

    if region_data['event_class'] != "None":
        event_class = Class.objects.get(name=region_data['event_class'])
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

    event = Event.objects.get(id=region_data['event_id'])
    print region_data['event_id']
    event.delete()

    return JsonResponse({})
