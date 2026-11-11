Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.hostname = "netdevops-vm"

  config.vm.network "private_network", ip: "192.168.56.10"
  config.vm.network "forwarded_port", guest: 8000, host: 8000,
                    host_ip: "0.0.0.0", auto_correct: true

  config.vm.synced_folder ".", "/vagrant", disabled: true

  config.vm.provider "virtualbox" do |vb|
    vb.name   = "netdevops-vm"
    vb.memory = 2048
    vb.cpus   = 2
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook       = "ansible/site.yml"
    ansible.inventory_path = "ansible/inventory.ini"
    ansible.limit          = "all"
  end
end
