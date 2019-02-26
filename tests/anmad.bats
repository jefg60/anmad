#!/usr/bin/env bats
#
version=0.9.4
dirpoll=./anmad_dirpoll.py
printvault=./print_vault_value.py
pylint="python3 $(which pylint)"

@test "test --help option" {
  run "$dirpoll" --help
  [ "$status" -eq 0 ]
  [[ "$output" = *"usage"* ]]
}

@test "run without args, print help" {
  run "$dirpoll"
  [[ "$output" = *"error: the following arguments are required:"* ]]
}

@test "run with incorrect args, print help" {
  run "$dirpoll" -i samples/inventory-internal --debug --no-syslog
  [[ "$output" = *"error: the following arguments are required:"* ]]
}

@test "run with 1 playbook and 1 inventory" {
  run "$dirpoll" -p samples/deploy.yaml -i samples/inventory-internal --debug --no-syslog --dir_to_watch /tmp/ --dry-run --interval 1
  [[ "$output" = *"Polling for updates"* ]]
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run with 1 playbook and 2 inventories" {
  run "$dirpoll" -p samples/deploy.yaml -i samples/inventory-internal samples/inventory-internal --debug --no-syslog --dir_to_watch /tmp/ --dry-run --interval 1
  [[ "$output" = *"Polling for updates"* ]]
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run with 2 inventories and 2 playbooks" {
  run "$dirpoll" -p samples/deploy.yaml samples/deploy2.yaml -i samples/inventory-internal samples/inventory-internal --debug --no-syslog --dir_to_watch /tmp/ --dry-run --interval 1
  [[ "$output" = *"Polling for updates"* ]]
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run without --debug" {
  run "$dirpoll" -p samples/deploy.yaml samples/deploy2.yaml -i samples/inventory-internal samples/inventory-internal --no-syslog --dir_to_watch /tmp/ --dry-run --interval 1
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run without --no-syslog but with --debug, using conf file" {
  run "$dirpoll" -c configtest.ini
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "logpoll Version is $version" {
  run "$dirpoll" --version
  [ "$output" = "$version" ]
}

@test "printvault Version is $version" {
  run "$printvault" --version
  [ "$output" = "$version" ]
}

@test "able to decrypt testvault" {
  run "$printvault" --vaultfile testvault --yaml_key master_ansible_user_ssh_phrase --vault_password_file vaultpassword
  [[ "$output" == "1234567890abc321" ]]
}

@test "pylint a*.py" {
  run $pylint ./a*.py
  [ "$status" -eq 0 ]
}

@test "pylint $printvault" {
  run $pylint "$printvault"
  [ "$status" -eq 0 ]
}
