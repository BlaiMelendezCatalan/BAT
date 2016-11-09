import datetime
import django.core.exceptions as e
from annotation_tool.models import Project, Wav, Segment



def create_project(project_name):
	if project_name != "":
		p = Project(name=project_name, creation_date=datetime.datetime.now())
		p.save()


def attach_wav_files_to_project(project_name, input_dir):

	if input_dir[-1] != '/':
		input_dir = input_dir + '/'

	try:
		p = Project.objects.get(name=project_name)
	except:
		raise e.ObjectDoesNotExist("Create project %s first" % project_name)
	for fnames in os.walk(input_dir):
		for fname in fnames:
			abs_path = os.path.abs_path(input_dir + fname)
			w = Wav(project=p,
					abs_path=abs_path,
					name = abs_path.split('/')[-1],
					upload_date=datetime.datetime.now())
			w.save()
			#Create segments


#def annotate_segment():