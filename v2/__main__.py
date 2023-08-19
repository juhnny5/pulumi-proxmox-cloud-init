import os
import yaml
import pulumi
import pulumi_proxmoxve as proxmox

folder_path = "vms/"

def load_yaml_files_from_folder(folder_path):
    yaml_files = [file for file in os.listdir(folder_path) if file.endswith(".yaml")]
    loaded_data = []

    for yaml_file in yaml_files:
        file_path = os.path.join(folder_path, yaml_file)
        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
            loaded_data.append(yaml_data)

    return loaded_data

parsed_data = load_yaml_files_from_folder(folder_path) 

for vm in parsed_data:
    disks = []
    nets = []
    ip_configs = []
    ssh_keys = []

    for v in vm:
        for disk_entry in v['disks']:
            for d in disk_entry:
                disks.append(
                    proxmox.vm.VirtualMachineDiskArgs(
                        interface=disk_entry[d]['interface'],
                        datastore_id=disk_entry[d]['datastore_id'],
                        size=disk_entry[d]['size'],
                        file_format=disk_entry[d]['file_format'],
                        cache=disk_entry[d]['cache']
                    )
                )

        for ip_config_entry in v['cloud_init']['ip_configs']:
            ipv4 = ip_config_entry.get('ipv4')
            ipv6 = ip_config_entry.get('ipv6')

            if ipv4:
                ip_configs.append(
                    proxmox.vm.VirtualMachineInitializationIpConfigArgs(
                        ipv4=proxmox.vm.VirtualMachineInitializationIpConfigIpv4Args(
                            address=ipv4.get('address', ''),
                            gateway=ipv4.get('gateway', '')
                        )
                    )
                )

            if ipv6:
                ip_configs.append(
                    proxmox.vm.VirtualMachineInitializationIpConfigArgs(
                        ipv6=proxmox.vm.VirtualMachineInitializationIpConfigIpv6Args(
                            address=ipv6.get('address', ''),
                            gateway=ipv6.get('gateway', '')
                        )
                    )
                )

        for ssk_keys_entry in v['cloud_init']['user_account']['keys']:
            ssh_keys.append(ssk_keys_entry)

        for net_entry in v['network_devices']:
            for n in net_entry:
                nets.append(
                    proxmox.vm.VirtualMachineNetworkDeviceArgs(
                        bridge=net_entry[n]['bridge'],
                        model=net_entry[n]['model']
                    )
                )

        virtual_machine = proxmox.vm.VirtualMachine(
            vm_id=v['vm_id'],
            resource_name=v['resource_name'],
            node_name=v['node_name'],
            agent=proxmox.vm.VirtualMachineAgentArgs(
                enabled=v['agent']['enabled'],
                trim=v['agent']['trim'],
                type=v['agent']['type']
            ),
            bios=v['bios'],
            cpu=proxmox.vm.VirtualMachineCpuArgs(
                cores=v['cpu']['cores'],
                sockets=v['cpu']['sockets']
            ),
            clone=proxmox.vm.VirtualMachineCloneArgs(
                node_name=v['clone']['node_name'],
                vm_id=v['clone']['vm_id'],
                full=v['clone']['full'],
            ),
            disks=disks,
            memory=proxmox.vm.VirtualMachineMemoryArgs(
                dedicated=v['memory']['dedicated']
            ),
            name=v['name'],
            network_devices=nets,
            initialization=proxmox.vm.VirtualMachineInitializationArgs(
                type=v['cloud_init']['type'],
                datastore_id=v['cloud_init']['datastore_id'],
                dns=proxmox.vm.VirtualMachineInitializationDnsArgs(
                    domain=v['cloud_init']['dns']['domain'],
                    server=v['cloud_init']['dns']['server']
                ),
                ip_configs=ip_configs,
                user_account=proxmox.vm.VirtualMachineInitializationUserAccountArgs(
                    username=v['cloud_init']['user_account']['username'],
                    password=v['cloud_init']['user_account']['password'],
                    keys=ssh_keys
                ),
            ),
            on_boot=v['on_boot']
        )
        
        pulumi.export(v['name'], virtual_machine.id)
