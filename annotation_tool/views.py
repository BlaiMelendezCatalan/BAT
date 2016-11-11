from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from annotation_tool.models import Project, Wav, Segment, Annotation, Event
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from .forms import CreateProjectForm, UploadDataForm
import django.core.exceptions as e
import utils


def index(request):
    return HttpResponse("Hello, world. You're at the annotation tool index.")


def projects(request):
    context = {}

    context['projects'] = Project.objects.all()

    if request.method == 'POST':
        context['form'] = CreateProjectForm(request.POST)
        if context['form'].is_valid():
            p = utils.create_project(
                        name=context['form'].cleaned_data['project_name'],
                        creation_date=timezone.now())
            return HttpResponseRedirect('./')
    else:
        context['form'] = CreateProjectForm()

    return render(request, 'annotation_tool/projects.html', context)


def wavs(request):
    context = {}

    # Define filters, extract possibles values and store selections
    context['filters'] = {
        'Projects': {'route': 'project__name',
                     'name': 'project'},
    }
    for v in context['filters'].values():
        v['available'] = Wav.objects.values_list(v['route'], flat=True) \
            .order_by(v['route']).distinct()
    selected_values = {}
    for v in context['filters'].values():
        v['selected'] = request.GET.get(v['name'], "")
        if v['selected']:
            selected_values[v['route']] = v['selected']

    # Get filtered runs
    context['query_data'] = Wav.objects.filter(**selected_values) \
                                            .order_by('-id')
    return render(request, 'annotation_tool/wavs.html', context)


def segments(request):
    context = {}

    # Define filters, extract possibles values and store selections
    context['filters'] = {
        'Projects': {'route': 'wav__project__name',
                     'name': 'project'},
        'Wavs': {'route': 'wav__name',
                 'name': 'wav'},
    }
    for v in context['filters'].values():
        v['available'] = Segment.objects.values_list(v['route'], flat=True) \
            .order_by(v['route']).distinct()
    selected_values = {}
    for v in context['filters'].values():
        v['selected'] = request.GET.get(v['name'], "")
        if v['selected']:
            selected_values[v['route']] = v['selected']

    # Get filtered runs
    context['query_data'] = Segment.objects.filter(**selected_values) \
                                            .order_by('-id')
    return render(request, 'annotation_tool/segments.html', context)


def annotations(request):
    context = {}

    # Define filters, extract possibles values and store selections
    context['filters'] = {
        'Projects': {'route': 'segment__wav__project__name',
                     'name': 'project'},
        'Wavs': {'route': 'segment__wav__name',
                 'name': 'wav'},
        'Segments': {'route': 'segment__name',
                     'name': 'segment'},
    }
    for v in context['filters'].values():
    	v['available'] = Annotation.objects.values_list(v['route'], flat=True) \
        	.order_by(v['route']).distinct()
    selected_values = {}
    for v in context['filters'].values():
        v['selected'] = request.GET.get(v['name'], "")
        if v['selected']:
            selected_values[v['route']] = v['selected']

    # Get filtered runs
    context['query_data'] = Annotation.objects.filter(**selected_values) \
                                            .order_by('-id')
    return render(request, 'annotation_tool/annotations.html', context)


def events(request):
    context = {}

    # Define filters, extract possibles values and store selections
    context['filters'] = {
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
    for v in context['filters'].values():
        v['available'] = Event.objects.values_list(v['route'], flat=True) \
            .order_by(v['route']).distinct()
    selected_values = {}
    for v in context['filters'].values():
        v['selected'] = request.GET.get(v['name'], "")
        if v['selected']:
            selected_values[v['route']] = v['selected']

    # Get filtered runs
    context['query_data'] = Event.objects.filter(**selected_values) \
                                            .order_by('-id')
    return render(request, 'annotation_tool/events.html', context)


def successful_upload(request):
    context = {}

    return render(request, 'annotation_tool/successful_upload.html', context)


class UploadFileView(FormView):
    form_class = UploadDataForm
    template_name = 'annotation_tool/upload_data.html'

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        project_name = request.POST.get('project_name')
        segments_length = request.POST.get('segments_length')
        files = request.FILES.getlist('upload_file_field')
        p = utils.get_project(name=project_name)

        if form.is_valid():
            for f in files:
                w = utils.create_wav(project=p, file=f, name=f.name, upload_date=timezone.now())
                duration = utils.get_wav_duration(w)
                utils.create_segments(wav=w, duration=duration, segments_length=segments_length)
            return HttpResponseRedirect('./')
        else:
            return self.form_invalid(form)
