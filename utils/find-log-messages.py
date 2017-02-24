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

from __future__ import print_function

import argparse
import collections
import logging
import os
import re
import sys

import colorama
colorama.init()

LOG = logging.getLogger(__name__)

LEVEL_COLORS = collections.OrderedDict([
    ('DEBUG', colorama.Style.RESET_ALL),
    ('INFO', colorama.Fore.MAGENTA),
    ('AUDIT', colorama.Fore.CYAN),
    ('TRACE', colorama.Fore.BLUE),
    ('WARNING', colorama.Fore.YELLOW),
    ('ERROR', colorama.Fore.LIGHTRED_EX),
])


def main():
    args = parse_args()
    process_log_files('.', level=args.level)


def process_log_files(directory, level=None):
    for filename in sorted(os.listdir(directory)):
        filename = os.path.join(directory, filename)
        if os.path.isfile(filename):
            process_file(filename, level=level)
        elif os.path.isdir(filename):
            process_log_files(filename, level=level)


def process_file(filename, level=None):
    # 2017-02-21 18:44:45.605 17469 ERROR
    level_re = generate_log_level_regex(level)
    search_re = re.compile(
        (r'(?P<date_time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} \d{1,5}) ' +
         r'(?P<level>' + level_re + r') ' +
         r'(?P<remaining>.*$)')
    )
    found = False
    with open(filename) as in_file:
        for line in in_file.readlines():
            line = line.rstrip()
            result = search_re.search(line)
            if result:
                if not found:
                    print(filename)
                    found = True

                date_time = result.group('date_time')
                log_level = result.group('level')
                remain = result.group('remaining')
                line = line.rstrip()
                print(
                    LEVEL_COLORS[log_level] + line + colorama.Style.RESET_ALL)
            elif level is None:
                print(line)


def generate_log_level_regex(level):
    # Given a level, create a regex for the level and all higher level messages
    # For example: If we look for WARNING level we also want ERROR level. So
    # create a regex of r'WARNING|ERROR'
    if level is None:
        return '[A-Z]+'
    level = level.upper()
    if level not in LEVEL_COLORS:
        raise ValueError("{!r} is not a valid log level")
    colors_list = LEVEL_COLORS.keys()
    index =  colors_list.index(level)
    regex_str = "|".join(colors_list[index:])
    return regex_str


def parse_args():
    parser = argparse.ArgumentParser(
        description=("A program to find error messages in log files"),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-l', '--level', default="ERROR",
        help=("The message level to search for. Will include all more severe "
              "level messages. The WARNING level will also include ERROR "
              "level"),
        choices=list(LEVEL_COLORS) + [x.lower() for x in LEVEL_COLORS],
    )

    args = parser.parse_args()
    return args


if '__main__' == __name__:
    format_string = "%(filename)s %(levelname)s: %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=format_string)
    sys.exit(main())
