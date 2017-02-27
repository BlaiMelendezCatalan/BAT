import os
from math import ceil, floor
import numpy as np
import random
import datetime
from annotation_tool.models import Project, Wav, Segment, Annotation, Event, Tag, Class, ClassProminence, Annotator
import annotation_tool.utils


def get_total_annotation_time_stats(model_obj):
	if model_obj.__class__.__name__ == 'Porject':
		annotations = Annotation.objects.filter(segment__wav__project=model_obj)
	elif model_obj.__class__.__name__ == 'Wav':
		annotations = Annotation.objects.filter(segment__wav=model_obj)
	elif model_obj.__class__.__name__ == 'Segment':
		annotations = Annotation.objects.filter(segment=model_obj)
	elif model_obj.__class__.__name__ == 'Annotation':
		annotations = [model_obj]
	else:
		raise ValueError('Model should be Project, Wav, Segment or Annotation')
	
	if not model_obj.__class__.__name__ == 'Annotation':
		ids = annotations.values_list('id', flat=True)
	else:
		ids = [model_obj.id]

	finish_times = []
	for annotation in annotations:
		finish_time = 0
		all_logs = Log.objects.filter(annotation=annotation)
		logs = Log.objects.filter(
					annotation=annotation,
					action__in=['start',
								'finish annotation',
								'finish annotation and load next'])
		for log in logs:
			if log.action == 'start' && log != logs[0]:
				last_log = all_logs[list(all_logs).index(log) - 1]
				if not last_log.action in ['finish annotation', 'finish annotation and load next']:
					finish_time += last_log.time
			else:
				finish_time += log.time
		finish_times.append(finish_time)

	if model_obj.__class__.__name__ == 'Annotation':
		return finish_times[0]
	else:
		return ([np.mean(finish_times), np.var(finish_times)], [ids, finish_times])


def get_annotation_time_in_event_and_region_state_stats(model_obj):
	if model_obj.__class__.__name__ == 'Porject':
		annotations = Annotation.objects.filter(segment__wav__project=model_obj)
	elif model_obj.__class__.__name__ == 'Wav':
		annotations = Annotation.objects.filter(segment__wav=model_obj)
	elif model_obj.__class__.__name__ == 'Segment':
		annotations = Annotation.objects.filter(segment=model_obj)
	elif model_obj.__class__.__name__ == 'Annotation':
		annotations = [model_obj]
	else:
		raise ValueError('Model should be Project, Wav, Segment or Annotation')

	if not model_obj.__class__.__name__ == 'Annotation':
		ids = annotations.values_list('id', flat=True)
	else:
		ids = [model_obj.id]

	events_state_times = []
	regions_state_times = []
	for annotation in annotations:
		current_state = 'events_state'
		events_state_time = 0
		regions_state_time = 0
		all_logs = Log.objects.filter(annotation=annotation)
		logs = Log.objects.filter(
					annotation=annotation,
					action__in=['start',
								'solve overlaps',
								'back to annotation',
								'finish annotation',
								'finish annotation and load next'])
		
		for log in logs:
			if log.action == 'start' && log != logs[0] && current_state == 'event_state':
				last_log = all_logs[list(all_logs).index(log) - 1]
				if not last_log.action in ['solve overlaps',
										   'back to annotation',
										   'finish annotation',
										   'finish annotation and load next']:
					events_state_time += all_logs[list(all_logs).index(log) - 1].time
			elif log.action == 'start' && log != logs[0] && current_state == 'region_state':
				last_log = all_logs[list(all_logs).index(log) - 1]
				if not last_log.action in ['solve overlaps',
										   'back to annotation',
										   'finish annotation',
										   'finish annotation and load next']:
					regions_state_time += all_logs[list(all_logs).index(log) - 1].time
			elif log.action == 'solve overlaps':
				current_state = 'regions_state'
				events_state_time += log.time
			elif log.action == 'back to annotation':
				current_state = 'events_state'
				regions_state_time += log.time
			elif log.action in ['finish annotation', 'finish annotation and load next']:
				if current_state == 'events_state':
					events_state_time += log.time
				else:
					regions_state_time += log.time

		event_state_times.append(events_state_time)
		region_state_times.append(regions_state_time)

	if model_obj.__class__.__name__ == 'Annotation':
		return events_state_times[0], region_state_times[0]
	else:
		return ([np.mean(events_state_times),
				np.var(events_state_times),
				np.mean(regions_state_times),
				np.var(regions_state_times)],
				[ids,
				events_state_times,
				region_state_times])


def get_audio_playback_time_stats(model_obj):
	if model_obj.__class__.__name__ == 'Porject':
		annotations = Annotation.objects.filter(segment__wav__project=model_obj)
	elif model_obj.__class__.__name__ == 'Wav':
		annotations = Annotation.objects.filter(segment__wav=model_obj)
	elif model_obj.__class__.__name__ == 'Segment':
		annotations = Annotation.objects.filter(segment=model_obj)
	elif model_obj.__class__.__name__ == 'Annotation':
		annotations = [model_obj]
	else:
		raise ValueError('Model should be Project, Wav, Segment or Annotation')

	if not model_obj.__class__.__name__ == 'Annotation':
		ids = annotations.values_list('id', flat=True)
	else:
		ids = [model_obj.id]

	total_playbacks = []
	end_of_waveforms = []
	for annotation in annotations:
		logs = Log.objects.filter(
					annotation=annotation,
					action__in=['play', 'pause', 'end of waveform'])

		start = 0
		intervals = []
		interval = [0,0]
		total_playback = 0
		end_of_waveform = 0
		for log in logs:
			if log.action == 'play':
				interval[0] = log.time
			elif log.action == 'pause':
				interval[1] = log.time
				intervals.append(interval)
				total_playback += interval[1] - interval[0]
			else:
				end_of_waveform = 1
		end_of_waveforms.append(end_of_waveform)

	return ([total_playback, np.mean(end_of_waveforms)], [ids, end_of_waveforms])


def get_region_actions_stats(model_obj):
	if model_obj.__class__.__name__ == 'Porject':
		annotations = Annotation.objects.filter(segment__wav__project=model_obj)
	elif model_obj.__class__.__name__ == 'Wav':
		annotations = Annotation.objects.filter(segment__wav=model_obj)
	elif model_obj.__class__.__name__ == 'Segment':
		annotations = Annotation.objects.filter(segment=model_obj)
	elif model_obj.__class__.__name__ == 'Annotation':
		annotations = [model_obj]
	else:
		raise ValueError('Model should be Project, Wav, Segment or Annotation')

	if not model_obj.__class__.__name__ == 'Annotation':
		ids = annotations.values_list('id', flat=True)
	else:
		ids = [model_obj.id]

	for annotation in annotations:
		logs = Log.objects.filter(
					annotation=annotation,
					action__in=['update region limits mouse', 'update region limits keyboard',
								'update region class mouse', 'update region class keyboard',
								'shortcut F'])

		for log in logs:


# Number of errors
# Prominence
# Waveform navigation (seek, s, b)