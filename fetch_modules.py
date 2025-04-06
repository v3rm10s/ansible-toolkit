#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin

# ✅ Target Collection Index Pages
URLS = {
    "ansible.windows": "https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html#plugins-in-ansible-windows",
    "community.windows": "https://docs.ansible.com/ansible/latest/collections/community/windows/index.html#plugins-in-community-windows",
    "chocolatey.chocolatey": "https://docs.ansible.com/ansible/latest/collections/chocolatey/chocolatey/index.html#plugins-in-chocolatey-chocolatey",
    "microsoft.ad": "https://docs.ansible.com/ansible/latest/collections/microsoft/ad/index.html#plugins-in-microsoft-ad",
    "amazon.aws": "https://docs.ansible.com/ansible/latest/collections/amazon/aws/index.html#plugins-in-amazon-aws#plugins-in-amazon-aws",
    "ansible.builtin": "https://docs.ansible.com/ansible/latest/collections/ansible/builtin/index.html#plugins-in-ansible-builtin#plugins-in-ansible-builtin",
    "ansible.netcommon": "https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/index.html#plugins-in-ansible-netcommon#plugins-in-ansible-netcommon",
    "ansible.posix": "https://docs.ansible.com/ansible/latest/collections/ansible/posix/index.html#plugins-in-ansible-posix#plugins-in-ansible-posix",
    "ansible.utils": "https://docs.ansible.com/ansible/latest/collections/ansible/utils/index.html#plugins-in-ansible-utils#plugins-in-ansible-utils",
    "ansible.windows": "https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html#plugins-in-ansible-windows#plugins-in-ansible-windows",
    "arista.eos": "https://docs.ansible.com/ansible/latest/collections/arista/eos/index.html#plugins-in-arista-eos#plugins-in-arista-eos",
    "awx.awx": "https://docs.ansible.com/ansible/latest/collections/awx/awx/index.html#plugins-in-awx-awx#plugins-in-awx-awx",
    "azure.azcollection": "https://docs.ansible.com/ansible/latest/collections/azure/azcollection/index.html#plugins-in-azure-azcollection#plugins-in-azure-azcollection",
    "check_point.mgmt": "https://docs.ansible.com/ansible/latest/collections/check_point/mgmt/index.html#plugins-in-check-point-mgmt#plugins-in-check_point-mgmt",
    "chocolatey.chocolatey": "https://docs.ansible.com/ansible/latest/collections/chocolatey/chocolatey/index.html#plugins-in-chocolatey-chocolatey#plugins-in-chocolatey-chocolatey",
    "cisco.aci": "https://docs.ansible.com/ansible/latest/collections/cisco/aci/index.html#plugins-in-cisco-aci#plugins-in-cisco-aci",
    "cisco.asa": "https://docs.ansible.com/ansible/latest/collections/cisco/asa/index.html#plugins-in-cisco-asa#plugins-in-cisco-asa",
    "cisco.dnac": "https://docs.ansible.com/ansible/latest/collections/cisco/dnac/index.html#plugins-in-cisco-dnac#plugins-in-cisco-dnac",
    "cisco.intersight": "https://docs.ansible.com/ansible/latest/collections/cisco/intersight/index.html#plugins-in-cisco-intersight#plugins-in-cisco-intersight",
    "cisco.ios": "https://docs.ansible.com/ansible/latest/collections/cisco/ios/index.html#plugins-in-cisco-ios#plugins-in-cisco-ios",
    "cisco.iosxr": "https://docs.ansible.com/ansible/latest/collections/cisco/iosxr/index.html#plugins-in-cisco-iosxr#plugins-in-cisco-iosxr",
    "cisco.ise": "https://docs.ansible.com/ansible/latest/collections/cisco/ise/index.html#plugins-in-cisco-ise#plugins-in-cisco-ise",
    "cisco.meraki": "https://docs.ansible.com/ansible/latest/collections/cisco/meraki/index.html#plugins-in-cisco-meraki#plugins-in-cisco-meraki",
    "cisco.mso": "https://docs.ansible.com/ansible/latest/collections/cisco/mso/index.html#plugins-in-cisco-mso#plugins-in-cisco-mso",
    "cisco.nxos": "https://docs.ansible.com/ansible/latest/collections/cisco/nxos/index.html#plugins-in-cisco-nxos#plugins-in-cisco-nxos",
    "cisco.ucs": "https://docs.ansible.com/ansible/latest/collections/cisco/ucs/index.html#plugins-in-cisco-ucs#plugins-in-cisco-ucs",
    "cloud.common": "https://docs.ansible.com/ansible/latest/collections/cloud/common/index.html#plugins-in-cloud-common#plugins-in-cloud-common",
    "cloudscale_ch.cloud": "https://docs.ansible.com/ansible/latest/collections/cloudscale_ch/cloud/index.html#plugins-in-cloudscale-ch-cloud#plugins-in-cloudscale_ch-cloud",
    "community.aws": "https://docs.ansible.com/ansible/latest/collections/community/aws/index.html#plugins-in-community-aws#plugins-in-community-aws",
    "community.ciscosmb": "https://docs.ansible.com/ansible/latest/collections/community/ciscosmb/index.html#plugins-in-community-ciscosmb#plugins-in-community-ciscosmb",
    "community.crypto": "https://docs.ansible.com/ansible/latest/collections/community/crypto/index.html#plugins-in-community-crypto#plugins-in-community-crypto",
    "community.digitalocean": "https://docs.ansible.com/ansible/latest/collections/community/digitalocean/index.html#plugins-in-community-digitalocean#plugins-in-community-digitalocean",
    "community.dns": "https://docs.ansible.com/ansible/latest/collections/community/dns/index.html#plugins-in-community-dns#plugins-in-community-dns",
    "community.docker": "https://docs.ansible.com/ansible/latest/collections/community/docker/index.html#plugins-in-community-docker#plugins-in-community-docker",
    "community.general": "https://docs.ansible.com/ansible/latest/collections/community/general/index.html#plugins-in-community-general#plugins-in-community-general",
    "community.grafana": "https://docs.ansible.com/ansible/latest/collections/community/grafana/index.html#plugins-in-community-grafana#plugins-in-community-grafana",
    "community.hashi_vault": "https://docs.ansible.com/ansible/latest/collections/community/hashi_vault/index.html#plugins-in-community-hashi-vault#plugins-in-community-hashi_vault",
    "community.hrobot": "https://docs.ansible.com/ansible/latest/collections/community/hrobot/index.html#plugins-in-community-hrobot#plugins-in-community-hrobot",
    "community.library_inventory_filtering_v1": "https://docs.ansible.com/ansible/latest/collections/community/library_inventory_filtering_v1/index.html#plugins-in-community-library-inventory-filtering-v1#plugins-in-community-library_inventory_filtering_v1",
    "community.libvirt": "https://docs.ansible.com/ansible/latest/collections/community/libvirt/index.html#plugins-in-community-libvirt#plugins-in-community-libvirt",
    "community.mongodb": "https://docs.ansible.com/ansible/latest/collections/community/mongodb/index.html#plugins-in-community-mongodb#plugins-in-community-mongodb",
    "community.mysql": "https://docs.ansible.com/ansible/latest/collections/community/mysql/index.html#plugins-in-community-mysql#plugins-in-community-mysql",
    "community.network": "https://docs.ansible.com/ansible/latest/collections/community/network/index.html#plugins-in-community-network#plugins-in-community-network",
    "community.okd": "https://docs.ansible.com/ansible/latest/collections/community/okd/index.html#plugins-in-community-okd#plugins-in-community-okd",
    "community.postgresql": "https://docs.ansible.com/ansible/latest/collections/community/postgresql/index.html#plugins-in-community-postgresql#plugins-in-community-postgresql",
    "community.proxysql": "https://docs.ansible.com/ansible/latest/collections/community/proxysql/index.html#plugins-in-community-proxysql#plugins-in-community-proxysql",
    "community.rabbitmq": "https://docs.ansible.com/ansible/latest/collections/community/rabbitmq/index.html#plugins-in-community-rabbitmq#plugins-in-community-rabbitmq",
    "community.routeros": "https://docs.ansible.com/ansible/latest/collections/community/routeros/index.html#plugins-in-community-routeros#plugins-in-community-routeros",
    "community.sap_libs": "https://docs.ansible.com/ansible/latest/collections/community/sap_libs/index.html#plugins-in-community-sap-libs#plugins-in-community-sap_libs",
    "community.sops": "https://docs.ansible.com/ansible/latest/collections/community/sops/index.html#plugins-in-community-sops#plugins-in-community-sops",
    "community.vmware": "https://docs.ansible.com/ansible/latest/collections/community/vmware/index.html#plugins-in-community-vmware#plugins-in-community-vmware",
    "community.windows": "https://docs.ansible.com/ansible/latest/collections/community/windows/index.html#plugins-in-community-windows#plugins-in-community-windows",
    "community.zabbix": "https://docs.ansible.com/ansible/latest/collections/community/zabbix/index.html#plugins-in-community-zabbix#plugins-in-community-zabbix",
    "containers.podman": "https://docs.ansible.com/ansible/latest/collections/containers/podman/index.html#plugins-in-containers-podman#plugins-in-containers-podman",
    "cyberark.conjur": "https://docs.ansible.com/ansible/latest/collections/cyberark/conjur/index.html#plugins-in-cyberark-conjur#plugins-in-cyberark-conjur",
    "cyberark.pas": "https://docs.ansible.com/ansible/latest/collections/cyberark/pas/index.html#plugins-in-cyberark-pas#plugins-in-cyberark-pas",
    "dellemc.enterprise_sonic": "https://docs.ansible.com/ansible/latest/collections/dellemc/enterprise_sonic/index.html#plugins-in-dellemc-enterprise-sonic#plugins-in-dellemc-enterprise_sonic",
    "dellemc.openmanage": "https://docs.ansible.com/ansible/latest/collections/dellemc/openmanage/index.html#plugins-in-dellemc-openmanage#plugins-in-dellemc-openmanage",
    "dellemc.powerflex": "https://docs.ansible.com/ansible/latest/collections/dellemc/powerflex/index.html#plugins-in-dellemc-powerflex#plugins-in-dellemc-powerflex",
    "dellemc.unity": "https://docs.ansible.com/ansible/latest/collections/dellemc/unity/index.html#plugins-in-dellemc-unity#plugins-in-dellemc-unity",
    "f5networks.f5_modules": "https://docs.ansible.com/ansible/latest/collections/f5networks/f5_modules/index.html#plugins-in-f5networks-f5-modules#plugins-in-f5networks-f5_modules",
    "fortinet.fortimanager": "https://docs.ansible.com/ansible/latest/collections/fortinet/fortimanager/index.html#plugins-in-fortinet-fortimanager#plugins-in-fortinet-fortimanager",
    "fortinet.fortios": "https://docs.ansible.com/ansible/latest/collections/fortinet/fortios/index.html#plugins-in-fortinet-fortios#plugins-in-fortinet-fortios",
    "google.cloud": "https://docs.ansible.com/ansible/latest/collections/google/cloud/index.html#plugins-in-google-cloud#plugins-in-google-cloud",
    "grafana.grafana": "https://docs.ansible.com/ansible/latest/collections/grafana/grafana/index.html#plugins-in-grafana-grafana#plugins-in-grafana-grafana",
    "hetzner.hcloud": "https://docs.ansible.com/ansible/latest/collections/hetzner/hcloud/index.html#plugins-in-hetzner-hcloud#plugins-in-hetzner-hcloud",
    "ibm.qradar": "https://docs.ansible.com/ansible/latest/collections/ibm/qradar/index.html#plugins-in-ibm-qradar#plugins-in-ibm-qradar",
    "ibm.spectrum_virtualize": "https://docs.ansible.com/ansible/latest/collections/ibm/spectrum_virtualize/index.html#plugins-in-ibm-spectrum-virtualize#plugins-in-ibm-spectrum_virtualize",
    "ibm.storage_virtualize": "https://docs.ansible.com/ansible/latest/collections/ibm/storage_virtualize/index.html#plugins-in-ibm-storage-virtualize#plugins-in-ibm-storage_virtualize",
    "ieisystem.inmanage": "https://docs.ansible.com/ansible/latest/collections/ieisystem/inmanage/index.html#plugins-in-ieisystem-inmanage#plugins-in-ieisystem-inmanage",
    "infinidat.infinibox": "https://docs.ansible.com/ansible/latest/collections/infinidat/infinibox/index.html#plugins-in-infinidat-infinibox#plugins-in-infinidat-infinibox",
    "infoblox.nios_modules": "https://docs.ansible.com/ansible/latest/collections/infoblox/nios_modules/index.html#plugins-in-infoblox-nios-modules#plugins-in-infoblox-nios_modules",
    "inspur.ispim": "https://docs.ansible.com/ansible/latest/collections/inspur/ispim/index.html#plugins-in-inspur-ispim#plugins-in-inspur-ispim",
    "junipernetworks.junos": "https://docs.ansible.com/ansible/latest/collections/junipernetworks/junos/index.html#plugins-in-junipernetworks-junos#plugins-in-junipernetworks-junos",
    "kaytus.ksmanage": "https://docs.ansible.com/ansible/latest/collections/kaytus/ksmanage/index.html#plugins-in-kaytus-ksmanage#plugins-in-kaytus-ksmanage",
    "kubernetes.core": "https://docs.ansible.com/ansible/latest/collections/kubernetes/core/index.html#plugins-in-kubernetes-core#plugins-in-kubernetes-core",
    "kubevirt.core": "https://docs.ansible.com/ansible/latest/collections/kubevirt/core/index.html#plugins-in-kubevirt-core#plugins-in-kubevirt-core",
    "lowlydba.sqlserver": "https://docs.ansible.com/ansible/latest/collections/lowlydba/sqlserver/index.html#plugins-in-lowlydba-sqlserver#plugins-in-lowlydba-sqlserver",
    "microsoft.ad": "https://docs.ansible.com/ansible/latest/collections/microsoft/ad/index.html#plugins-in-microsoft-ad#plugins-in-microsoft-ad",
    "netapp.cloudmanager": "https://docs.ansible.com/ansible/latest/collections/netapp/cloudmanager/index.html#plugins-in-netapp-cloudmanager#plugins-in-netapp-cloudmanager",
    "netapp.ontap": "https://docs.ansible.com/ansible/latest/collections/netapp/ontap/index.html#plugins-in-netapp-ontap#plugins-in-netapp-ontap",
    "netapp.storagegrid": "https://docs.ansible.com/ansible/latest/collections/netapp/storagegrid/index.html#plugins-in-netapp-storagegrid#plugins-in-netapp-storagegrid",
    "netapp_eseries.santricity": "https://docs.ansible.com/ansible/latest/collections/netapp_eseries/santricity/index.html#plugins-in-netapp-eseries-santricity#plugins-in-netapp_eseries-santricity",
    "netbox.netbox": "https://docs.ansible.com/ansible/latest/collections/netbox/netbox/index.html#plugins-in-netbox-netbox#plugins-in-netbox-netbox",
    "ngine_io.cloudstack": "https://docs.ansible.com/ansible/latest/collections/ngine_io/cloudstack/index.html#plugins-in-ngine-io-cloudstack#plugins-in-ngine_io-cloudstack",
    "openstack.cloud": "https://docs.ansible.com/ansible/latest/collections/openstack/cloud/index.html#plugins-in-openstack-cloud#plugins-in-openstack-cloud",
    "ovirt.ovirt": "https://docs.ansible.com/ansible/latest/collections/ovirt/ovirt/index.html#plugins-in-ovirt-ovirt#plugins-in-ovirt-ovirt",
    "purestorage.flasharray": "https://docs.ansible.com/ansible/latest/collections/purestorage/flasharray/index.html#plugins-in-purestorage-flasharray#plugins-in-purestorage-flasharray",
    "purestorage.flashblade": "https://docs.ansible.com/ansible/latest/collections/purestorage/flashblade/index.html#plugins-in-purestorage-flashblade#plugins-in-purestorage-flashblade",
    "sensu.sensu_go": "https://docs.ansible.com/ansible/latest/collections/sensu/sensu_go/index.html#plugins-in-sensu-sensu-go#plugins-in-sensu-sensu_go",
    "splunk.es": "https://docs.ansible.com/ansible/latest/collections/splunk/es/index.html#plugins-in-splunk-es#plugins-in-splunk-es",
    "telekom_mms.icinga_director": "https://docs.ansible.com/ansible/latest/collections/telekom_mms/icinga_director/index.html#plugins-in-telekom-mms-icinga-director#plugins-in-telekom_mms-icinga_director",
    "theforeman.foreman": "https://docs.ansible.com/ansible/latest/collections/theforeman/foreman/index.html#plugins-in-theforeman-foreman#plugins-in-theforeman-foreman",
    "vmware.vmware": "https://docs.ansible.com/ansible/latest/collections/vmware/vmware/index.html#plugins-in-vmware-vmware#plugins-in-vmware-vmware",
    "vmware.vmware_rest": "https://docs.ansible.com/ansible/latest/collections/vmware/vmware_rest/index.html#plugins-in-vmware-vmware-rest#plugins-in-vmware-vmware_rest",
    "vultr.cloud": "https://docs.ansible.com/ansible/latest/collections/vultr/cloud/index.html#plugins-in-vultr-cloud#plugins-in-vultr-cloud",
    "vyos.vyos": "https://docs.ansible.com/ansible/latest/collections/vyos/vyos/index.html#plugins-in-vyos-vyos#plugins-in-vyos-vyos",
    "wti.remote": "https://docs.ansible.com/ansible/latest/collections/wti/remote/index.html#plugins-in-wti-remote#plugins-in-wti-remote"
}

CACHE_FILE = "ansible_windows_modules.json"

# ✅ Fetch modules from plugin index section
from urllib.parse import urljoin

def fetch_modules(index_url):
    print(f"📥 Fetching: {index_url}")
    response = requests.get(index_url)
    soup = BeautifulSoup(response.text, "html.parser")
    section = soup.find("section", {"id": "plugin-index"})
    modules = []

    if section:
        for li in section.find_all("li"):
            link = li.find("a")
            if link:
                name = link.text.strip()
                href = link.get("href")
                # ✅ Use urljoin to handle broken or relative hrefs
                full_url = urljoin(index_url, href)

                description = li.get_text().replace(name, "", 1).strip("–—-: \n")
                modules.append({
                    "name": name,
                    "url": full_url,
                    "description": description
                })

    return modules

# ✅ Update all collections and write cache
def update_all_modules():
    all_modules = {}
    print("\n🔄 Updating module list...\n")
    for name, url in URLS.items():
        modules = fetch_modules(url)
        modules.sort(key=lambda x: x['name'].lower())
        all_modules[name] = modules
        print(f"✅ {name} - {len(modules)} modules found.")
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(all_modules, f, indent=2, ensure_ascii=False)
    print(f"\n💾 All modules saved to '{CACHE_FILE}' ✔️")

# ✅ Entry point
if __name__ == "__main__":
    update_all_modules()
