from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers

from annotation_tool import models


class ProjectSerializer(serializers.Serializer):
    project_name = serializers.CharField(label='Project name', max_length=50)
    overlap = serializers.BooleanField(label='Allow class overlap in this project', default=False)


class TagSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)


class ClassSerializer(serializers.Serializer):
    project = serializers.PrimaryKeyRelatedField(queryset=models.Project.objects.all())
    name = serializers.CharField(label='Class name', max_length=50)
    tags = TagSerializer(many=True,
                         style={'template': 'annotation_tool/_tag_field.html'})
    color = serializers.CharField(label='Color',
                                  max_length=50,
                                  style={'template': 'annotation_tool/_colorpicker_field.html'})
    shortcut = serializers.CharField(max_length=1)

    def validate(self, data):
        try:
            models.Class.objects.get(Q(name=data.get('name')) |
                                     Q(shortcut=data.get('shortcut')) |
                                     Q(color=data.get('color')))
        except models.Class.DoesNotExist:
            pass
        else:
            raise serializers.ValidationError('Class with current params already exists.')

        return data

    def create(self, validated_data):
        del validated_data['tags']
        c = models.Class(**validated_data)
        c.save()
        # add tags
        tags = []
        for tag_name in self.initial_data['tags'].split(', '):
            tag, _ = models.Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)
        c.tags = tags
        c.save()
        return c


class UploadDataSerializer(serializers.Serializer):
    project = serializers.PrimaryKeyRelatedField(queryset=models.Project.objects.all())
    segments_length = serializers.FloatField(label='Segment length')
    upload_file_field = serializers.FileField()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(label='Username',
                                     max_length=50)
    password = serializers.CharField(label='Password',
                                     max_length=50,
                                     style={'input_type': 'password'})


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(label='Username',
                                     max_length=50)
    password = serializers.CharField(label='Password',
                                     max_length=50,
                                     style={'input_type': 'password'})
    confirm_password = serializers.CharField(label='Confirm password',
                                             max_length=50,
                                             style={'input_type': 'password'})

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError('Those passwords don\'t match.')

        try:
            models.User.objects.get(username=data.get('username'))
        except models.User.DoesNotExist:
            pass
        else:
            raise serializers.ValidationError('User already exists.')

        return data

    def create(self, validated_data):
        user = models.User(username=validated_data['username'])
        user.set_password(self.validated_data['password'])
        user.save()
        return user
