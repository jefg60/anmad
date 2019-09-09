perl -MPOSIX -e '$0="/opt/bin/ansible-playbook param1 param2 /srv/config/deploy.yaml"; pause' &
perl -MPOSIX -e '$0="/opt/bin/ansible-playbook /srv/config/deploy2.yaml"; pause' &
