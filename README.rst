audio_annotation_tool
==========

Install and run the project on the local computer
--------------

1. Install the docker and the docker-compose. For the docker install you can use `the official documentation guide`_.

.. _`the official documentation guide`: https://docs.docker.com/engine/installation/linux/ubuntulinux/

2. Clone the **dev** branch of the repository

3. Create file with name **.env** in project root (near **dev.yml** file) with text

::

    DJANGO_SETTINGS_MODULE=config.settings.local

4. Stop the postgresql service on your computer (if it exist)

::

    $ sudo service postgresql stop

5. Build the project with command

::

    $ docker-compose -f dev.yml build

6. After build, run the server with command (you can use **-d** param for run server in background-mode)

::

    $ docker-compose -f dev.yml up

7. Now you can add admin user with command

::

    $ docker-compose -f dev.yml run django python manage.py createsuperuser

8. Open http://127.0.0.1:8000 in browser