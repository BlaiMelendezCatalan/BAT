from django import forms

class CreateProjectForm(forms.Form):
    project_name = forms.CharField(label='Add new project', max_length=50)

class UploadDataForm(forms.Form):
    project_name = forms.CharField(label='Project name', max_length=50)
    segments_length = forms.FloatField(label='Segment length')
    upload_file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

class LoginForm(forms.Form):
	username = forms.CharField(label='Username', max_length=50)
	password = forms.CharField(label='Password', max_length=50, widget=forms.PasswordInput)
