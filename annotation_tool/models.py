from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
	name = models.CharField(max_length=50, unique=True)
	creation_date = models.DateTimeField('creation date')

	def __str__(self):
		return str(self.name)


class Class(models.Model):
	name = models.CharField(max_length=50)
	tags = models.ManyToManyField('Tag') # if none -> free tag

	def __str__(self):
		return str(self.name)


class Wav(models.Model):
	project = models.ForeignKey('Project', on_delete=models.CASCADE)
	file = models.FileField(upload_to="/home/bmelendez/musicspeech_annotation_project/django_test/", max_length=500)
	name = models.CharField(max_length=100)
	upload_date = models.DateTimeField('upload date')

	def __str__(self):
		return str(self.name)


class Segment(models.Model):
	wav = models.ForeignKey('Wav', on_delete=models.CASCADE)
	start_time = models.FloatField()
	end_time = models.FloatField()
	name = models.CharField(max_length=100)
	number_of_annotations = models.IntegerField(blank=True)
	difficulty = models.FloatField(blank=True)
	priority = models.FloatField(blank=True)

	def __str__(self):
		return str(self.name)


class Annotation(models.Model):
	segment = models.ForeignKey('Segment', on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	annotation_date = models.DateTimeField('annotation date')

	class Meta:
		unique_together = ("segment","user")

	def __str__(self):
		return str(self.id)


class Event(models.Model):
	annotation = models.ForeignKey('Annotation', on_delete=models.CASCADE)
	event_class = models.ForeignKey('Class', on_delete=models.CASCADE)
	start_time = models.FloatField()
	end_time = models.FloatField()
	tags = models.ManyToManyField('Tag', blank=True)

	def __str__(self):
		return str(self.id)


class Region(models.Model):
	annotation = models.ForeignKey('Annotation', on_delete=models.CASCADE)
	start_time = models.FloatField()
	end_time = models.FloatField()
	weight = models.FloatField(null=True, blank=True)


class Tag(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return str(self.name)
