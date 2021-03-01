# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  #config.vm.box = "bento/ubuntu-20.04"
  config.vm.box = "bento/amazonlinux-2"
  config.vm.network "forwarded_port", guest: 9999, host: 9999, id: "flaskdev"
  config.vm.provision "shell", inline: <<-SHELL
     if [ ! -d /var/log/ansible ] ; then
       yum install -y python3 python3-dev virtualenv apache2-dev python-virtualenv &&\
       mkdir -p /var/log/anmad /var/log/ansible/playbook
       chmod -R 0777 /var/log/ansible
       chmod -R 0777 /var/log/anmad
     fi
   SHELL
  config.vm.provision "shell", path: "vagranttest.sh", privileged: false
end
