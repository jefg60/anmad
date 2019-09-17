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
  config.vm.provision "shell", path: "vagranttest.sh", privileged: false
end
