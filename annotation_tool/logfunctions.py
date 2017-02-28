import os
from math import ceil, floor
import numpy as np
import random
import datetime
from annotation_tool.models import Project, Wav, Segment, Annotation, Event, Tag, Class, ClassProminence, Annotator
import annotation_tool.utils


ALL_ACTIONS = ['start', 'play mouse', 'pause mouse', 'play keyboard', 'pause keyboard', 'shortcut B', 'shortcut S',
			   'update region limits mouse', 'update region limits keyboard', 'update region class mouse',
			   'update region class keyboard', 'select region', 'shortcut F', 'add tags', 'delete tag',
			   'create region', 'click-delete region', 'cross-delete region', 'update class prominence',
			   'toggle prominence popup', 'back to annotation','overlaps not solved', 'prominence not assigned',
			   'classes not assigned before solve overlaps', 'switch view', 'click tips button',
			   'click controls button', 'finish annotation', 'finish annotation and load next', 'seek',
			   'end of waveform', 'adjust limits', 'avoid padding', 'prevent overlap on creation',
			   'prevent overlap on arrow', 'untoggle prominence popup', 'solve overlaps	']
NONE_ACTIONS = ['seek', 'end of waveform', 'adjust limits', 'avoid padding', 'prevent overlap on creation',
				'prevent overlap on arrow', 'untoggle prominence popup']


def get_annotations(model_obj):
	if model_obj.__class__.__name__ == 'Porject':
		annotations = Annotation.objects.filter(segment__wav__project=model_obj)
	elif model_obj.__class__.__name__ == 'Wav':
		annotations = Annotation.objects.filter(segment__wav=model_obj)
	elif model_obj.__class__.__name__ == 'Segment':
		annotations = Annotation.objects.filter(segment=model_obj)
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
		logs = Log.objects.filter(annotation=annotation)
		for i in xrange(len(logs)):
			if i != 0:
				total_time += logs[i] - logs[i - 1]
				if logs[i].action in ['play mouse', 'play keyboard']:
					start = logs[i].time
				elif logs[i].action in ['pause mouse', 'pause keyboard']:
					total_playback_time += logs[i].time - start
				elif logs[i].action == 'end of waveform':
					end_of_waveform += 1
				elif not logs[i].action in NONE_ACTIONS:
					total_annotation_time += logs[i] - logs[i - 1]

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
		logs = Log.objects.filter(annotation=annotation)
		for i in xrange(len(logs) - 1):
			if i != 0:
				if logs[i].action == 'solve overlaps':
					current_state = 'regions_state'
					events_state_time += logs[i].time - logs[i - 1].time
				elif logs[i].action == 'back to annotation':
					current_state = 'events_state'
					regions_state_time += logs[i].time - logs[i - 1].time
				else:
					if current_state == 'events_state':
						events_state_time += logs[i].time - logs[i - 1].time
					else:
						region_state_times += logs[i].time - logs[i - 1].time

		user_dict[annotation.user.username]['events_state'].append(events_state_time)
		user_dict[annotation.user.username]['regions_state'].append(regions_state_time)

	return user_dict


def get_all_actions_use_times(model_obj):
	annotations = get_annotations(model_obj)
	user_dict = {}
	for annotation in annotations:
		if not annotation.user.username in user_dict.keys():
			user_dict[annotation.user.username] = {}
		for action in ALL_ACTIONS:
			logs = Log.objects.filter(annotation=annotation, action=action)
			user_dict[annotation.user.username][action] = []
			user_dict[annotation.user.username][action].append(len(logs))

	return user_dict


def get_number_of_extra_actions(model_obj):
	annotations = get_annotations(model_obj)
	user_dict = get_all_actions_use_times(model_obj)
	for user in user_dict.keys():
		user_dict[user]['number_of_regions'] = []
		user_dict[user]['number_of_regions_multiclass'] = []
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
			extra_limits_update = max(0, user_dict[user]['update region limits mouse'][i] - \
								  number_of_regions)
			extra_shortcut_f = max(0, user_dict[user]['shortcut F'][i] - \
							   number_of_regions)
			extra_toggles = max(0, user_dict[user]['toggle prominence popup'][i] - \
							number_of_regions_multiclass)
			extra_prom_updates = max(0, user_dict[user]['update class prominence'][i] - \
								 number_of_toggle_lines)
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
				deletes + backs + solves + finishes + errors + tips_controls)

	return user_dict


def get_action_use_times(model_obj, action):
	annotations = get_annotations(model_obj)
	user_dict = {}
	for annotation in annotations:
		if not annotation.user.username in user_dict.keys():
			user_dict[annotation.user.username] = {}
			user_dict[annotation.user.username][action] = []
		logs = Log.objects.filter(annotation=annotation, action=action)
		user_dict[annotation.user.username][action].append(len(logs))

	return user_dict
