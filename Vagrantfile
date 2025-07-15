Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  
  #config.vm.network "private_network", ip: "192.168.56.10"
  config.vm.network "public_network"

  # Forward port 8001 from VM to host
  config.vm.network "forwarded_port", guest: 8001, host: 8001

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
  end
end