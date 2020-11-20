#!/usr/bin/env bats
#
load test_helper

@test "test the bats tests" {
  [[ 1 = 1 ]]
}

@test "running in python3.8" {
  run "$python" --version
  [[ "$output" == *"3.8."* ]]
}

@test "unit test of args" {
  run "$python" /vagrant/test/test_args.py --configfile /vagrant/test/configtest.ini
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "unit test of logging" {
  run "$python" /vagrant/test/test_logging.py --configfile /vagrant/test/configtest.ini
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
  [[ "$output" = *"anmad.logging test ok"* ]]
}

@test "test --help option" {
  run "$python" -m anmad.interface --help
  [[ "$output" = *"usage"* ]]
}

@test "run without --debug using commandline args" {
  run "$python" -m anmad.interface -p /vagrant/deploy.yaml /vagrant/deploy2.yaml -i /vagrant/samples/inventory-internal /vagrant/samples/inventory-internal --no-syslog --dry-run --playbook_root_dir /vagrant/samples
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run without --no-syslog but with --debug, using conf file" {
  run "$python" -m anmad.interface -c /vagrant/test/configtest.ini
  [[ "$output" != *"error"* ]]
}

@test "Version is $version" {
  run "$python" -m anmad.interface --version
  [[ "$output" = *"$version" ]]
}

@test "printvault Version is $version" {
  run "$python" "$printvault" --version
  [[ "$output" = "$version" ]]
}

@test "able to decrypt testvault" {
  run "$python" "$printvault" --vaultfile /vagrant/test/testvault --yaml_key master_ansible_user_ssh_phrase --vault_password_file /vagrant/test/vaultpassword
  [[ "$output" == "1234567890abc321" ]]
}

@test "anmad_buttons control page has correct version $version" {
    curl http://localhost:9999/ | grep "$version"
}

@test "anmad_buttons control page has a deploy2.yaml button" {
    curl http://localhost:9999/ | grep 'deploy2.yaml'
}

@test "pip metadata is correct including version $version" {
  run /home/vagrant/venv/bin/pip show anmad
  [[ "$output" = *"Version: $version"* ]]
  [[ "$output" = *"Summary: Creates a simple api and a browser interface for running ansible playbooks."* ]]
  [[ "$output" = *"Home-page: https://github.com/jefg60/anmad"* ]]
  [[ "$output" = *"Author: Jeff Hibberd"* ]]
  [[ "$output" = *"Author-email: jeff@jeffhibberd.com"* ]]
  [[ "$output" = *"License: GPLv3"* ]]
}
