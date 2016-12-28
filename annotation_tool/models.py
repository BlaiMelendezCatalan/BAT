from __future__ import unicode_literals

import os

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)
    creation_date = models.DateTimeField('creation date')
    overlap = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class Class(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    tags = models.ManyToManyField('Tag', blank=True)  # if none -> free tag
    color = models.CharField(max_length=50)
    shortcut = models.CharField(max_length=1)

    def __str__(self):
        return str(self.name)


# class Subclass(models.Model): # for overlapping zones


class Wav(models.Model):
    def get_file_path(self, filename):
        return os.path.join('uploaded_wavs', '%s' % slugify(self.project.name), filename)

    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=get_file_path,
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
    priority = models.FloatField(default=2.0)

    def __str__(self):
        return str(self.start_time) + '_' + str(self.end_time)


class Annotation(models.Model):
    FINISHED = 'finished'
    UNFINISHED = 'unfinished'
    STATUS_CHOICES = (
        (FINISHED, FINISHED),
        (UNFINISHED, UNFINISHED)
    )
    segment = models.ForeignKey('Segment', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    annotation_date = models.DateTimeField('annotation date')
    status = models.CharField(max_length=10, default=UNFINISHED, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ("segment", "user")

    def __str__(self):
        return str(self.name)


class Event(models.Model):
    annotation = models.ForeignKey('Annotation', on_delete=models.CASCADE)
    # class_name is the name of a Class object if no overlappings are allowed. Otherwise, it is a secondary (mixture) class name
    event_class = models.ForeignKey('Class', null=True,
                                    on_delete=models.CASCADE)  # This should be models.ManyToManyField('Class', blank=True) to allow overlappings
    start_time = models.FloatField(default=0.0)
    end_time = models.FloatField(default=0.01)
    color = models.CharField(max_length=50, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)

    class Meta:
        unique_together = ("annotation", "event_class", "start_time",
                           "end_time")  # This should be unique_together = ("annotation", "start_time", "end_time") to allow overlappings

    def __str__(self):
        return str(self.id)


class Region(models.Model):
    segment = models.ForeignKey('Segment', on_delete=models.CASCADE)
    # class_name is the name of a Class object if no overlappings are allowed. Otherwise, it is a secondary (mixture) class name
    class_name = models.FloatField(null=True, blank=True)
    start_time = models.FloatField()
    end_time = models.FloatField()

    class Meta:
        unique_together = ("segment", "start_time", "end_time")

    def __str__(self):
        return str(self.class_name)


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=50)

    @staticmethod
    def get_tag_names():
        return ','.join([tag.name for tag in Tag.objects.all()])


    def __str__(self):
        return str(self.name)
