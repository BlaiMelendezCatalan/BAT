import json
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from annotation_tool.models import Project, Wav, Segment, Annotation, Event, Class, Tag
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from .forms import CreateProjectForm, CreateClassForm, UploadDataForm, LoginForm
import django.core.exceptions as e
import utils
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test,login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect


def superuser_check(user):
    return user.is_superuser


def index(request):
    return HttpResponse("Hello, world. You're at the annotation tool index.")


#@login_required(login_url='../../annotation_tool/loginsignup')
@user_passes_test(superuser_check)
def projects(request):
    context = {}

    context['query_data'] = Project.objects.all()

    if request.method == 'POST':
        context['form'] = CreateProjectForm(request.POST)
        if context['form'].is_valid():
            utils.create_project(
                name=context['form'].cleaned_data['project_name'],
                creation_date=timezone.now())
            return HttpResponseRedirect('./')
    else:
        context['form'] = CreateProjectForm()

    return render(request, 'annotation_tool/projects.html', context)


#@login_required(login_url='../../loginsignup')
@user_passes_test(superuser_check)
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

    context['query_data'] = Wav.objects.filter(**selected_values) \
                                            .order_by('-id')
    return render(request, 'annotation_tool/wavs.html', context)


#@login_required(login_url='../loginsignup')
@user_passes_test(superuser_check)
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

    context['query_data'] = Segment.objects.filter(**selected_values) \
                                            .order_by('-id')
    return render(request, 'annotation_tool/segments.html', context)


#@login_required(login_url='../loginsignup')
@user_passes_test(superuser_check)
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
        'Users': {'route': 'user__username',
                  'name': 'user'}
    }
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
    return render(request, 'annotation_tool/annotations.html', context)


#@login_required(login_url='../loginsignup')
@user_passes_test(superuser_check)
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

    context['query_data'] = Event.objects.filter(**selected_values) \
                                            .order_by('-id')
    return render(request, 'annotation_tool/events.html', context)


#@login_required(login_url='../loginsignup')
@user_passes_test(superuser_check)
def classes(request):
    context = {}

    context['query_data'] = Class.objects.all()

    if request.method == 'POST':
        context['form'] = CreateClassForm(request.POST)
        if context['form'].is_valid():
            utils.create_class(name=context['form'].cleaned_data['class_name'])
            return HttpResponseRedirect('./')
    else:
        context['form'] = CreateClassForm()

    return render(request, 'annotation_tool/classes.html', context)


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



class UploadFileView(FormView):
    form_class = UploadDataForm
    template_name = 'annotation_tool/upload_data.html'

    @method_decorator(user_passes_test(superuser_check, login_url=None, redirect_field_name=None)) 
    def dispatch(self, *args, **kwargs):
        return super(UploadFileView,  self).dispatch(*args, **kwargs)

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

    if 'update-tags' in region_data.keys():
        for t in region_data['tags']:
            tag = Tag.objects.get_or_create(name=t)
            event.tags.add(tag[0])
        event.save()
    if 'update-class' in region_data.keys():
        event = Event.objects.get(id=region_data['event_id'])
        event_class = Class.objects.get(name=region_data['event_class'])
        event.event_class = event_class
        event.color = region_data['color']
        event.save()
    if 'update-times' in region_data.keys():
        event.start_time = region_data['start_time']
        event.end_time = region_data['end_time']
        event.save()

    return JsonResponse({})


def remove_event(request):
    print("remove_event")
    region_data = json.loads(request.POST.get('region_data'))

    event = Event.objects.get(id=region_data['event_id'])
    print region_data['event_id']
    event.delete()

    return JsonResponse({})
