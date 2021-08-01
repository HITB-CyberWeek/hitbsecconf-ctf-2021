## "Sandbox" service building

This service is complicated enough. To build it you should:

1. Build docker image (you need `docker` to be installed)
   ```
   pushd sandbox_docker_image
   ./build_and_export_image.sh
   popd
   ```

2. Build VM image (you need VirtualBox and `packer` to be installed)
   ```
   pushd sandbox_vm_image
   ./build_and_export_image.sh
   popd
   ```
   
3. Build main docker image with python API (not necessary if you run service with docker-compose — see below)
   ```
   docker build .
   ```
   
## "Sandbox" service deploying

Bring following files and directories to the server:
  - `docker-compose.yaml`
  - `Dockerfile`
  - `.dockerignore`
  - `src/`
  - `sandbox_vm_image/output-sandbox/`
  - `sandbox_docker_image/sandbox.tar.gz`
  - `certificates/`
  - `keys/`

To run service you should

0. Install docker, docker-compose and VirtualBox (https://docs.docker.com/engine/install/ubuntu/,
https://docs.docker.com/compose/install/
and ```apt-get install virtualbox```)

2. (Remove old VM if it exist)
   ```
   VBoxManage unregistervm --delete docker.sandbox.2021.ctf.hitb.org
   ```
3. Run VM from image
   ```   
   VBoxManage import sandbox_vm_image/output-sandbox/packer-sandbox-*.ovf --vsys 0 --vmname docker.sandbox.2021.ctf.hitb.org
   VBoxManage hostonlyif create
   VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.56.1 
   VBoxManage modifyvm docker.sandbox.2021.ctf.hitb.org --nic1 hostonly --hostonlyadapter1 vboxnet0
   VBoxManage startvm docker.sandbox.2021.ctf.hitb.org --type headless
   ```

4. Run python API with database
   ```
   docker-compose up --build
   ```
