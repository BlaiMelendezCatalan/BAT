# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-08-23 18:03
from __future__ import unicode_literals

import annotation_tool.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('annotation_date', models.DateTimeField(verbose_name='annotation date')),
                ('status', models.CharField(choices=[('finished', 'finished'), ('unfinished', 'unfinished')], default='unfinished', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ClassInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shortcut', models.PositiveSmallIntegerField()),
                ('color', models.CharField(max_length=50)),
                ('class_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation_tool.Class')),
            ],
        ),
        migrations.CreateModel(
            name='ClassProminence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prominence', models.PositiveSmallIntegerField(blank=True, choices=[(1, ''), (2, ''), (3, ''), (4, ''), (5, 'Most salient')], null=True)),
                ('class_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation_tool.Class')),
            ],
            options={
                'ordering': ('class_obj__name',),
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.FloatField()),
                ('end_time', models.FloatField()),
                ('color', models.CharField(blank=True, max_length=50)),
                ('annotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation_tool.Annotation')),
                ('event_class', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='annotation_tool.Class')),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=50)),
                ('value', models.CharField(blank=True, max_length=50)),
                ('time', models.FloatField()),
                ('annotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation_tool.Annotation')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('creation_date', models.DateTimeField(verbose_name='creation date')),
                ('overlap', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.FloatField()),
                ('end_time', models.FloatField()),
                ('color', models.CharField(blank=True, max_length=50)),
                ('annotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation_tool.Annotation')),
            ],
        ),
        migrations.CreateModel(
            name='Segment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.FloatField()),
                ('end_time', models.FloatField()),
                ('name', models.CharField(max_length=1000)),
                ('priority', models.FloatField(default=2.0)),
                ('reliable', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Wav',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(max_length=500, upload_to=annotation_tool.models.get_wav_file_path)),
                ('name', models.CharField(max_length=1000)),
                ('upload_date', models.DateTimeField(verbose_name='upload date')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation_tool.Project')),
            ],
        ),
        migrations.AddField(
            model_name='segment',
            name='wav',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation_tool.Wav'),
        ),
        migrations.AddField(
            model_name='region',
            name='tags',
            field=models.ManyToManyField(blank=True, to='annotation_tool.Tag'),
        ),
        migrations.AddField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(blank=True, to='annotation_tool.Tag'),
        ),
        migrations.AddField(
            model_name='classprominence',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='annotation_tool.Region'),
        ),
        migrations.AddField(
            model_name='classinstance',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation_tool.Project'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='segment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation_tool.Segment'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='region',
            unique_together=set([('annotation', 'start_time', 'end_time')]),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('annotation', 'event_class', 'start_time', 'end_time')]),
        ),
        migrations.AlterUniqueTogether(
            name='classinstance',
            unique_together=set([('project', 'class_obj')]),
        ),
        migrations.AlterUniqueTogether(
            name='annotation',
            unique_together=set([('segment', 'user')]),
        ),
    ]
