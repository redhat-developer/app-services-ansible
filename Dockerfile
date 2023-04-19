FROM quay.io/mk-ci-cd/mas-ci-tools:latest

USER root

COPY . /usr/app-services-ansible

RUN chmod 777 -R /usr/app-services-ansible

ENV PATH ~/bin:$PATH

USER build

WORKDIR /usr/app-services-ansible
