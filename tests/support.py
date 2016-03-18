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
import os
import tarfile
import unittest

from common import KollaCliTest
from kollacli.common.utils import get_kollacli_home

LOGS_PREFIX = '/tmp/kolla_support_logs_'


class TestFunctional(KollaCliTest):

    def test_log_collector(self):
        zip_path = ''
        host1 = 'host_test1'
        try:
            path = os.path.join(get_kollacli_home(),
                                'tools', 'log_collector.py')
            retval, msg = self.run_command('%s %s' % (path, host1))
            self.assertEqual(0, retval,
                             'log_collector command failed: %s' % msg)
            self.assertIn(LOGS_PREFIX, msg)
            zip_path = '/tmp' + msg.split('/tmp')[1].strip()
            self.assertTrue(os.path.exists(zip_path),
                            'Zip file %s does not exist' % zip_path)
        except Exception as e:
            raise e
        finally:
            if zip_path and os.path.exists(zip_path):
                os.remove(zip_path)

    def test_dump(self):
        check_files = [
            'var/log/kolla/kolla.log',
            'kolla/etc/config/nova/nova-api.conf',
            'kolla/etc/kollacli/ansible/inventory.json',
            'kolla/share/ansible/site.yml',
            'kolla/share/docs/ansible-deployment.rst',
        ]
        # dump success output is:
        # dump successful to /tmp/kollacli_dump_Umxu6d.tgz
        dump_path = None
        try:
            msg = self.run_cli_cmd('dump')
            self.assertIn('/', msg, 'path not found in dump output: %s' % msg)

            dump_path = '/' + msg.strip().split('/', 1)[1]
            is_file = os.path.isfile(dump_path)
            self.assertTrue(is_file,
                            'dump file not found at %s' % dump_path)
            file_paths = []
            with tarfile.open(dump_path, 'r') as tar:
                file_paths = tar.getnames()

            for check_file in check_files:
                self.assertIn(check_file, file_paths,
                              'dump: check file: %s, not in files:\n%s'
                              % (check_file, file_paths))
        except Exception as e:
            raise e
        finally:
            if dump_path and os.path.exists(dump_path):
                os.remove(dump_path)


if __name__ == '__main__':
    unittest.main()
