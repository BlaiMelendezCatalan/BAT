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

# Implemented for non-overlapping events
def modify_segment_priority(segment):
	annotations = Annotation.objects.filter(segment=segment, status="finished")
	if len(annotations) > 1:
		# Get the set of boundaries of all events
		boundaries = [0.0, segment.end_time - segment.start_time]
		classes = list(Class.objects.values_list("name", flat=True)) # Depending on how we handle overlappings, this should probably include class mixtures.
		class_score = np.zeros(len(classes))
		segment_events = []
		for annotation in annotations:
			events = Event.objects.filter(annotation=annotation)
			segment_events.append(events)
			for event in events:
				boundaries.append(event.start_time)
				boundaries.append(event.end_time)
		boundaries = list(set(boundaries))
		# Compute agreement between annotations
		agreement = 0.0
		for i in xrange(len(boundaries) - 1):
			class_score = np.zeros(len(classes))
			for event in segment_events:
				if event.start_time <= boundaries[i] and event.end_time >= boundaries[i+1]:
					class_score[classes.index(event.event_class)] += 1
			max_score = max(class_score)
			duration = boundaries[i+1] - boundaries[i]
			agreement += float(max_score) * duration / len(annotations)

		segment.priority = (1 - agreement / (segment.end_time - segment.start_time)) / len(annotations)
		segment.save()
	else:
		print "modifying priority to 1.0"
		segment.priority = 1.0
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
	start = int(ceil(sample_rate * (segment.start_time)))
	end = int(floor(sample_rate * (segment.end_time + 0.1)))
	write(
		output_file,
		sample_rate,
		wav_file[1][start:end])

	return output_file


# Implemented for non-overlapping events
# It doesn't handle not annotated (unknown) parts of the segments yet		
def merge_segment_annotations(segment):
	annotations = Annotation.objects.filter(segment=segment)
	# Get the set of boundaries of all events
	boundaries = [0.0, segment.end_time - segment.start_time]
	classes = list(Class.objects.values_list("name", flat=True)) # Depending on how we handle overlappings, this should probably include class mixtures.
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
			if event.start_time <= boundaries[i] and event.end_time >= boundaries[i+1]:
				class_score[classes.index(event.event_class)] += 1
		if max(class_score) != 0:
			class_name = classes[np.argmax(class_score)]
			region = Region(segment=segment,
							class_name=class_name,
							start_time=boundaries[i],
							end_time=boundaries[i+1])
			region.save()
		else:
			region = Region(segment=segment,
							class_name="unknown",
							start_time=boundaries[i],
							end_time=boundaries[i+1])
			region.save()

# Still unfinished due to the undefinition of the necessary output format
def generate_ground_truth(project):
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
