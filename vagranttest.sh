#!/bin/bash
if [ ! -d ~/venv ] ; then
    virtualenv -p python3.7 ~/venv &&\
    ~/venv/bin/pip install configargparse mod_wsgi hotqueue redis ssh_agent_setup pyyaml flask ansible_vault pylint psutil requests
    git clone https://github.com/bats-core/bats-core.git
    cd bats-core
    sudo ./install.sh /usr/local
fi
/home/vagrant/venv/bin/pylint /vagrant/*.py || exit 1
/home/vagrant/venv/bin/pylint /vagrant/anmad/*.py || exit 2
/home/vagrant/venv/bin/python -m unittest discover -s /vagrant || exit 3
/vagrant/dummy-ansible-playbook.sh
if ! screen -list | grep -q "anmaddev"; then
  screen -d -m -S anmaddev /home/vagrant/venv/bin/python /vagrant/anmad_buttons.py --configfile /vagrant/test/configtest.nodry.ini
fi
bats /vagrant/test/anmad.bats || exit 4
/home/vagrant/venv/bin/python /vagrant/test_requests.py
