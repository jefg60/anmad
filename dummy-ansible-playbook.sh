#!/bin/bash
/usr/bin/perl -MPOSIX -e '$0="/opt/bin/ansible-playbook param1 param2 /srv/config/deploy.yaml"; pause' &
/usr/bin/perl -MPOSIX -e '$0="/opt/bin/ansible-playbook /srv/config/deploy2.yaml"; pause' &
