"""Network-free cluster tests: render probes and exercise URI retries on localhost.

Requires ansible-core, PyYAML and Jinja2. No cluster credentials are used.
"""
import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest

from jinja2 import Environment, StrictUndefined
import yaml


ROLE = Path(__file__).resolve().parents[1]
TASK = next(
    task for task in yaml.safe_load((ROLE / "tasks/provision_im_rocketchat.yaml").read_text())
    if task["name"] == "Disable RC API Rate Limiter"
)


class RocketChatStartupTests(unittest.TestCase):
    def test_rendered_startup_probe(self):
        template = (ROLE / "templates/im_rocketchat.yaml.j2").read_text()
        rendered = Environment(autoescape=True, undefined=StrictUndefined).from_string(template).render(
            rocketchat_namespace="rocketchat", route_subdomain="apps.example.invalid"
        )
        resources = list(yaml.safe_load_all(rendered))
        container = resources[0]["spec"]["template"]["spec"]["containers"][0]
        probe = container["startupProbe"]
        self.assertEqual(probe["httpGet"], container["livenessProbe"]["httpGet"])
        self.assertEqual(probe["failureThreshold"] * probe["periodSeconds"], 300)
        self.assertEqual(resources[1]["kind"], "Service")
        self.assertEqual(resources[2]["kind"], "Route")

    def test_request_configuration(self):
        headers = TASK["uri"]["headers"]
        self.assertEqual(headers["X-2fa-method"], "password")
        self.assertRegex(headers["X-2fa-code"], r"^[0-9a-f]{64}$")
        self.assertEqual(TASK["uri"]["status_code"], 200)
        self.assertEqual(TASK["uri"]["timeout"], 30)
        self.assertTrue(TASK["no_log"])
        self.assertEqual(TASK["retries"], 20)
        self.assertEqual(TASK["delay"], 10)

    def run_responses(self, statuses, success, expected_calls):
        ansible = shutil.which("ansible-playbook")
        if not ansible:
            self.skipTest("ansible-playbook must be on PATH")
        calls = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length", "0")))
                status = statuses[min(len(calls), len(statuses) - 1)]
                calls.append(status)
                if status == -1:
                    self.close_connection = True
                    return
                body = json.dumps(dict(success=status == 200)).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            task = copy.deepcopy(TASK)
            # Keep the real URI module and until expression. Only replace the
            # destination/credentials and shorten the retry budget for fixtures.
            task["uri"]["url"] = f"http://127.0.0.1:{server.server_port}/settings"
            task["uri"]["headers"] = {"accept": "application/json"}
            task.update(retries=2, delay=0)
            play = [dict(hosts="localhost", gather_facts=False, connection="local", tasks=[task])]
            with tempfile.TemporaryDirectory(prefix="rhdp-rocketchat-test-") as directory:
                root = Path(directory)
                (root / "playbook.yaml").write_text(yaml.safe_dump(play, sort_keys=False))
                (root / "ansible.cfg").write_text("[defaults]\nretry_files_enabled = False\n")
                env = os.environ.copy()
                env.update(ANSIBLE_CONFIG=str(root / "ansible.cfg"), ANSIBLE_NOCOLOR="1")
                result = subprocess.run(
                    [ansible, "-i", "localhost,", str(root / "playbook.yaml"),
                     "-e", json.dumps(dict(ansible_python_interpreter=shutil.which("python")))],
                    cwd=root, env=env, text=True, capture_output=True, timeout=60,
                )
                self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
                self.assertEqual(len(calls), expected_calls, calls)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_503_then_success(self):
        self.run_responses([503, 503, 200], True, 3)

    def test_transport_error_then_success(self):
        self.run_responses([-1, 200], True, 2)

    def test_persistent_503_fails(self):
        self.run_responses([503], False, 3)

    def test_authentication_error_fails_without_retry(self):
        self.run_responses([401], False, 1)

    def test_forbidden_fails_without_retry(self):
        self.run_responses([403], False, 1)


if __name__ == "__main__":
    unittest.main()
