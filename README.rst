audio_annotation_tool
==========

Install and run the project on the local computer
--------------

1. Install the docker and the docker-compose. For the docker install you can use `the official documentation guide`_.

.. _`the official documentation guide`: https://docs.docker.com/engine/installation/linux/ubuntulinux/

2. Clone the **dev** branch of the repository

3. Stop the postgresql service on your computer (if it exist)

::

    $ sudo service postgresql stop

4. Build the project with command

::

    $ docker-compose -f dev.yml build

5. After build, run the server with command (you can use **-d** param for run server in background-mode)

::

    $ docker-compose -f dev.yml up

6. Now you can add admin user with command

::

    $ docker-compose -f dev.yml run django python manage.py createsuperuser

7. Open http://127.0.0.1:8000 in browser