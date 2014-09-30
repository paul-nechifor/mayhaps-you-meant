#!/bin/bash

main() {
  if [ "$#" -ne 1 ]; then
    echo No parameter given.
  fi
  $1
}

start() {
  vagrant up --no-provision
  vagrant provision
  setup_project
  start_bot
}

setup_project() {
  vagrant ssh -- -t '/vagrant/scripts/tasks.sh setup_project'
}

start_bot() {
  vagrant ssh -- -t 'sudo service mym start'
}

stop() {
  stop_bot
  vagrant halt
}

stop_bot() {
  vagrant ssh -- -t 'sudo service mym stop'
}

logs() {
  vagrant ssh -- -t 'tail -f /var/log/mym'
}

main $@
