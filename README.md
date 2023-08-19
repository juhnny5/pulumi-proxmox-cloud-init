# Pulumi + Proxmox VE + cloud-init = ❤️

Creating vms with Pulumi on Proxmox VE.

In this repository, you'll find 2 versions, the first where the vms configuration declaration is present in the `vms.yaml` file. In the second version, you can declare your vms in the `vms/` folder, adding your vms in *.yaml* files with any name you like.

The second version is more practical and easier to maintain.

[Blog post here](https://blog.jbriault.fr/pulumi-proxmox-cloudinit/).

## Configuration

### On Proxmox VE

#### Create Pulumi user

```bash
pveum role add Pulumi -privs "VM.Allocate VM.Clone VM.Config.CDROM VM.Config.CPU VM.Config.Cloudinit VM.Config.Disk VM.Config.HWType VM.Config.Memory VM.Config.Network VM.Config.Options VM.Monitor VM.Audit VM.PowerMgmt Datastore.AllocateSpace Datastore.Audit"
pveum user add pulumi@pve -password <password> -comment "Pulumi account"
pveum aclmod / -user pulumi@pve -role Pulumi
```

#### Create Template

```bash
cd /tmp
wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img
apt update -y && apt install libguestfs-tools -y
```

```bash
virt-customize -a jammy-server-cloudimg-amd64.img --install qemu-guest-agent
virt-customize -a jammy-server-cloudimg-amd64.img --run-command 'useradd jbriault'
virt-customize -a jammy-server-cloudimg-amd64.img --run-command 'mkdir -p /home/jbriault/.ssh'
virt-customize -a jammy-server-cloudimg-amd64.img --ssh-inject jbriault:file:/home/jbriault/.ssh/id_rsa.pub
virt-customize -a jammy-server-cloudimg-amd64.img --run-command 'chown -R jbriault: /home/jbriault'
```

```bash
qm create 9000 --name "ubuntu-2204-cloudinit-template" --memory 2048 --cores 2 --net0 virtio,bridge=vmbr0
qm importdisk 9000 jammy-server-cloudimg-amd64.img local-lvm
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0
qm set 9000 --boot c --bootdisk scsi0
qm set 9000 --ide2 local-lvm:cloudinit
qm set 9000 --serial0 socket --vga serial0
qm set 9000 --agent enabled=1

qm template 9000
```

### In your Pulumi project

#### Configure Proxmox endpoint

```bash
vi .env
```

#### Add new VM

```bash
vi vms.yaml
```

## Usage

```bash
pulumi stack init dev
pulumi preview
pulumi up
```
