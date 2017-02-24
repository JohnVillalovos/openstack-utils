#!/usr/bin/python -tt
# vim: ai ts=4 sts=4 et sw=4

# Copyright (c) 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import re
import sys

TELNET_RE = re.compile(
    r'^telnet://((?P<ipv4>[0-9.]*)|\[(?P<ipv6>[0-9a-f:]*)\]):(?P<port>.*)$')


def main():
    args = parse_args()
    # telnet://[2001:4800:1ae1:18:f816:3eff:fe54:3c74]:19885
    result = TELNET_RE.search(args.telnet_url)
    if result:
        matches = result.groupdict()
        for host_key in ('ipv4', 'ipv6'):
            if matches[host_key]:
                break
        else:
            # It didn't match the IPv4 or IPv6 regex :(
            host_key = None
            raise ValueError(
                "URL provided doesn't seem to be an IPv4 or IPv6 address")
        host = result.group(host_key)
        port = result.group('port')
        print "telnet {} {}".format(host, port)
        os.execl("/usr/bin/telnet", "/usr/bin/telnet", host, port)

    sys.exit(
        "Must provide a URL in the form of: telnet://HOST_IP_ADDRESS:PORT")


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "A program to execute telnet when given a URL in the form of "
            "telnet://HOST_IP_ADDRESS:PORT. These URLs are provided by the "
            "Zuul status page http://status.openstack.org/zuul/"),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'telnet_url', metavar="TELNET_URL",
        help=("The URL for the telnet connection. In the form of: "
              "telnet://HOST_IP_ADDRESS:PORT"),
        type=telnet_type)

    args = parser.parse_args()
    return args


def telnet_type(url):
    if not url.startswith("telnet://"):
        raise argparse.ArgumentTypeError(
            "The provided URL does not start with 'telnet://")
    return url


if '__main__' == __name__:
    sys.exit(main())

