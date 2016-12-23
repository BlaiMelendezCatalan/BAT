from django import forms
from rest_framework import serializers

from annotation_tool.models import Project


class ProjectSerializer(serializers.Serializer):
    project_name = serializers.CharField(label='Add new project', max_length=50)


class ClassSerializer(serializers.Serializer):
    class_name = serializers.CharField(label='Add new class', max_length=50)


class UploadDataSerializer(serializers.Serializer):
    project_name = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    segments_length = serializers.FloatField(label='Segment length')
    upload_file_field = serializers.FileField()
