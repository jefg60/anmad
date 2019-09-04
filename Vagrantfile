# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.provision "shell", inline: <<-SHELL
     echo 'Acquire::http { Proxy "http://192.168.1.174:3142"; }' > /etc/apt/apt.conf.d/proxy
     apt-get update
     apt-get install -y python3.7 python3.7-dev virtualenv apache2-dev bats redis
   SHELL
  config.vm.provision "shell" do |s|
     s.inline =
       "virtualenv -p python3.7 ~/venv
        ~/venv/bin/pip install configargparse mod_wsgi hotqueue redis ssh_agent_setup pyyaml flask ansible_vault pylint
        bats /vagrant/test/anmad.bats"
     s.privileged = false
  end
end
