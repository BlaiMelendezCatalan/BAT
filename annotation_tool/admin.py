from django.contrib import admin

from .models import Project, Wav, Segment, Annotation, Event, Class, Tag, Region, ClassProminence, Log

admin.site.register(Project)
admin.site.register(Wav)
admin.site.register(Segment)
admin.site.register(Annotation)
admin.site.register(Event)
admin.site.register(Class)
admin.site.register(Tag)
admin.site.register(Region)
admin.site.register(ClassProminence)
admin.site.register(Log)

# Register your models here.
