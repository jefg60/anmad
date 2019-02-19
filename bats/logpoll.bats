#!/usr/bin/env bats
#
#This is obviously just a quick control test - if this fails the tests are not reliable!

@test "Check that 1 equals 1" {
  one=1
  [ $one -eq 1 ]
}

@test "test --help option" {
  run ./ansible_logpoll.py --help
  [ "$status" -eq 0 ]
  [[ "$output" = *"usage"* ]]
}

@test "run without args, print help" {
  run ./ansible_logpoll.py
  [[ "$output" = *"error: the following arguments are required:"* ]]
}

@test "run with incorrect args, print help" {
  run ./ansible_logpoll.py -i samples/inventory-internal --debug --no-syslog
  [[ "$output" = *"error: the following arguments are required:"* ]]
}

@test "run with 1 playbook and 1 inventory" {
  run ./ansible_logpoll.py -p samples/deploy.yaml -i samples/inventory-internal --debug --no-syslog --dir_to_watch /tmp/ --dry-run --interval 1
  [[ "$output" = *"Polling for updates"* ]]
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run with 1 playbook and 2 inventories" {
  run ./ansible_logpoll.py -p samples/deploy.yaml -i samples/inventory-internal samples/inventory-internal --debug --no-syslog --dir_to_watch /tmp/ --dry-run --interval 1
  [[ "$output" = *"Polling for updates"* ]]
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run with 2 inventories and 2 playbooks" {
  run ./ansible_logpoll.py -p samples/deploy.yaml samples/deploy2.yaml -i samples/inventory-internal samples/inventory-internal --debug --no-syslog --dir_to_watch /tmp/ --dry-run --interval 1
  [[ "$output" = *"Polling for updates"* ]]
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run without --debug" {
  run ./ansible_logpoll.py -p samples/deploy.yaml samples/deploy2.yaml -i samples/inventory-internal samples/inventory-internal --no-syslog --dir_to_watch /tmp/ --dry-run --interval 1
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run without --no-syslog but with --debug, using conf file" {
  run ./ansible_logpoll.py -c configtest.ini
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "logpoll Version is 0.9.3" {
  run ./ansible_logpoll.py --version
  [ "$output" = "0.9.3" ]
}

@test "printvault Version is 0.9.3" {
  run ./print_vault_value.py --version
  [ "$output" = "0.9.3" ]
}

@test "able to decrypt testvault" {
  run ./print_vault_value.py --vaultfile testvault --yaml_key ssh_passphrase --vault_password_file vaultpassword
  [[ "$output" == "1234567890abc321" ]]
}
