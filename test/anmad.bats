#!/usr/bin/env bats
#
load test_helper

@test "test the bats tests" {
  [[ 1 = 1 ]]
}

@test "running in python3.7" {
  run python --version
  [[ "$output" == *"3.7."* ]]
}

@test "unit test of args" {
  run python /vagrant/test_args.py --configfile /vagrant/test/configtest.ini
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "unit test of logging" {
  run python /vagrant/test_logging.py --configfile /vagrant/test/configtest.ini
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
  [[ "$output" = *"anmad.logging test ok" ]]
}

@test "unit test other python modules" {
  run python -m unittest discover
  [ "$status" -eq 0 ]
}

@test "test --help option" {
  run "$program" --help
  [[ "$output" = *"usage"* ]]
}

@test "run without args, print help" {
  run "$program"
  [[ "$output" = *"error: the following arguments are required:"* ]]
}

@test "run with incorrect args, print help" {
  run "$program" -i /vagrant/samples/inventory-internal --debug --no-syslog
  [[ "$output" = *"error: the following arguments are required:"* ]]
}

@test "run without --debug" {
  run "$program" -p /vagrant/deploy.yaml /vagrant/deploy2.yaml -i /vagrant/samples/inventory-internal /vagrant/samples/inventory-internal --no-syslog --dry-run --playbook_root_dir /vagrant/samples
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run without --no-syslog but with --debug, using conf file" {
  run "$program" -c /vagrant/test/configtest.ini
  [[ "$output" != *"error"* ]]
}

@test "$program Version is $version" {
  run "$program" --version
  [[ "$output" = "$version" ]]
}

@test "printvault Version is $version" {
  run "$printvault" --version
  [[ "$output" = "$version" ]]
}

@test "able to decrypt testvault" {
  run "$printvault" --vaultfile /vagrant/test/testvault --yaml_key master_ansible_user_ssh_phrase --vault_password_file /vagrant/test/vaultpassword
  [[ "$output" == "1234567890abc321" ]]
}

@test "pylint a*.py" {
  run $pylint /vagrant/a*.py
  [[ "$status" -eq 0 ]]
}

@test "pylint anmad modules /vagrant/anmad/*.py" {
  run $pylint /vagrant/anmad/*.py
  [[ "$status" -eq 0 ]]
}

@test "pylint $printvault" {
  run $pylint "$printvault"
  [[ "$status" -eq 0 ]]
}
