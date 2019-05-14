#!/usr/bin/env bats
#
load test_helper

@test "test the tests" {
  [[ 1 = 0 ]]
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
  run "$program" -i samples/inventory-internal --debug --no-syslog
  [[ "$output" = *"error: the following arguments are required:"* ]]
}

@test "run without --debug" {
  run "$program" -p deploy.yaml deploy2.yaml -i samples/inventory-internal samples/inventory-internal --no-syslog --dry-run --playbook_root_dir samples
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run without --no-syslog but with --debug, using conf file" {
  run "$program" -c configtest.ini
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
  run "$printvault" --vaultfile testvault --yaml_key master_ansible_user_ssh_phrase --vault_password_file vaultpassword
  [[ "$output" == "1234567890abc321" ]]
}

@test "pylint a*.py" {
  run $pylint ./a*.py
  [[ "$status" -eq 0 ]]
}

@test "pylint $printvault" {
  run $pylint "$printvault"
  [[ "$status" -eq 0 ]]
}
