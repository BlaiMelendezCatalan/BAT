from django.contrib.auth.models import User
from rest_framework import serializers

from annotation_tool.models import Project


class ProjectSerializer(serializers.Serializer):
    project_name = serializers.CharField(label='Add new project', max_length=50)


class ClassSerializer(serializers.Serializer):
    class_name = serializers.CharField(label='Add new class', max_length=50)


class UploadDataSerializer(serializers.Serializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
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
            User.objects.get(username=data.get('username'))
        except User.DoesNotExist:
            pass
        else:
            raise serializers.ValidationError('User already exists.')

        return data

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(self.validated_data['password'])
        user.save()
        return user
