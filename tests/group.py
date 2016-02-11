# Copyright(c) 2016, Oracle and/or its affiliates.  All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
from common import KollaCliTest

import json
import unittest

from kollacli.common.inventory import DEFAULT_GROUPS
from kollacli.common.inventory import DEFAULT_OVERRIDES
from kollacli.common.inventory import DEPLOY_GROUPS


class TestFunctional(KollaCliTest):

    def test_group_add_remove(self):
        groups = self.get_default_groups()

        # check default group list
        self.check_group(groups)

        tg1 = 'test_group_t1'
        tg2 = 'test_group_t2'

        self.run_cli_cmd('group add %s' % tg1)
        groups[tg1] = {
            'Services': [],
            'Hosts': []}
        self.check_group(groups)

        self.run_cli_cmd('group add %s' % tg2)
        groups[tg2] = {
            'Services': [],
            'Hosts': []}
        self.check_group(groups)

        self.run_cli_cmd('group remove %s' % tg2)
        del groups[tg2]
        self.check_group(groups)

        self.run_cli_cmd('group remove %s' % tg1)
        del groups[tg1]
        self.check_group(groups)

    def test_group_add_host(self):
        groups = self.get_default_groups()

        host1 = 'test_host1'
        host2 = 'test_host2'
        groupname = 'compute'

        group = groups[groupname]
        hosts = group['Hosts']

        self.run_cli_cmd('host add %s' % host1)

        hosts.append(host1)
        self.run_cli_cmd('group addhost %s %s' % (groupname, host1))
        self.check_group(groups)

        self.run_cli_cmd('host add %s' % host2)

        hosts.append(host2)
        self.run_cli_cmd('group addhost %s %s' % (groupname, host2))
        self.check_group(groups)

        self.run_cli_cmd('group removehost %s %s' % (groupname, host2))
        hosts.remove(host2)
        self.check_group(groups)

        self.run_cli_cmd('group removehost %s %s' % (groupname, host1))
        hosts.remove(host1)
        self.check_group(groups)

    def test_add_group_to_service(self):
        groups = self.get_default_groups()

        groupname = 'compute'
        service1 = 'keystone'
        service2 = 'heat-api'

        self.run_cli_cmd('service addgroup %s %s' % (service1, groupname))
        groups[groupname]['Services'].append(service1)
        self.check_group(groups)

        self.run_cli_cmd('service addgroup %s %s' % (service2, groupname))
        groups[groupname]['Services'].append(service2)
        self.check_group(groups)

        self.run_cli_cmd('service removegroup %s %s'
                         % (service2, groupname))
        groups[groupname]['Services'].remove(service2)
        self.check_group(groups)

        self.run_cli_cmd('service removegroup %s %s'
                         % (service1, groupname))
        groups[groupname]['Services'].remove(service1)
        self.check_group(groups)

    def check_group(self, groups):
        """check groups

        group listhosts -f json:
            group listhosts -f json
                [{"Group Name": "compute", "Hosts": []},
                {"Group Name": "control", "Hosts": ["ub-target1"]},
                {"Group Name": "network", "Hosts": []}]

            group listservices -f json:
                [{"Group Name": "compute", "Services": []},
                {"Group Name": "control",
                    "Services": ["glance", "keystone", "mysqlcluster",
                        "nova", "rabbitmq"]},
                {"Group Name": "network", "Services": ["haproxy", "neutron"]}]
        """
        # check hosts in groups
        msg = self.run_cli_cmd('group listhosts -f json')
        cli_groups = json.loads(msg)
        self.assertEqual(len(cli_groups), len(groups),
                         '# of groups in cli not equal to expected groups.' +
                         '\n\nexpected: %s, \n\ncli: %s'
                         % (groups, cli_groups))

        for cli_group in cli_groups:
            cli_hosts = cli_group['Hosts']
            for group_name, info in groups.items():
                if group_name != cli_group['Group']:
                    continue
                group_hosts = info['Hosts']
                self.assertEqual(len(cli_hosts), len(group_hosts),
                                 'Group: %s. # of hosts in cli ' % group_name +
                                 'not equal to expected hosts, ' +
                                 '\n\nexpected: %s, \n\ncli: %s'
                                 % (group_hosts, cli_hosts))

                for group_host in group_hosts:
                    self.assertIn(group_host, cli_hosts,
                                  'Group: %s' % group_name +
                                  '\n\nexpected_hosts: %s, \n\nnot in cli: %s '
                                  % (group_host, cli_hosts))

        # check services in group
        msg = self.run_cli_cmd('group listservices -f json')
        cli_groups = json.loads(msg)

        for cli_group in cli_groups:
            cli_services = cli_group['Services']
            for group_name, info in groups.items():
                if group_name != cli_group['Group']:
                    continue
                group_services = info['Services']
                self.assertEqual(len(cli_services), len(group_services),
                                 'Group: %s. # of services in cli'
                                 % group_name +
                                 ' not equal to expected services,' +
                                 '\nexpected: %s, \ncli: %s'
                                 % (group_services, cli_services))
                for group_service in group_services:
                    self.assertIn(group_service, cli_services,
                                  'Group: %s' % group_name +
                                  '\nexpected_services: %s, \nnot in cli: %s '
                                  % (group_service, cli_services))

    def get_default_groups(self):
        """get default groups

        return a dict:
        {
          groupname: {
                      Services: [svc1, svc2...],
                      Hosts: []
                      }
        }
        """
        groups = {}
        for groupname in DEPLOY_GROUPS:
            groups[groupname] = {'Services': [],
                                 'Hosts': []}

        for servicename, groupname in DEFAULT_GROUPS.items():
            groups[groupname]['Services'].append(servicename)

        for servicename, groupname in DEFAULT_OVERRIDES.items():
            groups[groupname]['Services'].append(servicename)

        return groups


if __name__ == '__main__':
    unittest.main()
