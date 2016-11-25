import os
import shutil
from math import ceil, floor
import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write
from django.utils import timezone
import contextlib
import wave
import numpy as np
import django.core.exceptions as e
from annotation_tool.models import Project, Wav, Segment, Annotation, Event, Tag, Class
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from annotation_project.settings import BASE_DIR


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
	with contextlib.closing(wave.open(wav.file,'r')) as f:
		duration = f.getnframes() / float(f.getframerate())

	return duration


def create_segments(wav, duration, segments_length):
	# Make the lasy segment longer or an additional shorter segment depending on the decimal part of the division
	number_of_segments = int(np.ceil(duration / float(segments_length)))
	for i in xrange(number_of_segments):
		start_time = i * float(segments_length)
		end_time = float(min(duration, (i+1) * float(segments_length)))
		name = wav.name.split('/')[-1].replace(".wav", "_" + str(start_time) + "_" + str(end_time) + ".wav")
		s = Segment(wav=wav, start_time=start_time, end_time=end_time, name=name)
		s.save()


def create_annotation(segment, user):
	name = str(segment.name.replace('.wav', '')) + '_annotation_' + str(user.id)
	annotation = Annotation(segment=segment,
							user=user,
							name=name,
							annotation_date=timezone.now())
	annotation.save()

	segment.number_of_annotations += 1
	# Compute difficulty(inter-annotation difference)
	# Compute priority = f(difficulty, number_of_annotations)
	segment.save()

	return annotation


def create_class(name):
	c = Class(name = name)
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


def pick_segment_to_annotate(project_name, user_id):
	segments = Segment.objects.filter(wav__project__name=project_name).order_by('priority')
	for segment in segments:
		annotations = Annotation.objects.filter(segment__id=segment.id)
		if user_id in annotations.values_list('user__id', flat=True):
			continue
		else:
			return segment


#def compute_difficulty(segment_id):
#	classes = Class.objects.values_list('name')
#	for c in classes:
#		events = Event.objects.filter(annotation__segment__id=segment_id, event_class=c)
#		for e in events:


def compute_priority(segment_id):
	segment = Segment.objects.get(id=segment_id)
	segment.priority = segment.number_of_annotations # * segment.difficulty
	segment.save()


def delete_tmp_files():
	if os.path.exists(BASE_DIR + '/tmp/'):
		shutil.rmtree(BASE_DIR + '/tmp/')


def create_tmp_file(segment):
	os.mkdir(BASE_DIR + '/tmp/')
	input_file = segment.wav.file.name
	output_file = 'tmp/' + input_file.split('/')[-1]
	wav_file = read(input_file, 'r')
	sample_rate = wav_file[0]
	start = int(ceil(sample_rate * segment.start_time))
	end = int(floor(sample_rate * segment.end_time))
	write(
		output_file,
		sample_rate,
		wav_file[1][start:end])

	return output_file


#def annotate_silence(segment_path):
#	wav_file = read(BASE_DIR + '/' + segment_path, 'r')
#	max_value = pow(max(wav_file[1]), 2)
#	signal = pow(np.array(wav_file[1], dtype=np.float), 2)
#	signal = signal / max(signal)
#	energy = []
#	average_range = 200
#	for i in xrange(len(signal)):
#		summation = sum(
#			signal[max(0, i - average_range):min(len(signal), i + 1 + average_range)])
#		energy.append(summation / len(
#			signal[max(0, i - average_range):min(len(signal), i + 1 + average_range)]))
#	print energy