import re
import requests
import ast
import pandas as pd
from ...models import *
from ...utils.main_utils import get_priority_detailed_info


def get_external_ips(ip_pool):
    try:
        result_list = ast.literal_eval(ip_pool)
        if not isinstance(result_list, list):
            result_list = ''
    except (ValueError, SyntaxError) as e:
        print(f"Error convert str to list: {e}")
        return None

    ext_pool = []
    for ip_address in result_list:
        result = VirtualIps.query.filter_by(internal_ip=ip_address).first()
        if result is not None:
            ext_pool.append(str(result.virtual_ip))

    return str(ext_pool)


def report_nutanix_vms_to_xlsx(data):
    def get_company_name(company_id):
        customer = PriorityCompanies.query.filter_by(custname=company_id).first()
        if customer is not None:
            return customer.custdes

    def get_state(power_state):
        return 'On' if power_state else 'Off'

    def get_memory(memory_in_mb):
        gb = memory_in_mb / 1024
        if gb >= 1:
            return f"{int(gb)} Gb"
        else:
            return f"{int(memory_in_mb)} Mb"

    df = pd.DataFrame(
        [
            [
                i + 1, get_state(d.power_state), d.uuid, d.creation_time, d.cluster_name, d.vm_name, d.description,
                d.company_id, get_company_name(d.company_id), d.contract_num, d.num_vcpus_per_socket,
                d.num_threads_per_core, d.num_sockets, get_memory(d.memory_size_mib), d.total_disks,
                get_memory(d.total_disks_size_mib), d.internal_ip, get_external_ips(d.internal_ip), d.subnet_reference
            ]
            for i, d in enumerate(data)
        ],
        columns=[
            '#', 'Power State', 'Uuid', 'Creation Time', 'Cluster Name', 'Vm Name', 'Description', 'Company Id', 'Name',
            'Contract Num', 'Num Vcpus Per Socket', 'Num Threads Per Core', 'Num Sockets', 'Memory Size Mib',
            'Total Disks', 'Total Disks Size Mib', 'Internal Ip', 'External Ip', 'Subnet Reference'
        ]
    )

    fn = f'nutanix_vms_{str(int(time.time()))}.xlsx'
    writer = pd.ExcelWriter(f'static/report/{fn}', engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Nutanix_VMs')
    writer.book.save(f'static/report/{fn}')
    return fn


def get_vms_additional_data(vms, search_query, expim_priority):
    customers = PriorityCompanies.query.all()
    company_id_pool = []

    for company in vms:
        company_id_pool.append(str(company.company_id))
    company_id_pool = str(set(company_id_pool)).strip('{}')

    contracts = get_priority_detailed_info(expim_priority, company_id_pool)
    counters = count(vms)

    full_details = False
    if search_query:
        full_details = details_count(vms)
    print(counters)

    return counters, customers, contracts, full_details


def get_vms_like(search_query):
    vms = NutanixVMs.query.filter(
            (NutanixVMs.vm_name.ilike(f"%{search_query}%")) |
            (NutanixVMs.company_id.ilike(f"%{search_query}%")) |
            (NutanixVMs.contract_num.ilike(f"%{search_query}%")) |
            (NutanixVMs.internal_ip.ilike(f"%{search_query}%")) |
            (NutanixVMs.subnet_reference.ilike(f"%{search_query}%"))
        ).all()
    if not vms:
        vms = 0
    return vms


def details_count(vms):
    conditions_pool = []
    for vm in vms:
        conditions_pool.append((int(vm.company_id), vm.contract_num))
    details_result_search = {}
    details_result_calc = {}
    for unit in set(conditions_pool):
        name = str(unit[1])
        details_result_search[name+'_'+str(unit[0])] = []
        details_result_calc[name] = {
            'company_id': str(unit[0]),
            'disks': 0,
        }

        data = NutanixDetails.query.filter(
            NutanixDetails.CUSTOMERS_CUSTNAME == unit[0], NutanixDetails.DOCUMENTS_DOCNO == unit[1]).all()
        for row in data:
            details_result_search[name+'_'+str(unit[0])].append(row.PART_PARTNAME)
        for item in details_result_search[name+'_'+str(unit[0])]:
            if item in details_result_calc[name]:
                details_result_calc[name][item] += 1
                if item in ("VPS-HDSSD", "VPS-HDSAS", "VPS-HDHYB"):
                    details_result_calc[name]['disks'] += 1
            else:
                details_result_calc[name][item] = 1
    print(details_result_calc)
    return details_result_calc


def count(pool):
    counters = {
        'all': len(pool),
        'active': 0,
        'inactive': 0,
        'NutLin': 0,
        'NutLin-active': 0,
        'NutWin': 0,
        'NutWin-active': 0,
        'NutCLS': 0,
        'NutCLS-active': 0,
        'vCPUs': 0,
        'sockets': 0,
        'CPU_totally': 0,
        'RAM': 0,
        'disks': 0,
        'disks_size': 0,
    }

    for vm in pool:
        if vm.power_state == 1:
            counters['active'] += 1
            counters['vCPUs'] += int(vm.num_vcpus_per_socket)
            counters['sockets'] += int(vm.num_sockets)
            counters['RAM'] += int(vm.memory_size_mib)
            counters['CPU_totally'] += int(vm.num_vcpus_per_socket) * int(vm.num_sockets)
            counters['disks'] += vm.total_disks
            counters['disks_size'] += vm.total_disks_size_mib

        if vm.cluster_name == 'XpmNutLin':
            counters['NutLin'] += 1
            counters['NutLin-active'] += int(vm.power_state)
        elif vm.cluster_name == 'XPMNUTWIN':
            counters['NutWin'] += 1
            counters['NutWin-active'] += int(vm.power_state)
        elif vm.cluster_name == 'NUTCLS':
            counters['NutCLS'] += 1
            counters['NutCLS-active'] += int(vm.power_state)
        else:
            print()
    counters['inactive'] = counters['all'] - counters['active']
    counters['NutLin-inactive'] = counters['NutLin'] - counters['NutLin-active']
    counters['NutWin-inactive'] = counters['NutWin'] - counters['NutWin-active']
    counters['NutCLS-inactive'] = counters['NutCLS'] - counters['NutCLS-active']
    return counters


def add_all_nutanix_details(lines):
    for line in lines:
        new_details = NutanixDetails(
            CUSTOMERS_CUSTNAME=line[3],
            DOCUMENTS_DOC=line[0],
            DOCUMENTS_DOCNO=line[1],
            PART_PARTNAME=line[9],
        )
        db.session.add(new_details)
    db.session.commit()


def bits_to_gb(bits):
    gb_value = round(bits / 8 / 1024 / 1024 / 1024, 2)
    return gb_value
