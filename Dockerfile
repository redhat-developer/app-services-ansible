FROM quay.io/app-sre/mk-ci-tools:latest

USER root

COPY . /usr/app-services-ansible

RUN mkdir -p /usr/app-services-ansible/results
RUN chmod 755 -R /usr/app-services-ansible

ENV PATH ~/bin:$PATH

WORKDIR /usr/app-services-ansible/tests
