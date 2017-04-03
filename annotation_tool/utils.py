import os
import shutil
from math import ceil, floor
import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write
from django.utils import timezone
import contextlib
import wave
import csv
import django.core.exceptions as e
from annotation_tool.models import Project, Class, Wav, Segment, Annotation, Event, Region, ClassProminence, Tag
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
    if int(segments_length) != -1 and duration > segments_length:
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
    segments = Segment.objects.filter(wav__project__name=project_name)
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
        #modify_segment_priority(annotation.segment)


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
    dtype = type(wav_file[1][0])
    sample_rate = wav_file[0]
    padding = round((segment.end_time - segment.start_time) / 20., 2)
    last_segment = Segment.objects.filter(wav=segment.wav).order_by('start_time')
    last_segment = last_segment.reverse()[0]
    if segment.start_time == 0 and segment == last_segment:
        start = 0
        end = int(floor(sample_rate * (segment.end_time + 2 * padding)))
        wav = np.memmap('/tmp/wav.array', dtype=dtype,
                        mode='w+', shape=(int(2 * round(sample_rate * padding)) + len(wav_file[1]),))
        wav[:] = 0
        wav[int(round(sample_rate * padding)):-1 * int(round(sample_rate * padding))] = wav_file[1]
    elif segment.start_time == 0:
        start = 0
        end = int(floor(sample_rate * (segment.end_time + 2 * padding)))
        wav = np.memmap('/tmp/wav.array', dtype=dtype,
                        mode='w+', shape=(int(round(sample_rate * padding)) + len(wav_file[1]),))
        wav[:] = 0
        wav[int(round(sample_rate * padding)):] = wav_file[1]
    elif segment == last_segment:
        start = int(ceil(sample_rate * (segment.start_time - padding)))
        end = int(floor(sample_rate * (segment.end_time + 2 * padding)))
        wav = np.memmap('/tmp/wav.array', dtype=dtype,
                        mode='w+', shape=(int(round(sample_rate * padding)) + len(wav_file[1]),))
        wav[:] = 0
        wav[:-1 * int(round(sample_rate * padding))] = wav_file[1]
    else:
        start = int(ceil(sample_rate * (segment.start_time - padding)))
        end = int(floor(sample_rate * (segment.end_time + padding)))
        wav = wav_file[1]
    write(
        output_file,
        sample_rate,
        wav[start:end])

    return output_file, padding


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


def save_ground_truth_to_csv(project):
    path = BASE_DIR + '/ground_truth/'
    path += project.name.replace(' ', '_') + '/'
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    path_csv = path + project.name.replace(' ', '_') + '.csv'
    with open(path_csv, 'ab') as csvfile:
        gtwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        gtwriter.writerow(['annotator', 'wav', 'start', 'end', 'classes', 'prominences'])
    annotations = Annotation.objects.filter(segment__wav__project=project)
    users = list(set(annotations.values_list('user__username', flat=True)))
    wavs = Wav.objects.filter(project=project)
    for user in users:
        for wav in wavs:
            input_file = os.path.join(MEDIA_ROOT, wav.file.name)
            wav_file = read(input_file, 'r')
            dtype = type(wav_file[1][0])
            segments = Segment.objects.filter(wav=wav).order_by('start_time')
            for segment in segments:
                annotation = annotations.filter(segment=segment, user__username=user)
                if annotation:
                    regions = Region.objects.filter(annotation=annotation).order_by('start_time')
                    if regions:
                        for region in regions: #Check if region.start != region.end
                            class_prominences = ClassProminence.objects.filter(
                                                    region=region).order_by('class_obj__name')
                            classes = []
                            prominences = []
                            for cp in class_prominences:
                                classes.append(cp.class_obj.name)
                                prominences.append(cp.prominence)
                            if None in prominences and len(prominences) > 1:
                                raise ValueError("Unassigned prominence in annotation %d of user %s" % (annotation.id, user))
                            row = []
                            row.append(user)
                            row.append(wav.name.replace('.wav', ''))
                            start_time = segment.start_time + region.start_time
                            row.append(start_time)
                            end_time = segment.start_time + region.end_time
                            row.append(end_time)
                            row.append('/'.join(classes))
                            rms = computeRMS(wav_file[0], wav_file[1], start_time, end_time, dtype)
                            if len(prominences) > 1:
                                max_prom = sum(prominences)
                                row.append('/'.join(str(x * rms / max_prom) for x in prominences))
                            else:
                                row.append(str(rms))
                            with open(path_csv, 'ab') as csvfile:
                                gtwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                                gtwriter.writerow(row)
                    else:
                        events = Event.objects.filter(annotation=annotation).order_by('start_time')
                        for event in events:
                            row = []
                            row.append(user)
                            row.append(wav.name.replace('.wav', ''))
                            start_time = segment.start_time + event.start_time
                            row.append(start_time)
                            end_time = segment.start_time + event.end_time
                            row.append(end_time)
                            rms = computeRMS(wav_file[0], wav_file[1], start_time, end_time, dtype)
                            row.append(event.event_class.name)
                            row.append(str(rms))
                            with open(path_csv, 'ab') as csvfile:
                                gtwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                                gtwriter.writerow(row)


def computeRMS(sr, wav_file, start_time, end_time, dtype):
    excerpt = np.array(wav_file[int(round(start_time*sr)):int(round(end_time*sr))])
    if dtype == np.int16:
        excerpt = excerpt / float(-np.iinfo(np.int16).min)
    elif dtype == np.int32:
        excerpt = excerpt / float(-np.iinfo(np.int32).min)
    elif dtype == np.uint8:
        excerpt = excerpt / float(np.iinfo(np.uint8).max)
    return np.sqrt(np.mean(np.square(excerpt)))