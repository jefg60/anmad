#!/usr/bin/env bats
#
#This is obviously just a quick control test - if this fails the tests are not reliable!

@test "Check that 1 equals 1" {
    one=1
    [ $one -eq 1 ]
}

@test "run without args, print help" {
./ansible_logpoll.py
}

@test "run with incorrect args, print help" {
./ansible_logpoll.py -i i1.yml --debug --no-syslog
}

@test "run with 1 playbook and 1 inventory" {
./ansible_logpoll.py -p p1.yml -i i1.yml --debug --no-syslog --logdir /tmp/ --dry-run --interval 1
}

@test "run with 1 playbook and 2 inventories" {
./ansible_logpoll.py -p p1.yml -i i1.yml i2.yml --debug --no-syslog --logdir /tmp/ --dry-run --interval 1
}

@test "run with 2 inventories and 2 playbooks" {
./ansible_logpoll.py -p p1.yml p2.yml -i i1.yml i2.yml --debug --no-syslog --logdir /tmp/ --dry-run --interval 1
}

@test "run without --debug" {
./ansible_logpoll.py -p p1.yml p2.yml -i i1.yml i2.yml --no-syslog --logdir /tmp/ --dry-run --interval 1
}

@test "run without --no-syslog but with --debug" {
./ansible_logpoll.py -p p1.yml p2.yml -i i1.yml i2.yml --debug --logdir /tmp/ --dry-run --interval 1
}
