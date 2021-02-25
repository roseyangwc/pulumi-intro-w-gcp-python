"""A Google Cloud Python Pulumi program"""
import pulumi
from pulumi import ResourceOptions
from pulumi_gcp import compute

# Read init script
with open('scripts/vm_startup_script.txt', 'r') as startup_script:
    data = startup_script.read()
script = data

# Read ssh key from pulumi configs
config = pulumi.Config()
sshkey = config.require_secret('sshkey')  # Read the secret: sshkey

# Create VPC network
compute_network = compute.Network("default-network")

# Create firewall rules to VPC network
compute_firewall = compute.Firewall(
    "firewall",
    network = compute_network.name,
    allows = [compute.FirewallAllowArgs(
        protocol = "tcp",
        ports = ["22", "80"]
    )]
)

# Create IP address
instance_addr = compute.Address(
    "demo-instance-address",
    region = "asia-east1"
)

# Create Instance
compute_instance = compute.Instance(
    "demo-instance",
    zone = "asia-east1-a",
    boot_disk = compute.InstanceBootDiskArgs(
        initialize_params = compute.InstanceBootDiskInitializeParamsArgs(
            image = "ubuntu-1804-bionic-v20210211"
        )
    ),
    machine_type = "e2-medium",
    network_interfaces = [compute.InstanceNetworkInterfaceArgs(
        network = compute_network.name,
        access_configs = [compute.InstanceNetworkInterfaceAccessConfigArgs(
            nat_ip = instance_addr.address
        )],
    )],
    opts = ResourceOptions(depends_on = [compute_firewall]),
    metadata_startup_script = script,
    metadata = {
        "ssh-keys": sshkey
    },
    tags = ["demo", "dev"]
)

pulumi.export("instanceName", compute_instance.name)
pulumi.export("instanceIP", instance_addr.address)
pulumi.export("sshkey", sshkey)