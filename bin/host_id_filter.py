#!/usr/bin/env python

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from lib.stamus.common import StamusRestConnection, StamusHostIdFilters

from splunklib.searchcommands import dispatch, EventingCommand, Configuration, Option
from splunklib.searchcommands.validators import Code

@Configuration()
class HostIdFilterCommand(EventingCommand):
    """ Filters, augments, and updates records on the events stream.
    ##Syntax
    .. code-block::
        hostidfilter filter=<expression>
    ##Description
    Filter events to get only events where or the source or the destination IP
    is in the host ID set defined by the filter.
    ##Example
    Display only alerts for IP that run a service on port 443.
    .. code-block::
        | even_type="alert"
        | hostiffilter filter="service.port=443"
    """
    filter = Option(doc='''
        **Syntax:** **filter=***<expression>*
        **Description:** Use space separated field=val filter.
        ''')

    def transform(self, records):
        if not self.filter:
            for record in records:
                yield record
            return

        HOST_URL = '/rest/appliances/host_id_alerts/'
        snc = StamusRestConnection()
        # Do search
        filters = StamusHostIdFilters(self.filter).get()
        resp = snc.get(HOST_URL, params = filters)
        data = resp.get('results', [])

        ips_list = [host['ip'] for host in data]

        for record in records:
            if record.get('src_ip') in ips_list or record.get('dest_ip') in ips_list:
                yield record
        return


dispatch(HostIdFilterCommand, sys.argv, sys.stdin, sys.stdout, __name__)
