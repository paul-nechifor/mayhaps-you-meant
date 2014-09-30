Vagrant.configure("2") do |config|
  config.vm.define "mym" do |machine|
    machine.vm.box = "ubuntu/trusty64"
    machine.vm.provision "shell", path: "scripts/tasks.sh", args: "provision"
    machine.vm.provider "virtualbox" do |v|
      v.memory = 1024
      v.cpus = 1
    end
  end
end
