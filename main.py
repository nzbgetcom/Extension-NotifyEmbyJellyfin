#
# This file is part of nzbget. See <https://nzbget.com>.
#
# Copyright (C) 2024 Denis <denis@nzbget.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#


import os
import sys
import urllib.parse
import urllib.request

SUCCESS = 93
ERROR = 94
NONE = 95


REQUIRED_OPTIONS = [
    "NZBPO_APIKEY",
    "NZBPO_HOST",
    "NZBPO_PORT",
]


def validate_options(options: list) -> None:
    for optname in options:
        if optname not in os.environ:
            print(
                f"[ERROR] Option {optname[6:]} is missing in configuration file. Please check extension settings."
            )
            sys.exit(ERROR)


validate_options(REQUIRED_OPTIONS)


API_KEY = os.environ["NZBPO_APIKEY"]
HOST = os.environ["NZBPO_HOST"]
PORT = os.environ["NZBPO_PORT"]


VERBOSE = os.environ["NZBPO_VERBOSE"] == "yes"
COMMAND = os.environ.get("NZBCP_COMMAND") == "ping"

URL = f"http://{HOST}:{PORT}"


if VERBOSE:
    print("[INFO] URL:", URL)


def ping_server(url: str) -> int:
    req_url = f"{url}/System/Ping"

    if VERBOSE:
        print(f"[INFO] REQUEST URL: {req_url}")

    try:
        req = urllib.request.Request(req_url)
        with urllib.request.urlopen(req) as response:
            data = response.read().decode("utf-8")

            print(
                f"[INFO] Server pinged successfully: {data}",
            )
            return SUCCESS

    except Exception as ex:
        print(f"[ERROR] Unexpected exception: {ex}. Wrong API key?")
        return ERROR


def refresh_library(url) -> int:
    req_url = f"{url}/Library/Refresh"
    headers = {"Authorization": f'MediaBrowser Client="NZBGet", Token="{API_KEY}"'}

    if VERBOSE:
        print(f"[INFO] REQUEST URL: {req_url}")
        print(f"[INFO] HEADERS: {headers}")

    try:
        req = urllib.request.Request(req_url, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            data = response.read().decode("utf-8")

            print(f"[INFO] The library refreshed successfully: {data}")
            return SUCCESS

    except Exception as ex:
        print(f"[ERROR] Unexpected exception: {ex}")
        return ERROR


if COMMAND:
    sys.exit(ping_server(URL))


PATH = os.environ.get("NZBPP_FINALDIR") or os.environ["NZBPP_DIRECTORY"]


if VERBOSE:
    print(f"[INFO] PATH: {PATH}")


sys.exit(refresh_library(URL))
