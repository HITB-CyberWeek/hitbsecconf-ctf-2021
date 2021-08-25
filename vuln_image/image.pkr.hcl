packer {
  required_plugins {
    digitalocean = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/digitalocean"
    }
  }
}

variable "api_token" {
  type = string
}

source "digitalocean" "vuln_image" {
  api_token    = var.api_token
  image        = "ubuntu-20-04-x64"
  region       = "sgp1"
  size         = "s-2vcpu-4gb"
  ssh_username = "root"
}

build {
  sources = ["source.digitalocean.vuln_image"]

  provisioner "shell" {
    inline_shebang = "/bin/sh -ex"
    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive",
    ]
    inline = [
      # Wait apt-get lock
      "while ps -opid= -C apt-get > /dev/null; do sleep 1; done",

      "apt-get clean",
      "apt-get update",

      # Wait apt-get lock
      "while ps -opid= -C apt-get > /dev/null; do sleep 1; done",

      "apt-get upgrade -y -q -o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold'",

      # Install docker and docker-compose
      "apt-get install -y -q apt-transport-https ca-certificates nfs-common",
      "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -",
      "add-apt-repository \"deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\"",
      "apt-get update",
      "apt-get install -y -q docker-ce",
      "curl -L \"https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose",
      "chmod +x /usr/local/bin/docker-compose",
      
      # Install haveged, otherwise docker-compose may hang: https://stackoverflow.com/a/68172225/1494610
      "apt-get install -y -q haveged",

      # Add users for services
      "useradd -m -u 10000 -s /bin/bash fw",
      "useradd -m -u 10001 -s /bin/bash passman",
      "useradd -m -u 10002 -s /bin/bash secure-mail",
      "useradd -m -u 10003 -s /bin/bash sandbox",
      "useradd -m -u 10004 -s /bin/bash svghost",
      "useradd -m -u 10005 -s /bin/bash xar",
    ]
  }

  # Copy services
  provisioner "file" {
    source = "../services/fw/"
    destination = "/home/fw/"
  }

  provisioner "file" {
    source = "../services/passman/deploy/"
    destination = "/home/passman/"
  }

  provisioner "file" {
    source = "../services/secure-mail/"
    destination = "/home/secure-mail/"
  }

  provisioner "shell" {
    inline = [
      "cd ~sandbox",
      "mkdir sandbox_vm_image sandbox_docker_image",
    ]
  }

  provisioner "file" {
    source = "../services/sandbox/docker-compose.yaml"
    destination = "/home/sandbox/"
  }

  provisioner "file" {
    source = "../services/sandbox/Dockerfile"
    destination = "/home/sandbox/"
  }

  provisioner "file" {
    source = "../services/sandbox/.dockerignore"
    destination = "/home/sandbox/"
  }

  provisioner "file" {
    source = "../services/sandbox/src"
    destination = "/home/sandbox/"
  }

  provisioner "file" {
    source = "../services/sandbox/certificates"
    destination = "/home/sandbox/"
  }

  provisioner "file" {
    source = "../services/sandbox/keys"
    destination = "/home/sandbox/"
  }

  provisioner "file" {
    source = "../services/sandbox/sandbox_vm_image/output-sandbox"
    destination = "/home/sandbox/sandbox_vm_image/"
  }

  provisioner "file" {
    source = "../services/sandbox/sandbox_docker_image/sandbox.tar.gz"
    destination = "/home/sandbox/sandbox_docker_image/"
  }


  provisioner "file" {
    source = "../services/svghost/out"
    destination = "/home/svghost/"
  }

  provisioner "file" {
    source = "../services/svghost/docker-compose.yml"
    destination = "/home/svghost/"
  }

  provisioner "file" {
    source = "../services/svghost/Dockerfile"
    destination = "/home/svghost/"
  }

  provisioner "file" {
    source = "../services/svghost/start.sh"
    destination = "/home/svghost/"
  }

  provisioner "file" {
    source = "../services/xar/"
    destination = "/home/xar/"
  }
  
  # Build and run services for the first time
  provisioner "shell" {
    inline = [
      "cd ~fw",
      "docker-compose up --build -d",
    ]
  }

  provisioner "shell" {
    inline = [
      "cd ~passman",
      "docker-compose up --build -d",
    ]
  }

  provisioner "shell" {
    inline = [
      "cd ~sandbox",
      "apt-get -y -q install virtualbox",
      "VBoxManage import sandbox_vm_image/output-sandbox/packer-sandbox-*.ovf --vsys 0 --vmname docker.sandbox.2021.ctf.hitb.org",
      "VBoxManage hostonlyif create",
      "VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.56.1",
      "VBoxManage modifyvm docker.sandbox.2021.ctf.hitb.org --nic1 hostonly --hostonlyadapter1 vboxnet0",
      "VBoxManage startvm docker.sandbox.2021.ctf.hitb.org --type headless",
      "docker-compose up --build -d"
    ]
  }

  provisioner "shell" {
    inline = [
      "cd ~secure-mail",
      "docker-compose up --build -d",
    ]
  }

  provisioner "shell" {
    inline = [
      "cd ~svghost",
      "docker-compose up --build -d",
    ]
  }

  provisioner "shell" {
    inline = [
      "cd ~xar",
      "docker-compose up --build -d",
    ]
  }

  # Fix some internal digitalocean+cloud-init scripts to be compatible with our cloud infrastructure
  provisioner "shell" {
    script = "digital_ocean_specific_setup.sh"
  }
}
