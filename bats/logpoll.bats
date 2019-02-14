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
  run ./ansible_logpoll.py -p samples/deploy.yaml -i samples/inventory-internal --debug --no-syslog --logdir /tmp/ --dry-run --interval 1
  [[ "$output" = *"Polling for updates"* ]]
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run with 1 playbook and 2 inventories" {
  run ./ansible_logpoll.py -p samples/deploy.yaml -i samples/inventory-internal samples/inventory-internal --debug --no-syslog --logdir /tmp/ --dry-run --interval 1
  [[ "$output" = *"Polling for updates"* ]]
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run with 2 inventories and 2 playbooks" {
  run ./ansible_logpoll.py -p samples/deploy.yaml samples/deploy2.yaml -i samples/inventory-internal samples/inventory-internal --debug --no-syslog --logdir /tmp/ --dry-run --interval 1
  [[ "$output" = *"Polling for updates"* ]]
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "run without --debug" {
  run ./ansible_logpoll.py -p samples/deploy.yaml samples/deploy2.yaml -i samples/inventory-internal samples/inventory-internal --no-syslog --logdir /tmp/ --dry-run --interval 1
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

# This should work on OSX 10.14
@test "run without --no-syslog but with --debug" {
  run ./ansible_logpoll.py -p samples/deploy.yaml samples/deploy2.yaml -i samples/inventory-internal samples/inventory-internal --debug --logdir /tmp/ --dry-run --interval 1 --syslogdevice /var/run/syslog
  [[ "$output" != *"error"* ]]
  [ "$status" -eq 0 ]
}

@test "Version is 0.7" {
  run ./ansible_logpoll.py --version
  [ "$output" = "0.7" ]
}
