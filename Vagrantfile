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
     cp /vagrant/vagrant_proxy /etc/apt/apt.conf.d/proxy
     apt-get update
     apt-get install -y python3.7 python3.7-dev virtualenv apache2-dev bats redis
     mkdir /var/log/ansible
     ln -s /vagrant/ansible.log /var/log/ansible/deploy.yaml.log
     ln -s /vagrant/ansible.log /var/log/ansible/deploy2.yaml.log
   SHELL
  config.vm.provision "shell" do |s|
     s.inline =
       "virtualenv -p python3.7 ~/venv
        ~/venv/bin/pip install configargparse mod_wsgi hotqueue redis ssh_agent_setup pyyaml flask ansible_vault pylint psutil
        bash /vagrant/dummy-ansible-playbook.sh
        ~/venv/bin/python /vagrant/anmad_buttons.py --configfile /vagrant/test/configtest.nodry.ini &
        bats /vagrant/test/anmad.bats"
     s.privileged = false
  end
end
