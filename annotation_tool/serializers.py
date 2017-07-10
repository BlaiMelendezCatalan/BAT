from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers
from django.utils import timezone
import colorsys

from annotation_tool import models


class ProjectSerializer(serializers.Serializer):
    project_name = serializers.CharField(label='Project name', max_length=50)
    overlap = serializers.BooleanField(label='Allow class overlap in this project', default=False)
    class_names = list(models.Class.objects.values_list("name", flat=True).order_by("name"))
    classes = serializers.MultipleChoiceField(choices=class_names)

    def create(self, validated_data):
        project = models.Project(name=validated_data['project_name'],
                                 overlap=validated_data['overlap'],
                                 creation_date=timezone.now())
        project.save()
        n_colors = len(validated_data['classes'])
        colors = []
        for i in xrange(n_colors):
            colors.append(colorsys.hsv_to_rgb(i / float(n_colors), 1, 1))
        for i, class_name in enumerate(sorted(validated_data['classes'])):
            c = models.Class.objects.get(name=class_name)
            print colors[i]
            rgba_color = "rgba(%.2f, %.2f, %.2f, 0.5)" % (255 * colors[i][0],
                                                          255 * colors[i][1],
                                                          255 * colors[i][2])
            print rgba_color
            ci = models.ClassInstance.objects.create(project=project,
                                                     class_obj=c,
                                                     shortcut=i + 1,
                                                     color=rgba_color)
            ci.save()
        return project


class TagSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)


class ClassSerializer(serializers.Serializer):
    name = serializers.CharField(label='Class name', max_length=50)

    def validate(self, data):
        objects = models.Class.objects.filter(name=data.get('name'))
        if objects:
            raise serializers.ValidationError('Class with current params already exists.')

        return data

    def create(self, validated_data):
        validated_data['name'] = validated_data['name'].replace(' ', '_')
        class_object = models.Class(**validated_data)
        class_object.save()
        return class_object


class UploadDataSerializer(serializers.Serializer):
    project = serializers.PrimaryKeyRelatedField(queryset=models.Project.objects.all())
    segments_length = serializers.FloatField(label='Segment length')
    upload_file_field = serializers.FileField(style={'template': 'fields/_file_field.html'})


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


#class ClassProminenceSerializer(serializers.Serializer):
#    region = serializers.PrimaryKeyRelatedField(queryset=models.Region.objects.all())
#    class_obj = serializers.PrimaryKeyRelatedField(queryset=models.Class.objects.all())
#    prominence = serializers.IntegerField(required=False,
#                                          min_value=models.ClassProminence.VERY_LOW,
#                                          max_value=models.ClassProminence.VERY_LOUD)
#
#    def create(self, validated_data):
#        obj = models.ClassProminence(**validated_data)
#        obj.save()
#        return obj


#class RegionSerializer(serializers.Serializer):
#    annotation = serializers.PrimaryKeyRelatedField(queryset=models.Annotation.objects.all())
#    start_time = serializers.FloatField()
#    end_time = serializers.FloatField()
#    tags = TagSerializer(many=True)
#    color = serializers.CharField(max_length=50, allow_blank=True)
#    classes = serializers.CharField()

#    def create(self, validated_data):
#        classes = validated_data.pop('classes')
#        validated_data.pop('tags')
#
#        region = models.Region(**validated_data)
#        region.save()
#
#        # add tags
#        if 'tags[]' in self.initial_data:
#            tags = dict(self.initial_data)['tags[]']
#            tags = map(lambda name: models.Tag.objects.get_or_create(name=name)[0], tags)
#            region.tags.add(*tags)
#
#        # add classes
#        classes = map(lambda name: models.Class.objects.get(name=name, project=region.get_project()), classes.split())
#        for class_obj in classes:
#            data = {'region': region.id, 'class_obj': class_obj.id}
#            class_prominence = ClassProminenceSerializer(data=data)
#            class_prominence.is_valid(raise_exception=True)
#            class_prominence.save()
#
#        return region
