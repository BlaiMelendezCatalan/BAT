BAT - BMAT Annotation Tool
==========

Install and run the project on the local computer
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

5. Build the project.

::

    $ docker-compose -f dev.yml build
    
6. Now you can add an admin user.

::

    $ docker-compose -f dev.yml run django python manage.py createsuperuser

7. Run the tool locally or on a server.

::

    $ docker-compose -f dev.yml up



8. Open **http://localhost:8003/annotation_tool/** or **http://<your_server>:8003/annotation_tool/** in your browser. You can change the port in dev.yml.
