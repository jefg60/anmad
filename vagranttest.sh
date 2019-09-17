#!/bin/bash
if [ ! -d ~/venv ] ; then
    virtualenv -p python3.7 ~/venv &&\
    ~/venv/bin/pip install configargparse mod_wsgi hotqueue redis ssh_agent_setup pyyaml flask ansible_vault pylint psutil requests
    git clone https://github.com/bats-core/bats-core.git
    cd bats-core
    sudo ./install.sh /usr/local
    /usr/bin/screen -d -m -S anmaddev /home/vagrant/venv/bin/python /vagrant/anmad_buttons.py --configfile /vagrant/test/configtest.nodry.ini
fi

/vagrant/dummy-ansible-playbook.sh &&\
/home/vagrant/venv/bin/pylint /vagrant/*.py &&\
/home/vagrant/venv/bin/pylint /vagrant/anmad/*.py &&\
/home/vagrant/venv/bin/python -m unittest discover -s /vagrant &&\
bats /vagrant/test/anmad.bats &&\
/home/vagrant/venv/bin/python /vagrant/test_requests.py 
