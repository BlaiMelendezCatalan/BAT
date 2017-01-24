from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers
from django.utils import timezone

from annotation_tool import models


class ProjectSerializer(serializers.Serializer):
    project_name = serializers.CharField(label='Project name', max_length=50)
    overlap = serializers.BooleanField(label='Allow class overlap in this project', default=False)

    def create(self, validated_data):
        project = models.Project(name=validated_data['project_name'],
                                 overlap=validated_data['overlap'],
                                 creation_date=timezone.now())
        project.save()
        return project


class TagSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)


class ClassSerializer(serializers.Serializer):
    project = serializers.PrimaryKeyRelatedField(queryset=models.Project.objects.all())
    name = serializers.CharField(label='Class name', max_length=50)
    tags = TagSerializer(many=True,
                         style={'template': 'fields/_tag_field.html'})
    color = serializers.CharField(label='Color',
                                  max_length=50,
                                  style={'template': 'fields/_colorpicker_field.html'})
    shortcut = serializers.CharField(max_length=1)

    def validate(self, data):
        objects = models.Class.objects.filter(project=data.get('project'))\
            .filter(Q(name=data.get('name')) |
                    Q(shortcut=data.get('shortcut')) |
                    Q(color=data.get('color')))
        if objects:
            raise serializers.ValidationError('Class with current params already exists.')

        return data

    def create(self, validated_data):
        del validated_data['tags']
        class_object = models.Class(**validated_data)
        class_object.save()
        # add tags
        tags = []
        for tag_name in self.initial_data['tags'].split(', '):
            if tag_name:
                tag, _ = models.Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
        class_object.tags = tags
        class_object.save()
        return class_object


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


class ClassProminenceSerializer(serializers.Serializer):
    region = serializers.PrimaryKeyRelatedField(queryset=models.Region.objects.all())
    class_obj = serializers.PrimaryKeyRelatedField(queryset=models.Class.objects.all())
    prominence = serializers.IntegerField(required=False,
                                          min_value=models.ClassProminence.VERY_LOW,
                                          max_value=models.ClassProminence.VERY_LOUD)

    def create(self, validated_data):
        obj = models.ClassProminence(**validated_data)
        obj.save()
        return obj


class RegionSerializer(serializers.Serializer):
    annotation = serializers.PrimaryKeyRelatedField(queryset=models.Annotation.objects.all())
    start_time = serializers.FloatField()
    end_time = serializers.FloatField()
    tags = TagSerializer(many=True)
    color = serializers.CharField(max_length=50, allow_blank=True)
    classes = serializers.CharField()

    def create(self, validated_data):
        classes = validated_data.pop('classes')
        validated_data.pop('tags')

        region = models.Region(**validated_data)
        region.save()

        # add tags
        if 'tags[]' in self.initial_data:
            tags = dict(self.initial_data)['tags[]']
            tags = map(lambda name: models.Tag.objects.get_or_create(name=name)[0], tags)
            region.tags.add(*tags)

        # add classes
        classes = map(lambda name: models.Class.objects.get(name=name, project=region.get_project()), classes.split())
        for class_obj in classes:
            data = {'region': region.id, 'class_obj': class_obj.id}
            class_prominence = ClassProminenceSerializer(data=data)
            class_prominence.is_valid(raise_exception=True)
            class_prominence.save()

        return region
