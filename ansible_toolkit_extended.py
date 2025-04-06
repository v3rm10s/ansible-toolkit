import os
import questionary
from prompt_toolkit.styles import Style

# UI styling
custom_style = Style.from_dict({
    "qmark": "#00d787 bold",
    "question": "bold",
    "answer": "#00d787 bold",
    "pointer": "#00d787 bold",
    "highlighted": "#00d787 bold",
    "selected": "#00d787 bold",
})

# Modular service templates
SERVICE_TEMPLATES = {
    "Azure": {
        "Connectivity": {
            "Azure VM ping + RDP port test": [
                "- name: Azure VM ping check",
                "  win_ping:",
                "- name: Test RDP port (3389)",
                "  win_command: Test-NetConnection -ComputerName localhost -Port 3389"
            ],
            "Azure VM extension status": [
                "- name: Check Azure VM extension",
                "  win_shell: Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like '*Azure*'}",
                "  register: extension_status",
                "- name: Output extension status",
                "  debug:",
                "    var: extension_status.stdout_lines"
            ]
        },
        "Security": {
            "NSG rule test": [
                "- name: Validate NSG rules",
                "  uri:",
                "    url: http://localhost:80",
                "    method: GET",
                "  register: nsg_check",
                "- name: Output NSG rule result",
                "  debug:",
                "    var: nsg_check"
            ],
            "Disk encryption status": [
                "- name: Check BitLocker status",
                "  win_command: manage-bde -status",
                "  register: encryption_status",
                "- name: Output encryption info",
                "  debug:",
                "    var: encryption_status.stdout_lines"
            ]
        }
    },
    "AWS": {
        "Connectivity": {
            "EC2 ping + SSH port check": [
                "- name: Ping EC2 instance",
                "  ping:",
                "- name: Test SSH port",
                "  shell: nc -zv localhost 22",
                "  register: ssh_check",
                "- name: Output SSH check",
                "  debug:",
                "    var: ssh_check.stdout_lines"
            ]
        },
        "Security": {
            "Check SSM agent": [
                "- name: Check SSM agent",
                "  shell: systemctl status amazon-ssm-agent",
                "  register: ssm_status",
                "- name: Output SSM agent result",
                "  debug:",
                "    var: ssm_status.stdout_lines"
            ],
            "IAM user policy inspection": [
                "- name: Get IAM policy info",
                "  aws_iam_policy_info:",
                "    policy_arn: arn:aws:iam::aws:policy/AdministratorAccess",
                "  register: policy_info",
                "- name: Output policy info",
                "  debug:",
                "    var: policy_info"
            ]
        }
    },
    "On-Prem": {
        "Directory": {
            "Check AD DS service": [
                "- name: Ensure AD DS is running",
                "  win_service:",
                "    name: NTDS",
                "  register: ad_service",
                "- name: Output AD DS status",
                "  debug:",
                "    var: ad_service"
            ]
        },
        "Maintenance": {
            "Check pending Windows updates": [
                "- name: Check for updates",
                "  win_updates:",
                "    state: searched",
                "  register: updates",
                "- name: Output update results",
                "  debug:",
                "    var: updates"
            ]
        }
    },
    "Hybrid": {
        "Connectivity": {
            "Azure → On-Prem DNS check": [
                "- name: Test On-Prem DNS",
                "  win_command: nslookup onprem.local",
                "  register: dns_test",
                "- name: Output DNS test",
                "  debug:",
                "    var: dns_test.stdout_lines"
            ]
        },
        "Directory": {
            "AD Connect last sync": [
                "- name: Get AD Connect Sync Status",
                "  win_shell: Get-ADSyncScheduler | Format-List",
                "  register: sync_status",
                "- name: Show sync result",
                "  debug:",
                "    var: sync_status.stdout_lines"
            ]
        }
    }
}

# Save playbook
def save_playbook(content, task_name, filename, directory):
    save_path = os.path.join(directory, filename)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"- name: {task_name}\n")
        f.write("  hosts: all\n")
        f.write("  gather_facts: no\n")
        f.write("  tasks:\n")
        for line in content:
            f.write("    " + line + "\n")
    return save_path

# Tool 4: Playbook Generator
def generate_playbook():
    env = questionary.select("🌐 Choose environment:", choices=list(SERVICE_TEMPLATES.keys()), style=custom_style).ask()
    mode = questionary.select("🧭 View mode?", choices=["Grouped", "Flat"], style=custom_style).ask()

    if mode == "Grouped":
        category = questionary.select("📂 Choose service group:", choices=list(SERVICE_TEMPLATES[env].keys()), style=custom_style).ask()
        task = questionary.select("🔧 Choose check:", choices=list(SERVICE_TEMPLATES[env][category].keys()), style=custom_style).ask()
        selected_task = SERVICE_TEMPLATES[env][category][task]
        task_name = task
    else:
        flat_tasks = {}
        for group in SERVICE_TEMPLATES[env].values():
            flat_tasks.update(group)
        task = questionary.select("🔧 Choose check:", choices=list(flat_tasks.keys()), style=custom_style).ask()
        selected_task = flat_tasks[task]
        task_name = task

    filename = questionary.text("💾 File name (e.g. check_vm.yml):").ask()
    if not filename.endswith(".yml"):
        filename += ".yml"
    directory = questionary.path("📂 Directory to save:", only_directories=True).ask()
    path = save_playbook(selected_task, task_name, filename, directory)
    print(f"✅ Playbook saved at: {path}")

# Tool 5: Dynamic Inventory Generator
def generate_dynamic_inventory():
    choice = questionary.select(
        "🗂 Choose inventory type:",
        choices=["AWS EC2 Plugin", "Azure RM Plugin", "Static Hosts File"],
        style=custom_style
    ).ask()

    filename = questionary.text("💾 File name for inventory config (e.g. inventory_aws.yml):").ask()
    if not filename.endswith(".yml"):
        filename += ".yml"
    directory = questionary.path("📂 Directory to save:", only_directories=True).ask()
    path = os.path.join(directory, filename)

    content = ""

    if "AWS" in choice:
        region = questionary.text("🌎 AWS region (e.g. us-east-1):").ask()
        tag = questionary.text("🏷️ Filter by tag (e.g. Environment=prod):").ask()
        key, value = tag.split("=")
        content = f"""plugin: aws_ec2
regions: ["{region}"]
filters:
  tag:{key}: {value}
hostnames:
  - tag:Name
keyed_groups:
  - prefix: tag
    key: Environment
"""

    elif "Azure" in choice:
        resource_group = questionary.text("📘 Azure resource group name:").ask()
        content = f"""plugin: azure_rm
include_vm_resource_groups:
  - {resource_group}
auth_source: auto
plain_host_names: yes
"""

    elif "Static" in choice:
        ip = questionary.text("🔌 Enter target IP or hostname:").ask()
        content = f"""[all]
{ip}
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Inventory config saved at: {path}")
