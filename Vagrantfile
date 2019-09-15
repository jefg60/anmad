# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.network "forwarded_port", guest: 9999, host: 9999, id: "flaskdev"
  config.vm.provision "shell", inline: <<-SHELL
     if [ ! -d /var/log/ansible ] ; then
       cp /vagrant/vagrant_proxy /etc/apt/apt.conf.d/proxy &&\
       apt-get update &&\
       apt-get install -y python3.7 python3.7-dev virtualenv apache2-dev redis &&\
       mkdir -p /var/log/anmad /var/log/ansible/playbook
       chmod -R 0777 /var/log/ansible
       chmod -R 0777 /var/log/anmad
     fi
   SHELL
  config.vm.provision "shell" do |s|
     s.inline =
       "if [ ! -d ~/venv ] ; then
          virtualenv -p python3.7 ~/venv &&\
          ~/venv/bin/pip install configargparse mod_wsgi hotqueue redis ssh_agent_setup pyyaml flask ansible_vault pylint psutil requests
          git clone https://github.com/bats-core/bats-core.git
          cd bats-core
          sudo ./install.sh /usr/local
        fi
        /home/vagrant/venv/bin/pylint /vagrant/*.py || exit 1
        /home/vagrant/venv/bin/pylint /vagrant/anmad/*.py || exit 2
        /home/vagrant/venv/bin/python -m unittest discover -s /vagrant || exit 3
        bash /vagrant/dummy-ansible-playbook.sh
        #/home/vagrant/venv/bin/python /vagrant/anmad_buttons.py --configfile /vagrant/test/configtest.nodry.ini &> /var/log/anmad/anmad_buttons.log &
        bats /vagrant/test/anmad.bats || exit 4
        /home/vagrant/venv/bin/python /vagrant/test_requests.py"
     s.privileged = false
  end
end
