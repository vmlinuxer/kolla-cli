# Copyright(c) 2016, Oracle and/or its affiliates.  All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from cliff.command import Command
from kollacli.api.client import ClientApi
import kollacli.i18n as u
import logging
import traceback

LOG = logging.getLogger(__name__)
CLIENT = ClientApi()


class Dump(Command):
    """Dumps configuration data for debugging.

    Dumps most files in /etc/kolla and /usr/share/kolla into a
    tar file so be given to support / development to help with
    debugging problems.
    """
    def take_action(self, parsed_args):
        try:
            dump_path = CLIENT.support_dump()
            LOG.info(u._('Dump successful to {path}').format(path=dump_path))
        except Exception:
            msg = (u._('Dump failed: {reason}')
                   .format(reason=traceback.format_exc()))
            raise Exception(msg)
