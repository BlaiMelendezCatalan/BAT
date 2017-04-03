from __future__ import unicode_literals

import os

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
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
    shortcut = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = (('project', 'name'), ('project', 'color'), ('project', 'shortcut'))
        ordering = ('shortcut',)

    def __str__(self):
        return str(self.name)


def get_wav_file_path(self, filename):
    return os.path.join('uploaded_wavs', '%s' % slugify(self.project.name), filename)


class Wav(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=get_wav_file_path,
        max_length=500)
    name = models.CharField(max_length=1000)
    upload_date = models.DateTimeField('upload date')

    def __str__(self):
        return str(self.name)


@receiver(models.signals.post_delete, sender=Wav)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
        Deletes file from filesystem
        when corresponding `Wav` object is deleted.
    """
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)


class Segment(models.Model):
    wav = models.ForeignKey('Wav', on_delete=models.CASCADE)
    start_time = models.FloatField()
    end_time = models.FloatField()
    name = models.CharField(max_length=1000)
    priority = models.FloatField(default=2.0)
    reliable = models.BooleanField(default=False)

    def get_project(self):
        return self.wav.project

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
    name = models.CharField(max_length=1000)
    annotation_date = models.DateTimeField('annotation date')
    status = models.CharField(max_length=10, default=UNFINISHED, choices=STATUS_CHOICES)

    def get_project(self):
        return self.segment.wav.project

    class Meta:
        unique_together = ("segment", "user")

    def __str__(self):
        return str(self.name)


class Event(models.Model):
    annotation = models.ForeignKey('Annotation', on_delete=models.CASCADE)
    event_class = models.ForeignKey('Class', null=True,
                                    on_delete=models.CASCADE)
    start_time = models.FloatField()
    end_time = models.FloatField()
    color = models.CharField(max_length=50, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)

    def get_project(self):
        return self.annotation.get_project()

    class Meta:
        unique_together = ("annotation", "event_class", "start_time",
                           "end_time")

    def __str__(self):
        return str(self.id)


class Region(models.Model):
    annotation = models.ForeignKey('Annotation', on_delete=models.CASCADE)
    start_time = models.FloatField()
    end_time = models.FloatField()
    color = models.CharField(max_length=50, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)

    def get_project(self):
        return self.annotation.get_project()

    class Meta:
        unique_together = ("annotation", "start_time", "end_time")

    def __str__(self):
        return str(self.id)


class ClassProminence(models.Model):
    VERY_LOW = 1
    LOW = 2
    MID = 3
    LOUD = 4
    VERY_LOUD = 5
    PROMINENCE_CHOICES = (
        (VERY_LOW, ''),
        (LOW, ''),
        (MID, ''),
        (LOUD, ''),
        (VERY_LOUD, 'Most salient')
    )
    region = models.ForeignKey(Region, related_name='classes')
    class_obj = models.ForeignKey(Class)
    prominence = models.PositiveSmallIntegerField(choices=PROMINENCE_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.class_obj.name

    class Meta:
        ordering = ('class_obj__name',)



class Tag(models.Model):
    name = models.CharField(unique=True, max_length=50)

    @staticmethod
    def get_tag_names():
        return Tag.objects.values_list('name', flat=True)

    def __str__(self):
        return str(self.name)


class Log(models.Model):
    annotation = models.ForeignKey('Annotation', on_delete=models.CASCADE)
    action = models.CharField(max_length=50, blank=False)
    value = models.CharField(max_length=50, blank=True)
    time = models.FloatField(null=False, blank=False)

    def __str__(self):
        return self.action
