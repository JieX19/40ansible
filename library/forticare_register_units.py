#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)

# Copyright 2019 Fortinet, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

DOCUMENTATION = '''
---
module: forticare_register_units
short_description: Register products and contracts in FortiCare.
description:
    - The registration of products and contracts are allowed in the same request.
      When registering products/contracts via the registration API, the system will
      return the unit's warranty and contract, for product and contract registration
      (respectively).
      Please note that this module is not idempotent since products already registered
      will return a failure in the request

version_added: '2.9'
author:
    - Miguel Angel Munoz (@mamunozgonzalez)
notes:
    - Run as a local_action in your playbook
requirements:
    - None
options:
    token:
       description:
            - User token required to access FortiCare.
       required: true
    version:
        description:
            - API version.
    register_units:
        description:
            - List of units to be registered.
        suboptions:
            serial_number:
                description:
                    - Product serial number
                required: true
            contract_number:
                description:
                    - Register contract with production
            description:
                description:
                    - Setup product description during registration process
            asset_group_ids:
                description:
                    - Register product under certain asset group. Multiple asset group allowed.
            replaced_serial_number:
                description:
                    - Used for product RMA registration for replaced product serial number
            additional_info:
                description:
                    - It stores extra info for certain product registration, for example system ID, IP address etc.
            is_government:
                description:
                    - Indicates if product will be used for government
'''

EXAMPLES = '''
- hosts: localhost
  tasks:
  - name: Register units
    forticare_register_units:
      token: YOUR_TOKEN
      version: 1.0
      registration_units:
        - serial_number: FMG-3K3407400133
          contract_number: ""
          description: Backup device
          asset_group_ids: ""
          replaced_serial_number: ""
          additional_info: "10.1.1.1"
          is_government: false
'''

RETURN = '''
status_code:
  description: HTTP status code given by FortiCare server for last API operation executed.
  returned: always
  type: integer
  sample: 200
reason:
  description: Status explanation or reason of the failure. Returns 'OK' when successful
  returned: always
  type: str
  sample: 'OK'
content:
  description: Detailed information as dictionary format about the execution of the method and results of the query.
  returned: always
  type: str
  sample: '{"Build": "1.0", "Error": null, "Message": "Success", "Status": 0, "Token": "...", "Version": "1.0", "Assets": [....]'
'''

from ansible.module_utils.basic import AnsibleModule
import requests
import json
import traceback


def forticare_register_units(data):
    body_data = {'Token': data['token']}
    if 'version' in data and data['version']:
        body_data['Version'] = data['version']
    body_data['RegistrationUnits'] = []

    for unit in data['registration_units']:
        unit_data = {'Serial_Number': unit['serial_number']}
        if 'contract_number' in unit and unit['contract_number']:
            unit_data['Contract_Number'] = unit['contract_number']
        if 'description' in unit and unit['description']:
            unit_data['Description'] = unit['description']
        if 'asset_group_ids' in unit and unit['asset_group_ids']:
            unit_data['Asset_Group_IDS'] = unit['asset_group_ids']
        if 'replaced_serial_number' in unit and unit['replaced_serial_number']:
            unit_data['Replaced_Serial_Number'] = unit['replaced_serial_number']
        if 'additional_info' in unit and unit['additional_info']:
            unit_data['Additional_Info'] = unit['additional_info']
        if 'is_government' in unit and unit['is_government']:
            unit_data['Is_Government'] = unit['is_government']

        body_data['RegistrationUnits'].append(unit_data)

    url = 'https://support.fortinet.com/ES/FCWS_RegistrationService.svc/REST/REST_RegisterUnits'

    try:
        r = requests.post(url, json=body_data, timeout=10, verify=True)

    except requests.exceptions.Timeout:
        return True, False, {"status_code": None,
                             "reason": "Timeout contacting FortiCare server",
                             "content": None}
    except Exception as e:
        return True, False, {"status_code": None,
                             "reason": "General exception when running POST on FortiCare server",
                             "content": str(e.__traceback__) + str(traceback.format_exc())}

    content = json.loads(r.content) if r and 'content' in dir(r) else None

    result = {"status_code": r.status_code if r and 'status_code' in dir(r) else None,
              "reason": r.reason if r and 'reason' in dir(r) else None,
              "content": content}

    success = r.status_code != 200 or content['Status'] != 0 if content else True
    return success, not success, result


def main():
    fields = {
        'token': {'required': True, 'type': 'str', 'no_log': True},
        'version': {'required': False, 'type': 'str'},
        'registration_units': {
            'required': True,
            'type': 'list',
            'options': {
                'serial_number': {'required': True, 'type': 'str'},
                'contract_number': {'required': False, 'type': 'str'},
                'description': {'required': False, 'type': 'str'},
                'asset_group_ids': {'required': False, 'type': 'list'},
                'replaced_serial_number': {'required': False, 'type': 'str'},
                'additional_info': {'required': False, 'type': 'str'},
                'is_government': {'required': False, 'type': 'bool', 'default': False}
            }
        }
    }
    module = AnsibleModule(argument_spec=fields,
                           supports_check_mode=False)

    is_error, has_changed, result = forticare_register_units(module.params)

    if not is_error:
        module.exit_json(changed=has_changed, meta=result)
    else:
        module.fail_json(msg='Error in repo', meta=result)


if __name__ == '__main__':
    main()
