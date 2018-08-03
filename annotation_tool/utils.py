import os
import shutil
from math import ceil, floor
import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write
from django.utils import timezone
from intervaltree import IntervalTree
import contextlib
import wave
import csv
import subprocess
import django.core.exceptions as e
from django.core.files import File
from annotation_tool.models import Project, Class, Wav, Segment, Annotation, Event, Region, ClassProminence, Tag
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from config.settings.common import BASE_DIR, MEDIA_ROOT
from tqdm import tqdm


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
    if float(segments_length) != -1 and float(duration) > float(segments_length):
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


def upload_wavs_from_shell(project_name, segment_length):
    project_name = project_name.lower()
    media_path = "media/uploaded_wavs/" + project_name + '/'
    p = Project.objects.get(name=project_name)
    file_list = os.listdir(media_path)
    if file_list == []:
        raise ValueError("Upload files to %s" % media_path)
    for file_name in file_list:
        f = File(open(media_path + file_name), 'r')
        subprocess.call(['rm', media_path + file_name])
        f.name = file_name
        w = Wav(project=p, file=f, name=file_name, upload_date=timezone.now())
        w.save()
        duration = get_wav_duration(w)
        create_segments(wav=w, duration=duration, segments_length=segment_length)


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


def pick_segment_to_annotate(project_name, user_id):
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


def compute_rms(sr, wav, start_time, end_time, dtype):
    excerpt = np.array(wav[int(round(start_time*sr)):int(round(end_time*sr))])
    if dtype == np.int16:
        excerpt = excerpt / float(-np.iinfo(np.int16).min)
    elif dtype == np.int32:
        excerpt = excerpt / float(-np.iinfo(np.int32).min)
    elif dtype == np.uint8:
        excerpt = excerpt / float(np.iinfo(np.uint8).max)
    return np.sqrt(np.mean(np.square(excerpt)))


def read_wav(wav_file_name):
    input_file = os.path.join(MEDIA_ROOT, wav_file_name)
    return read(input_file, 'r')


def export_region_to_csv(wav, segment, region, annotator_name, output_csv):
    start_time = segment.start_time + region.start_time
    end_time = segment.start_time + region.end_time
    class_prominences = ClassProminence.objects.filter(
                            region=region).order_by('class_obj__name')
    classes = []
    prominences = []
    for cp in class_prominences:
        classes.append(cp.class_obj.name)
        prominences.append(cp.prominence)
    classes = '/'.join(classes)
    prominences = '/'.join([str(x) for x in prominences])
    sr, wav_samples = read_wav(wav.file.name)
    dtype = type(wav_samples[0])
    rms = compute_rms(sr, wav_samples, start_time, end_time, dtype)
    row = [annotator_name, wav.name, start_time, end_time, classes,
           prominences, rms]
    with open(output_csv, 'ab') as csvfile:
        gtwriter = csv.writer(csvfile, delimiter=',', quotechar='|',
                              quoting=csv.QUOTE_MINIMAL)
        gtwriter.writerow(row)


def export_annotation_to_csv(annotation, annotator_name, output_csv):
    segment = annotation.segment
    wav = annotation.segment.wav
    regions = Region.objects.filter(
                annotation=annotation).order_by('start_time')
    for region in regions:
        export_region_to_csv(wav, segment, region, annotator_name, output_csv)


def export_ground_truth_to_csv(wavs, annotator_name, output_csv):
    if os.path.exists(output_csv):
        os.remove(output_csv)
    with open(output_csv, 'ab') as csvfile:
        gtwriter = csv.writer(csvfile, delimiter=',', quotechar='|',
                              quoting=csv.QUOTE_MINIMAL)
        gtwriter.writerow(['annotator', 'wav', 'start', 'end', 'classes',
                           'prominences', 'energy'])
    annotations = Annotation.objects.filter(segment__wav__in=wavs,
                    user__username=annotator_name).order_by(
                        'segment__wav__name',
                        'segment__start_time')
    for annotation in tqdm(annotations):
        export_annotation_to_csv(annotation, annotator_name, output_csv)


def export_collection_ground_truth_to_csv(wavs_collection_name, annotator_name,
                                          output_csv):
    wavs = Wav.objects.filter(wavs_collection__name=wavs_collection_name)
    export_ground_truth_to_csv(wavs, annotator_name, output_csv)


def export_project_ground_truth_to_csv(project_name, annotator_name,
                                       output_csv):
    wavs = Wav.objects.filter(project__name=project_name)
    export_ground_truth_to_csv(wavs, annotator_name, output_csv)


def export_wavs_ground_truth_to_csv(wavs, annotator_name, output_csv):
    export_ground_truth_to_csv(wavs, annotator_name, output_csv)
