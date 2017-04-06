BAT - BMAT Annotation Tool
==========

Description:
--------------

BAT is an open-source, web-based tool for the manual annotation of events in audio recordings developed at `BMAT (Barcelona Music and Audio Techonologies)`_.

.. _`BMAT (Barcelona Music and Audio Techonologies)`: https://www.bmat.com/

(1) It provides an easy way to annotate the salience of simultaneous sound sources.
(2) It allows to define multiple ontologies to adapt to multiple tasks.
(3) It offers the possibility to cross-annotate audio data. 
(4) It is easy to install and deploy on servers.

Install and run BAT locally or on a server:
--------------

1. Install docker and docker-compose. For the details on docker installation you can use `the official documentation guide`_.

.. _`the official documentation guide`: https://docs.docker.com/engine/installation/linux/ubuntulinux/

2. Clone the **master** branch of this repository.

3. Create file named **.env** in the project root (near the **dev.yml** file) with the following text:

::

    DJANGO_SETTINGS_MODULE=config.settings.local

4. Stop the postgresql service on your computer (if it exist).

::

    $ sudo service postgresql stop

5. Build BAT.

::

    $ docker-compose -f dev.yml build
    
6. Now you can add an admin user.

::

    $ docker-compose -f dev.yml run django python manage.py createsuperuser

7. Run BAT locally or on a server.

::

    $ docker-compose -f dev.yml up



8. Open **http://localhost:8003/annotation_tool/** or **http://<your_server>:8003/annotation_tool/** in your browser. You can change the port in dev.yml.

First steps with BAT:
--------------

1. As the admin you can create projects. Porjects are usually named after the type of events that we want to annotate (instrument sounds, chords, everyday life sounds, etc.). To create one, go to the projects page and click "Add Project". Name it and choose whether or not events overlap for your particular annotation task.

2. Once the project is created you need to create the ontology, i.e., the classes, that you are going to use for the annotation. To do this, go to the classes page.

3. The third step is to upload the audio data that you want to annotate. BAT works with segments, so you will have to enter a value in the segment length field. If you write -1, the whole duration of the audio file will be used as the segment length. Right now BAT accepts only wav files. 

4. Your project is ready. Create an annotator account and start annotating!

Annotation process:
--------------

1. 
