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


import sys
from os.path import dirname
import os
import subprocess
import http.server
import threading
import unittest
import json
from urllib.parse import urlparse

SUCCESS = 93
NONE = 95
ERROR = 94

ROOT_DIR = dirname(__file__)
HOST = "127.0.0.1"
PORT = "8096"


class HttpServerGetMock(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)

        data = ""
        if parsed_url.path == "/System/Ping":
            data = "success"
            self.send_response(200)
        else:
            data = "failure"
            self.send_response(400)

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        data = "success"
        self.wfile.write(data.encode("utf-8"))


class HttpPostMock(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        parsed_url = urlparse(self.path)

        data = ""
        if parsed_url.path == "/Library/Refresh":
            data = "success"
            self.send_response(200)
        else:
            data = "failure"
            self.send_response(400)

        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(data.encode("utf-8"))


def get_python():
    if os.name == "nt":
        return "python"
    return "python3"


def run_script():
    sys.stdout.flush()
    proc = subprocess.Popen(
        [get_python(), ROOT_DIR + "/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy(),
    )
    out, err = proc.communicate()
    ret_code = proc.returncode
    return (out.decode(), int(ret_code), err.decode())


def set_default_env():
    os.environ["NZBPO_APIKEY"] = "API_KEY"
    os.environ["NZBPP_DIRECTORY"] = ROOT_DIR
    os.environ["NZBPO_HOST"] = HOST
    os.environ["NZBPO_PORT"] = PORT
    os.environ["NZBPO_VERBOSE"] = "yes"


class Tests(unittest.TestCase):
    def test_command(self):
        set_default_env()
        os.environ["NZBCP_COMMAND"] = "ping"
        server = http.server.HTTPServer((HOST, int(PORT)), HttpServerGetMock)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        [_, code, _] = run_script()
        server.shutdown()
        server.server_close()
        thread.join()
        self.assertEqual(code, SUCCESS)

    def test_refresh_lib(self):
        set_default_env()
        os.environ.pop("NZBCP_COMMAND", None)
        server = http.server.HTTPServer((HOST, int(PORT)), HttpPostMock)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        [_, code, _] = run_script()
        server.shutdown()
        server.server_close()
        thread.join()
        self.assertEqual(code, SUCCESS)

    def test_manifest(self):
        with open(ROOT_DIR + "/manifest.json", encoding="utf-8") as file:
            try:
                json.loads(file.read())
            except ValueError as e:
                self.fail(f"manifest.json is not valid: {e}")


if __name__ == "__main__":
    unittest.main()
