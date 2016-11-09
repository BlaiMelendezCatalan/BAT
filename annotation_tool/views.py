from django.shortcuts import render
from django.http import HttpResponse
from annotation_tool.models import Project, Wav, Segment, Annotation, Event
from django.contrib.auth.models import User


def index(request):
    return HttpResponse("Hello, world. You're at the annotation tool index.")


def projects(request):
    projects = Project.objects.all()
    return render(request, 'annotation_tool/projects.html', {'projects': projects})


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
