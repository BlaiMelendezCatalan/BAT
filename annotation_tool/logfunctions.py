import os
from math import ceil, floor
import numpy as np
import random
import datetime
from annotation_tool.models import Annotation, Event, Region, ClassProminence, Log
import annotation_tool.utils


ALL_ACTIONS = ['play', 'start', 'play mouse', 'pause mouse', 'play keyboard', 'pause keyboard', 'shortcut B', 'shortcut S',
			   'update region limits mouse', 'update region limits keyboard', 'update region class mouse',
			   'update region class keyboard', 'select region', 'shortcut F', 'add tags', 'delete tag',
			   'create region', 'click-delete region', 'cross-delete region', 'update class prominence',
			   'toggle prominence popup', 'back to annotation','overlaps not solved', 'prominence not assigned',
			   'classes not assigned before solve overlaps', 'switch view', 'click tips button',
			   'click controls button', 'finish annotation', 'finish annotation and load next', 'seek',
			   'end of waveform', 'adjust limits', 'avoid padding', 'prevent overlap on creation',
			   'prevent overlap on arrow', 'untoggle prominence popup', 'solve overlaps']
NONE_ACTIONS = ['seek', 'end of waveform', 'adjust limits', 'avoid padding', 'prevent overlap on creation',
				'prevent overlap on arrow', 'untoggle prominence popup', 'play', 'start']
ANNOTATION_ACTIONS = ['update region limits mouse', 'update region limits keyboard', 'update region class mouse',
			   'update region class keyboard', 'select region', 'shortcut F', 'add tags', 'delete tag',
			   'create region', 'click-delete region', 'cross-delete region', 'update class prominence',
			   'toggle prominence popup', 'back to annotation', 'finish annotation', 'finish annotation and load next',
			   'solve overlaps']


def get_annotations(model_obj):
	if model_obj.__class__.__name__ == 'Project':
		annotations = Annotation.objects.filter(segment__wav__project=model_obj).order_by('id')
	elif model_obj.__class__.__name__ == 'Wav':
		annotations = Annotation.objects.filter(segment__wav=model_obj).order_by('id')
	elif model_obj.__class__.__name__ == 'Segment':
		annotations = Annotation.objects.filter(segment=model_obj).order_by('id')
	else:
		raise ValueError('Model should be Project, Wav, Segment or Annotation')

	return annotations


def get_total_annotation_time_stats(model_obj):
	annotations = get_annotations(model_obj)
	user_dict = {}
	for annotation in annotations:
		if not annotation.user.username in user_dict.keys():
			user_dict[annotation.user.username] = {}
			user_dict[annotation.user.username]['total_time'] = []
			user_dict[annotation.user.username]['total_playback_time'] = []
			user_dict[annotation.user.username]['total_annotation_time'] = []
			user_dict[annotation.user.username]['number_of_end_of_waveform'] = []
			
		total_time = 0
		total_playback_time = 0
		total_annotation_time = 0
		start = 0
		end_of_waveform = 0
		is_playing = True
		logs = Log.objects.filter(annotation=annotation).order_by('id')
		for i in xrange(len(logs)):
			if i != 0:
				total_time += max(0, logs[i].time - logs[i - 1].time)
				if logs[i].action == 'start':
					continue
				elif logs[i].action == 'play':
					start = logs[i].time
					is_playing = True
				elif logs[i].action in ['play mouse', 'play keyboard']:
					start = logs[i].time
					is_playing = True
				elif logs[i].action in ['pause mouse', 'pause keyboard']:
					total_playback_time += logs[i].time - logs[i - 1].time
					is_playing = False
				elif logs[i].action == 'end of waveform':
					total_playback_time += logs[i].time - logs[i - 1].time
					is_playing = False
					end_of_waveform += 1
				elif logs[i - 1].action != 'start':
					if is_playing:
						total_playback_time += logs[i].time - logs[i - 1].time
					if logs[i].action in ANNOTATION_ACTIONS and logs[i - 1].action in ANNOTATION_ACTIONS:
						total_annotation_time += max(0, logs[i].time - logs[i - 1].time)

		user_dict[annotation.user.username]['total_time'].append(total_time)
		user_dict[annotation.user.username]['total_playback_time'].append(total_playback_time)
		user_dict[annotation.user.username]['total_annotation_time'].append(total_annotation_time)
		user_dict[annotation.user.username]['number_of_end_of_waveform'].append(end_of_waveform)

	return user_dict


def get_annotation_time_in_events_and_regions_states_stats(model_obj):
	annotations = get_annotations(model_obj)
	user_dict = {}
	for annotation in annotations:
		if not annotation.user.username in user_dict.keys():
			user_dict[annotation.user.username] = {}
			user_dict[annotation.user.username]['events_state'] = []
			user_dict[annotation.user.username]['regions_state'] = []
		current_state = 'events_state'
		events_state_time = 0
		regions_state_time = 0
		logs = Log.objects.filter(annotation=annotation).order_by('id')
		for i in xrange(len(logs)):
			if i != 0:
				print logs[i - 1].time, logs[i - 1].action, logs[i].time, logs[i].action
				if logs[i].action == 'solve overlaps':
					current_state = 'regions_state'
					events_state_time += logs[i].time - logs[i - 1].time
				elif logs[i].action == 'back to annotation':
					current_state = 'events_state'
					regions_state_time += logs[i].time - logs[i - 1].time
				else:
					if current_state == 'events_state':
						events_state_time += max(0, logs[i].time - logs[i - 1].time)
					else:
						regions_state_time += max(0, logs[i].time - logs[i - 1].time)

		user_dict[annotation.user.username]['events_state'].append(events_state_time)
		user_dict[annotation.user.username]['regions_state'].append(regions_state_time)

	return user_dict


def get_all_actions_use_times(model_obj):
	annotations = get_annotations(model_obj)
	user_dict = {}
	for annotation in annotations:
		if not annotation.user.username in user_dict.keys():
			user_dict[annotation.user.username] = {}
	for user in user_dict.keys():
		for action in ALL_ACTIONS:
			user_dict[user][action] = np.zeros(len(annotations))
	for i in xrange(len(annotations)):
		logs = Log.objects.filter(annotation=annotations[i]).order_by('id')
		for j in xrange(len(logs)):
			print logs[j].action
			if j != 0 and logs[j].action == 'update region limits keyboard':
				if logs[j - 1].action != 'update region limits keyboard':
					user_dict[annotation.user.username]['update region limits keyboard'][i] += 1
			elif logs[j].action == 'update region limits mouse':
				user_dict[annotation.user.username][logs[j].action][i] += 1
				user_dict[annotation.user.username]['select region'][i] -= 1
			else:
				user_dict[annotation.user.username][logs[j].action][i] += 1	

	return user_dict


def get_number_of_extra_actions(model_obj):
	annotations = get_annotations(model_obj)
	user_dict = get_all_actions_use_times(model_obj)
	for user in user_dict.keys():
		user_dict[user]['number_of_regions'] = []
		user_dict[user]['number_of_regions_multiclass'] = []
		user_dict[user]['number_of_toggle_lines'] = []
		user_dict[user]['total_extra_annotation_actions'] = []
	for annotation in annotations:
		regions = Region.objects.filter(annotation=annotation)
		if regions:
			number_of_regions_multiclass = 0
			number_of_toggle_lines = 0
			for region in regions:
				cp = ClassProminence.objects.filter(region=region)
				if len(cp) > 1:
					number_of_regions_multiclass += 1
					number_of_toggle_lines += len(cp)
			user_dict[annotation.user.username][
						'number_of_regions_multiclass'].append(number_of_regions_multiclass)
			user_dict[annotation.user.username][
						'number_of_toggle_lines'].append(number_of_toggle_lines)
		else:
			regions = Event.objects.filter(annotation=annotation)
			user_dict[annotation.user.username][
						'number_of_regions_multiclass'].append(0)
			user_dict[annotation.user.username][
						'number_of_toggle_lines'].append(0)
		user_dict[annotation.user.username]['number_of_regions'].append(len(regions))
	for user in user_dict.keys():
		for i in xrange(len(user_dict[user]['number_of_regions'])):
			number_of_regions = user_dict[user]['number_of_regions'][i]
			number_of_regions_multiclass = user_dict[annotation.user.username][
												'number_of_regions_multiclass'][i]
			number_of_toggle_lines = user_dict[annotation.user.username][
												'number_of_toggle_lines'][i]
			extra_class_update = max(0, user_dict[user]['update region class mouse'][i] + \
								 user_dict[user]['update region class keyboard'][i] - \
								 number_of_regions)
			extra_limits_update = max(0, user_dict[user]['update region limits mouse'][i] + \
								  user_dict[user]['update region limits keyboard'][i] - \
								  number_of_regions)
			extra_shortcut_f = max(0, user_dict[user]['shortcut F'][i] - \
							   number_of_regions)
			extra_toggles = max(0, user_dict[user]['toggle prominence popup'][i] - \
							number_of_regions_multiclass)
			extra_prom_updates = max(0, user_dict[user]['update class prominence'][i] - \
								 number_of_toggle_lines)
			extra_selects = max(0, user_dict[user]['select region'][i] - number_of_regions)
			deletes = user_dict[user]['click-delete region'][i] + \
					  user_dict[user]['cross-delete region'][i]
			backs = user_dict[user]['back to annotation'][i]
			solves = max(0, user_dict[user]['solve overlaps'][i] - 1)
			finishes = max(0, user_dict[user]['finish annotation'][i] + \
							  user_dict[user]['finish annotation and load next'][i] - 1)
			errors = user_dict[user]['overlaps not solved'][i] + \
					 user_dict[user]['prominence not assigned'][i] + \
					 user_dict[user]['classes not assigned before solve overlaps'][i]
			tips_controls = user_dict[user]['click controls button'][i] + \
							user_dict[user]['click tips button'][i]
			user_dict[user]['total_extra_annotation_actions'].append(extra_class_update + \
				extra_limits_update + extra_shortcut_f + extra_toggles + extra_prom_updates + \
				extra_selects + deletes + backs + solves + finishes + errors + tips_controls)

	return user_dict


def get_number_of_overlaps(model_obj):
	annotations = get_annotations(model_obj)
	user_dict = {}
	for annotation in annotations:
		if not annotation.user.username in user_dict.keys():
			user_dict[annotation.user.username] = {}
			user_dict[annotation.user.username]['number of overlaps'] = []
			user_dict[annotation.user.username]['number of classes per overlap'] = []
			user_dict[annotation.user.username]['classes per overlap'] = []
		number_of_overlaps = 0
		number_of_classes_per_overlap = []
		regions = Region.objects.filter(annotation=annotation)
		if regions:
			number_of_regions_multiclass = 0
			number_of_toggle_lines = 0
			for region in regions:
				cp = ClassProminence.objects.filter(region=region)
				if len(cp) > 1:
					number_of_overlaps += 1
					number_of_classes_per_overlap.append(len(cp))
			user_dict[annotation.user.username][
						'number of overlaps'].append(number_of_overlaps)
			user_dict[annotation.user.username][
						'number of classes per overlap'].append(number_of_classes_per_overlap)
		else:
			regions = Event.objects.filter(annotation=annotation)
			user_dict[annotation.user.username][
						'number of overlaps'].append(0)
			user_dict[annotation.user.username][
						'number of classes per overlap'].append([])

	return user_dict
