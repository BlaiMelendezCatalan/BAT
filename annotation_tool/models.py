from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from annotation_project.settings import BASE_DIR


class Project(models.Model):
	name = models.CharField(max_length=50, unique=True)
	creation_date = models.DateTimeField('creation date')

	def __str__(self):
		return str(self.name)


class Class(models.Model):
	name = models.CharField(max_length=50)
	tags = models.ManyToManyField('Tag', blank=True) # if none -> free tag
	color = models.CharField(max_length=50)
	shortcut = models.CharField(max_length=1)

	def __str__(self):
		return str(self.name)


class Wav(models.Model):
	project = models.ForeignKey('Project', on_delete=models.CASCADE)
	file = models.FileField(
		upload_to=BASE_DIR + "/django_test/",
		max_length=500)
	name = models.CharField(max_length=100)
	upload_date = models.DateTimeField('upload date')

	def __str__(self):
		return str(self.name)


class Segment(models.Model):
	wav = models.ForeignKey('Wav', on_delete=models.CASCADE)
	start_time = models.FloatField()
	end_time = models.FloatField()
	name = models.CharField(max_length=100)
	number_of_annotations = models.IntegerField(default=0)
	difficulty = models.FloatField(default=1.0)
	priority = models.FloatField(default=0.0)

	def __str__(self):
		return str(self.name)


class Annotation(models.Model):
	segment = models.ForeignKey('Segment', on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	annotation_date = models.DateTimeField('annotation date')
	status = models.CharField(max_length=10, default="unfinished")

	class Meta:
		unique_together = ("segment","user")

	def __str__(self):
		return str(self.name)


class Event(models.Model):
	annotation = models.ForeignKey('Annotation', on_delete=models.CASCADE)
	event_class = models.ForeignKey('Class', null=True, on_delete=models.CASCADE)
	start_time = models.FloatField(default=0.0)
	end_time = models.FloatField(default=0.01)
	color = models.CharField(max_length=50, blank=True)
	tags = models.ManyToManyField('Tag', blank=True)

	class Meta:
		unique_together = ("annotation", "event_class", "start_time", "end_time")

	def __str__(self):
		return str(self.id)


class Tag(models.Model):
	name = models.CharField(unique=True, max_length=50)

	def __str__(self):
		return str(self.name)
