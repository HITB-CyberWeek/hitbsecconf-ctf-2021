source "virtualbox-iso" "sandbox" {
  guest_os_type = "Debian_64"
  iso_url = "debian-10.10.0-amd64-netinst.iso"
  iso_checksum = "md5:c7d0e562e589e853b5d00563b4311720"

  memory = 1024

  http_directory = "http"
  boot_command = [
    "<esc><wait>",
    "install <wait>",
    " preseed/url=http://{{ .HTTPIP }}:{{ .HTTPPort }}/preseed.cfg <wait>",
    "debian-installer=en_US.UTF-8 <wait>",
    "auto <wait>",
    "locale=en_US.UTF-8 <wait>",
    "kbd-chooser/method=us <wait>",
    "keyboard-configuration/xkb-keymap=us <wait>",
    "netcfg/get_hostname=docker <wait>",
    "netcfg/get_domain=sandbox.2021.ctf.hitb.org <wait>",
    "<enter><wait>"
  ]
  ssh_username = "packer"
  ssh_password = "packer@docker.sandbox.2021.ctf.hitb.org"

  shutdown_command = "echo 'packer@docker.sandbox.2021.ctf.hitb.org' | sudo -S shutdown -P now"

  export_opts = [
    "--manifest",
    "--vsys", "0",
    "--description", "Sandbox VM with docker daemon",
    "--version", "1.0.0"
  ]
}

build {
  sources = ["sources.virtualbox-iso.sandbox"]

  provisioner "shell" {
    inline = [
      "mkdir ~/files"
    ]
  }

  provisioner "file" {
    source = "files/"
    destination = "~/files/"
  }

  provisioner "file" {
    source = "../keys/id_rsa.pub"
    destination = "~/id_rsa.pub"
  }

  provisioner "shell" {
    inline = [
      "sudo mkdir -p /etc/docker/ssl",

      "sudo useradd -m -s /bin/bash sandbox",
      "sudo mkdir /home/sandbox/.ssh/",
      "sudo cp ~/id_rsa.pub /home/sandbox/.ssh/authorized_keys",
      "sudo chown -R sandbox:sandbox /home/sandbox/.ssh",

      "sudo cp ~/files/daemon.json /etc/docker/daemon.json",
      "sudo mkdir /etc/systemd/system/docker.service.d/",
      "sudo cp ~/files/override.conf /etc/systemd/system/docker.service.d/override.conf",

      "sudo cp ~/files/interfaces.txt /etc/network/interfaces",
    ]
  }
}
