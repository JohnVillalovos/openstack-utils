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
import logging
import os
import pprint
import re
import subprocess
import sys
import urlparse

from bs4 import BeautifulSoup
import requests

session = requests.Session()

LOG = logging.getLogger(__name__)


def main():
    args = parse_args()
    download_url_directory(args.log_dir_url)


def download_url_directory(url, download_dir=None):
    if download_dir is None:
        # By default use the last path component of the URL path to name the
        # download directory.
        parsed_url = urlparse.urlparse(url)
        dir_name = parsed_url.path.strip('/').split('/')[-1]
        download_dir = os.path.join(os.path.abspath(os.getcwd()), dir_name)
    LOG.info("Processing directory: %s", url)
    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)

    result = session.get(url)
    result.raise_for_status()
    soup = BeautifulSoup(result.text, 'html.parser')

    links = set()
    # We only care about the links in the table, as that is the psuedo
    # directory listing
    for table in soup.find_all('table'):
        table_soup = BeautifulSoup(str(table), 'html.parser')
        for link in table_soup.find_all('a'):
            href = link.get('href')
            # The href should be equal to the text. For example:
            #   <a href="logs/">logs/</a>
            if href == link.string:
                orig_url = urlparse.urljoin(url, href)
                if orig_url in links:
                    continue
                full_url = orig_url
                if full_url:
                    assert full_url.startswith(url)
                    links.add(full_url)
                else:
                    LOG.error("Missing: %s", orig_url)
                    sys.exit(1)
    # Download what we found
    for link in sorted(links):
        if link.endswith('/'):
            parsed_url = urlparse.urlparse(link)
            dir_name = parsed_url.path.strip('/').split('/')[-1]
            download_url_directory(
                link, download_dir=os.path.join(download_dir, dir_name))
        else:
            download_file(link, download_dir)


def download_file(url, download_dir, retries=2):
    LOG.info("Downloading: %s", url)
    parsed_url = urlparse.urlparse(url)
    file_name = os.path.join(download_dir, os.path.basename(parsed_url.path))
    # The '*.gz' files are not really *.gz files, so get rid of the ".gz"
    # extension
    if file_name.endswith('.gz'):
        file_name = file_name[:-3]
    try_count = 0
    while True:
        try:
            result = session.get(url)
            result.raise_for_status()
        except requests.exceptions.ChunkedEncodingError:
            if try_count >= retries:
                LOG.exception()
                raise
            try_count += 1
            LOG.warning("Failure trying to download: %s", url)
            LOG.warning("Download attempt: %s of %s", try_count, retries + 1)
        else:
            break

    with open(file_name, 'w') as out_file:
        out_file.write(result.content)


def parse_args():
    parser = argparse.ArgumentParser(
        description=("A program to download the log files from an OpenStack "
                    "gate job"),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'log_dir_url', metavar="LOGDIR_URL",
        help="The URL for the directory containing the logfiles",
        type=http_type)

    args = parser.parse_args()
    return args


def http_type(url):
    if not url.startswith(('https://', 'http://')):
        raise argparse.ArgumentTypeError(
            "The provided URL does not start with 'https://' or 'http://'")
    return url


if '__main__' == __name__:
    format_string = "%(filename)s %(levelname)s: %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=format_string)
    # A way to figure out all the loggers attached
    #  for key in logging.Logger.manager.loggerDict:
    #      print(key)
    # Disable requests from logging
    logging.getLogger("requests").setLevel(logging.CRITICAL)
    sys.exit(main())
