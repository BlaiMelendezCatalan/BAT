FROM bitnami/minideb:jessie

RUN install_packages python gcc python-dev libblas-dev liblapack-dev libatlas-base-dev gfortran g++ libpq-dev libffi6 libffi-dev wget ca-certificates
RUN wget https://bootstrap.pypa.io/get-pip.py --secure-protocol=auto
RUN python get-pip.py

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
RUN pip install -r /requirements/local.txt

COPY ./compose/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./compose/django/start-dev.sh /start-dev.sh
RUN sed -i 's/\r//' /start-dev.sh
RUN chmod +x /start-dev.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
