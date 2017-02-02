import os
import shutil
from math import ceil, floor
import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write
from django.utils import timezone
import contextlib
import wave
import django.core.exceptions as e
from annotation_tool.models import Project, Wav, Segment, Annotation, Event, Tag, Class, ClassProminence
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from config.settings.common import BASE_DIR, MEDIA_ROOT


def create_project(name, creation_date):
    p = Project(name=name, creation_date=creation_date)
    p.save()


def delete_project(name):
    p = Project.objects.get(name=name)
    p.delete()


def get_project(name):
    try:
        p = Project.objects.get(name=name)
    except:
        raise e.ObjectDoesNotExist("Project '%s' does not exist. Create it first." % project_name)

    return p


def create_wav(project, file, name, upload_date):
    w = Wav(project=project, file=file, name=name, upload_date=upload_date)
    w.save()

    return w


def get_wav_duration(wav):
    with contextlib.closing(wave.open(wav.file, 'r')) as f:
        duration = f.getnframes() / float(f.getframerate())

    return duration


def create_segments(wav, duration, segments_length):
    if segments_length != -1:
        number_of_segments = duration / float(segments_length)
        if number_of_segments % 1 > .5:
            number_of_segments = int(np.ceil(number_of_segments))
        else:
            number_of_segments = int(np.floor(number_of_segments))
        for i in xrange(number_of_segments):
            
            start_time = i * float(segments_length)
            if i < number_of_segments - 1:
                end_time = (i + 1) * float(segments_length)
            else:
                end_time = float(duration)
            name = wav.name.split('/')[-1].replace(".wav", "_" + str(start_time) + "_" + str(end_time) + ".wav")
            s = Segment(wav=wav, start_time=start_time, end_time=end_time, name=name)
            s.save()
    else:
        name = wav.name.split('/')[-1].replace(".wav", "_" + "0.0" + "_" + str(duration) + ".wav")
        s = Segment(wav=wav, start_time=0.0, end_time=duration, name=name)
        s.save()


def create_annotation(segment, user):
    name = str(segment.name.replace('.wav', '')) + '_annotation_' + str(user.id)
    annotation = Annotation(segment=segment,
                            user=user,
                            name=name,
                            annotation_date=timezone.now())
    annotation.save()

    return annotation


def create_class(name):
    c = Class(name=name)
    c.save()


def set_user_permissions(user):
    annotation_content_type = ContentType.objects.get_for_model(Annotation)
    event_content_type = ContentType.objects.get_for_model(Event)
    tag_content_type = ContentType.objects.get_for_model(Tag)

    annotation_permission = Permission.objects.filter(content_type=annotation_content_type)
    event_permission = Permission.objects.filter(content_type=event_content_type)
    tag_permission = Permission.objects.filter(content_type=tag_content_type)

    permissions = annotation_permission | event_permission | tag_permission

    for p in permissions:
        user.user_permissions.add(p)


def pick_segment_to_annotate(project_name, user_id): # MODIFY!!!
    segments = Segment.objects.filter(wav__project__name=project_name).order_by('priority')
    for segment in segments:
        annotations = Annotation.objects.filter(segment__id=segment.id)
        if user_id in annotations.values_list('user__id', flat=True):
            continue
        else:
            return segment


def update_annotation_status(annotation, new_status=Annotation.UNFINISHED):
    old_status = annotation.status
    if old_status != new_status:
        annotation.status = new_status
        annotation.save()
        modify_segment_priority(annotation.segment)


def modify_segment_priority(segment): # MODIFY!!!
    segment.priority = 1
    segment.save()
    #annotations = Annotation.objects.filter(segment=segment, status="finished")
    #project = segment.get_project()
    #if len(annotations) > 1:
        #agreement = compute_interannotation_agreement(annotations, project.overlap)
        #if agreement >= 0.8:
            #segment.reliable = True
            #segment.save()
            #generate_ground_truth()



#def compute_interannotation_agreement(annotations, overlap):


def normalize_prominence(region):
    class_prominences = ClassProminence.objects.filter(region=region)
    classes = []
    prominences = np.array([])
    for cp in class_prominences:
        classes.append(cp.class_obj.name)
        prominences = np.append(prominences, cp.prominence)
    prominences = prominences / float(sum(prominences))
    dict = {}
    for c, p in zip(classes, prominences):
        dict[c] = p

    return dict



def delete_tmp_files():
    if os.path.exists(BASE_DIR + '/tmp/'):
        shutil.rmtree(BASE_DIR + '/tmp/')


def create_tmp_file(segment):
    os.mkdir(BASE_DIR + '/tmp/')
    input_file = os.path.join(MEDIA_ROOT, segment.wav.file.name)
    output_file = 'tmp/' + input_file.split('/')[-1]
    wav_file = read(input_file, 'r')
    sample_rate = wav_file[0]
    start = int(ceil(sample_rate * (segment.start_time)))
    end = int(floor(sample_rate * (segment.end_time)))
    write(
        output_file,
        sample_rate,
        wav_file[1][start:end])

    return output_file


def merge_segment_annotations(segment): # MODIFY!!!
    annotations = Annotation.objects.filter(segment=segment)
    # Get the set of boundaries of all events
    boundaries = [0.0, segment.end_time - segment.start_time]
    classes = list(Class.objects.values_list("name",
                                             flat=True))  # Depending on how we handle overlappings, this should probably include class mixtures.
    segment_events = []
    for annotation in annotations:
        events = Event.objects.filter(annotation=annotation)
        segment_events.append(events)
        for event in events:
            boundaries.append(event.start_time)
            boundaries.append(event.end_time)
    boundaries = list(set(boundaries))
    for i in xrange(len(boundaries) - 1):
        class_score = np.zeros(len(classes))
        for event in segment_events:
            if event.start_time <= boundaries[i] and event.end_time >= boundaries[i + 1]:
                class_score[classes.index(event.event_class)] += 1
        if max(class_score) != 0:
            class_name = classes[np.argmax(class_score)]
            region = Region(segment=segment,
                            class_name=class_name,
                            start_time=boundaries[i],
                            end_time=boundaries[i + 1])
            region.save()
        else:
            region = Region(segment=segment,
                            class_name="unknown",
                            start_time=boundaries[i],
                            end_time=boundaries[i + 1])
            region.save()


def generate_ground_truth(project): # MODIFY!!!
    wavs = Wavs.objects.filter(project=project)
    gt_dict = {}
    for wav in wavs:
        gt_dict[wav.name] = {}
        segments = Segment.objects.filter(wav=wav)
        for segment in segments:
            gt_dict[wav.name][segment.name] = {}
            regions = Region.objects.filter(segment=segment)
            for region in regions:
                gt_dict[wav.name][segment.name]['class'] = region.class_name
                gt_dict[wav.name][segment.name]['start_time'] = region.start_time
                gt_dict[wav.name][segment.name]['end_time'] = region.end_time
