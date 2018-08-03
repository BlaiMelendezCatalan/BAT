BAT - BMAT Annotation Tool
==========

Description:
--------------

BAT is an open-source, web-based tool for the manual annotation of events in audio recordings developed at [BMAT](http://www.bmat.com). It was developed in the context of a PhD and right now it is maintained by its author in his free. By no means is it a professional tool.

1. It provides an easy way to annotate the salience of simultaneous sound sources.
2. It allows to define multiple ontologies to adapt to multiple tasks.
3. It offers the possibility to cross-annotate audio data. 
4. It is easy to install and deploy on servers.

![alt text](https://github.com/BlaiMelendezCatalan/BAT/blob/master/other/gif.gif "Annotation process")

Install and run BAT locally or on a server:
--------------

1. Install docker and docker-compose. For the details on docker installation you can use [the official documentation guide](https://docs.docker.com/engine/installation/linux/ubuntulinux/)


2. Clone the **master** branch of this repository.


3. Create file named **.env** in the project root (near the **docker-compose.yml** file) with the following text:

`DJANGO_SETTINGS_MODULE=config.settings.local`

`POSTGRES_PASSWORD=change_this_password`

`POSTGRES_USER=change_this_user`

`DJANGO_SECRET_KEY=insert_a_long_string_with_ascii_chars`

4. Stop the postgresql service on your computer (if it exist).

`$ sudo service postgresql stop`

5. Build BAT.

`$ (sudo) docker-compose build`
    
6. Now you can add an admin user.

`$ (sudo) docker-compose run django python manage.py createsuperuser`

7. Run BAT locally or on a server.

`$ (sudo) docker-compose up`

8. Open http://localhost:8003/annotation_tool/ or **http://<your_server>:8003/annotation_tool/** in your browser. You can change the port in docker-compose.yml.

9. To close BAT, open a new terminal, go to the directory of the repository and type:

`$ (sudo) docker-compose down`

10. To access the database using the DJANGO shell: (to close it use 9.)

`$ (sudo) docker-compose run django python manage.py shell`

11. To log into the postgresql database:

`$ (sudo) docker ps -a` (indentify which is the postgresql container)

`$ (sudo) docker exec -i <container ID> psql -U bat_admin -p 5432`

First steps with BAT:
--------------

1. As the admin you can create projects, define classes and upload wavs to projects. First of all create the set of classes that you want to annotate with. Todo so go to "Classes" and click on "Add Class".

2. Once the classes are defined you need to create the project. Projects are usually named after the type of events that we want to annotate (instrument sounds, chords, everyday life sounds, etc.). To create one, go to "Projects" and click "Add Project". Name it, pick the classes you want to use and choose whether or not events can overlap for your particular annotation task.

3. The third step is to upload the audio data that you want to annotate in the "upload data page". BAT works with segments, so you will have to enter a value in the segment length field. If you write -1, the whole duration of the audio file will be used as the segment length. Right now BAT accepts only wav files. 

4. Your project is ready. Create an annotator account and start annotating!

Annotation process:
--------------

1. To annotate, create an annotator user, log in, go to the "new anotation page", and select a project. You will be automatically redirected to the "annotation page".

2. The annotation has two phases: the event identification and the salience assigning pahses.

3. In the event identification you create regions containing events that are of interest to the project's task by clicking and dragging over the waveform. Assign a class to these regions using the labels under the waveform or the keyboard shortcuts. Remember that you can also add tags to these regions.

4. If your project allows overlaps, some of the created regions might overlap. To finish the annotation you need to solve these overlaps, which means assigning how salient is each of the overlapping classes: first, click on the "solve overlaps" button. You will se that new regions, click on the label of those with more than one class to assign their salience.

5. Annotation is finished! Click on either "finish annotation" or "finish annotation and load next"

Third party software:
--------------

1. From the CrowdCurio project (https://github.com/CrowdCurio/audio-annotator): extended versions of wavesurfer.js and regions.js plugins.
