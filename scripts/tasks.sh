#!/bin/bash

main() {
  if [ "$#" -ne 1 ]; then
    echo No parameter given.
  fi
  $1
}

provision() {
  install_packages
  install_service
}

install_packages() {
  packages=(
    python-pip
    git
  )
  apt-get update
  apt-get install -y ${packages[@]}
  pip install virtualenv
}

install_service() {
  cp /vagrant/scripts/mym.conf /etc/init/mym.conf
  touch /var/log/mym
  chown vagrant /var/log/mym
}

setup_project() {
  cd /vagrant
  virtualenv env
  env/bin/pip install -r requirements.txt
}

main $@
