import requests
import re
# import json
# from .nutanix_utils import get_nutanix_vms
from ...models import *
from ...utils.main_utils import clear_table


def disks_info_handler(disk_list):
    total_disks = 0
    total_disks_size_mib = 0
    for disk in disk_list:
        # print(disk)
        if 'disk_size_mib' in disk:
            if disk['device_properties']['device_type'] == 'DISK':
                total_disks += 1
                total_disks_size_mib += int(disk['disk_size_mib'])

    return total_disks, total_disks_size_mib


def find_customer_contract(text):
    if str(text).lower().startswith('expim') or str(text).lower().startswith('xpm'):
        return 'EXPIM', 'EXPIM'
    company_id = re.findall(r'\b(\d{6})\b', text)
    contract_num = re.findall(r'\bSR\d{8}\b', text)
    # print(text, contract_num, company_id)
    return company_id, contract_num


def add_nutanix_vm(data):
    ips_pool = set()
    subnets = set()
    for nic in data['status']['resources']['nic_list']:
        # print('========= ********* ===========', nic['ip_endpoint_list'])
        for endpoint in nic['ip_endpoint_list']:
            # print('****************************************', endpoint['ip'], endpoint['type'])
            ips_pool.add(endpoint['ip'])

        vlan_pool = str(nic['subnet_reference']['name']).split('_')
        for vlan in vlan_pool:
            # print('&&&&&:', vlan, vlan_pool)
            if 'vlan' in vlan:
                subnets.add(vlan)
        # subnets.append(nic['subnet_reference']['name'])

    ips_pool_list = list(ips_pool)
    subnets_list = list(subnets)

    if 'hardware_virtualization_enabled' in data['spec']['resources']:
        hard_virtual = data['spec']['resources']['hardware_virtualization_enabled']
    else:
        hard_virtual = False
    desc = data['spec']['description'] if 'description' in data['spec'] else False
    if desc:
        company_id, contract_num = find_customer_contract(desc)
        # print(desc, company_id, contract_num)
    else:
        company_id, contract_num = find_customer_contract(data['spec']['name'])

    if not company_id:
        company_id = 0
    elif company_id == 'EXPIM':
        company_id = 1
    else:
        company_id = company_id[0]

    if not contract_num:
        contract_num = 'Not found'
    elif contract_num == 'EXPIM':
        contract_num = 'EXPIM'
    else:
        contract_num = contract_num[0]

    # print('DISK_LIST:', str(data['spec']['resources']['disk_list']))
    total_disks, total_disks_size_mib = disks_info_handler(data['spec']['resources']['disk_list'])

    new_vm = NutanixVMs(
        uuid=data['metadata']['uuid'],
        creation_time=datetime.strptime(data['metadata']['creation_time'], '%Y-%m-%dT%H:%M:%SZ'),
        cluster_name=data['spec']['cluster_reference']['name'],
        vm_name=data['spec']['name'],
        description=data['spec']['description'] if 'description' in data['spec'] else False,
        company_id=int(company_id),
        contract_num=contract_num,
        num_vcpus_per_socket=data['spec']['resources']['num_vcpus_per_socket'],
        num_threads_per_core=data['spec']['resources']['num_threads_per_core'],
        hardware_virtualization_enabled=hard_virtual,
        num_sockets=data['spec']['resources']['num_sockets'],
        memory_size_mib=data['spec']['resources']['memory_size_mib'],
        total_disks=int(total_disks),
        total_disks_size_mib=int(total_disks_size_mib),
        gpu_list=str(data['spec']['resources']['gpu_list']),
        internal_ip=str(ips_pool_list),
        subnet_reference=str(subnets_list),
        is_agent_vm=data['spec']['resources']['is_agent_vm'],
        power_state=True if data['spec']['resources']['power_state'] == 'ON' else False,
        machine_type=data['spec']['resources']['machine_type'],
    )
    db.session.add(new_vm)
    # print(new_vm.vm_name)
    db.session.commit()
    return True


def get_cluster_vms(cluster_ip, nutanix):
    endpoint = "vms/list"  # All VMs list
    url = f"https://{cluster_ip}:9440/api/nutanix/v3/{endpoint}"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = '{"kind": "vm","length": 500}'
    auth = (f"{nutanix['cluster_username']}", f"{nutanix['cluster_password']}")

    try:
        response = requests.post(url, headers=headers, data=data, auth=auth, verify=False)
    except Exception as e:
        print('Error - get info from Nutanix', e)
        return {}

    # print(response.status_code)
    # print(response.json())
    return response.json()


def get_nutanix_vms(nutanix):
    drop = clear_table(NutanixVMs)
    if drop:
        print(f'Table truncated before updating')

        for cluster_ip in nutanix['clusters_ip']:
            print('Get data from Nutanix cluster:', cluster_ip)
            results = get_cluster_vms(cluster_ip, nutanix)
            # with open('all_nutanix.json', 'a', encoding='utf-8') as json_file:
            #     json_file.write(str(results).replace("'", '"'))
            if results:

                no_spec_counter = 0
                counter = 0
                for vm_data in results['entities']:
                    if "spec" not in vm_data:
                        no_spec_counter += 1
                        print('NO spec', no_spec_counter)
                    else:
                        counter += 1
                        add_nutanix_vm(vm_data)
                print(f'Added from cluster: {counter} VMs')
        return True, 'Nutanix VMs Updated'
    else:
        return False, 'ERROR, when update Nutanix VMs'


def get_virtual_ips(config):  # update from Fortigate VIPs
    drop = clear_table(VirtualIps)
    if not drop:
        return False
    print(f'Table truncated before updating')

    token = config["token"]  # Token
    url = config["url"]
    headers = {"accept": "application/json"}
    params = {'access_token': token}
    response = requests.get(url, headers=headers, params=params, verify=False)

    if response.status_code == 200:
        data = response.json()
        # with open('ranges/forti.json', 'w', encoding='utf-8') as f:
        #     f.write(json.dumps(data, indent=4))
        # forti = json.loads(json.dumps(data, indent=4))

        for record in data["results"]:
            name = None
            int_ip = None
            virtual_ip = None
            comment = None
            if record["name"]:
                name = record["name"]
            if record["extip"]:
                print(record["extip"])
                virtual_ip = record["extip"]
                if '-' in virtual_ip:
                    virtual_ip = f'Error? >> {virtual_ip}'
            if len(record["mappedip"]) > 0:
                if record["mappedip"][0]["q_origin_key"]:
                    int_ip = record["mappedip"][0]["q_origin_key"]
                    if '-' in int_ip:
                        int_ip = f'Error? >> {int_ip}'
            if record["comment"]:
                comment = record["comment"]
            # print(name, virtual_ip, '---', int_ip, comment)
            save_vip_to_db(virtual_ip, int_ip, name, comment)
        return True, 'Updated Virtual IPs from FortiGate API'
    else:
        return False, f"-- Error get Virtual IPs {response.status_code}: {response.text}"


def save_vip_to_db(virtual_ip, internal_ip, name, comment):  # Save Fortigate VIPs
    # with app.app_context():
    existing_record = VirtualIps.query.filter_by(virtual_ip=virtual_ip, internal_ip=internal_ip).first()

    if existing_record:  # Если запись уже существует, обновить ее поля
        existing_record.name = name
        existing_record.comment = comment
        existing_record.last_update = datetime.utcnow()
        # print('Record updated successfully')
    else:  # Если записи не существует, создать новую запись
        new_record = VirtualIps(virtual_ip=virtual_ip, internal_ip=internal_ip, name=name, comment=comment)
        db.session.add(new_record)
        # print(f'New record for {virtual_ip} added successfully')
    db.session.commit()
    # print(f"Added {virtual_ip} | {internal_ip} to DB")
    return


def start_update(fortigate, nutanix):
    update_result = True
    update_log = ''
    result, msg = get_virtual_ips(fortigate)  # Update Fortigate Virtual IPs
    update_log += msg + "\n"
    if not result:
        print('Error update virtual_ips')
        update_result = False

    result, msg = get_nutanix_vms(nutanix)  # Update Nutanix VMs
    update_log += msg + "\n"
    if not result:
        print('Error update nutanix_vms')
        update_result = False

    # cf_result, cf_msg = get_latest_cloudflare_ips()  # Update from CloudFlare range IPs
    # imp_result, imp_msg = get_latest_imperva_ips(cfg)  # Update from Imperva range IPs

    return update_result, update_log
