"""Exercise the real OLM task block with a local, network-free module fixture.

Run with Python from an environment containing ansible-core and PyYAML:
    python -m unittest discover -s validation -v
The fixture removes retry delays; it does not validate live OLM behavior.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml


TASKS = Path(__file__).resolve().parents[1] / "tasks/wait_for_olm_operator.yaml"
FIXTURE = '''
from ansible.module_utils.basic import AnsibleModule

module = AnsibleModule(argument_spec=dict(
    api_version=dict(type='str'), kind=dict(type='str'),
    name=dict(type='str'), namespace=dict(type='str'),
    scenario=dict(type='str', required=True),
))
p = module.params
kind, name, scenario = p['kind'], p['name'], p['scenario']
if scenario == 'diagnostics_unavailable':
    module.fail_json(msg='fixture API unavailable')
metadata = dict(name=name or 'fixture', namespace=p['namespace'] or '')
resource = dict(kind=kind, metadata=metadata)
resources = [resource]
if kind == 'Subscription':
    resource['status'] = dict(currentCSV='fixture.v1', installPlanRef=dict(name='install-fixture'))
    if scenario == 'subscription_absent':
        resources = []
    elif scenario == 'subscription_no_status':
        resource.pop('status')
    elif scenario == 'subscription_unresolved':
        resource['status'] = dict(conditions=[dict(
            type='ResolutionFailed', status='True', message='fixture resolution error'
        )])
    elif scenario == 'subscription_empty_csv':
        resource['status']['currentCSV'] = ''
    elif scenario == 'subscription_no_installplan':
        resource['status'].pop('installPlanRef')
elif kind == 'InstallPlan':
    resource['status'] = dict(phase='Complete')
    if scenario == 'installplan_absent':
        resources = []
    elif scenario == 'installplan_no_status':
        resource.pop('status')
    elif scenario == 'installplan_installing':
        resource['status']['phase'] = 'Installing'
    elif scenario == 'installplan_failed':
        resource['status']['phase'] = 'Failed'
elif kind == 'ClusterServiceVersion':
    resource['status'] = dict(phase='Succeeded')
    if scenario == 'csv_absent':
        resources = []
    elif scenario == 'csv_no_status':
        resource.pop('status')
    elif scenario == 'csv_failed':
        resource['status'] = dict(phase='Failed', reason='fixture CSV failure')
elif kind == 'CustomResourceDefinition':
    resource['status'] = dict(conditions=[dict(type='Established', status='True')])
    if scenario == 'crd_absent':
        resources = []
    elif scenario == 'crd_no_status':
        resource.pop('status')
    elif scenario == 'crd_unestablished':
        resource['status']['conditions'][0]['status'] = 'False'
elif kind == 'CatalogSource':
    resource['status'] = dict(connectionState=dict(lastObservedState='TRANSIENT_FAILURE'))
elif kind == 'Event':
    resource.update(reason='FixtureEvent', message='fixture event message')
else:
    resource['status'] = dict(phase='Pending')
module.exit_json(changed=False, resources=resources)
'''


class OLMInstallationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ansible = shutil.which("ansible-playbook")
        if not cls.ansible:
            raise unittest.SkipTest("ansible-playbook must be on PATH")

    def run_scenario(self, scenario, expected_success):
        with tempfile.TemporaryDirectory(prefix="rhdp-olm-test-") as directory:
            root = Path(directory)
            library = root / "library"
            library.mkdir()
            (library / "fixture_olm.py").write_text(FIXTURE)
            tasks = yaml.safe_load(TASKS.read_text())
            for section in ("block", "rescue"):
                for task in tasks[0][section]:
                    if "kubernetes.core.k8s_info" in task:
                        args = task.pop("kubernetes.core.k8s_info")
                        args["scenario"] = "{{ fixture_scenario }}"
                        task["fixture_olm"] = args
                    if "retries" in task:
                        task.update(retries=1, delay=0)
            (root / "tasks.yaml").write_text(yaml.safe_dump(tasks, sort_keys=False))
            # Run both operators to cover reuse of the shared registered variables.
            play = [dict(
                hosts="localhost", gather_facts=False, connection="local",
                vars=dict(fixture_scenario=scenario),
                tasks=[dict(
                    name="Exercise operator gate", include_tasks="tasks.yaml",
                    vars=dict(
                        app_connect_ai_operator_name="{{ item }}",
                        app_connect_ai_operator_crd="fixture.kuadrant.io",
                    ),
                    loop=["limitador-operator", "rhcl-operator"],
                )],
            )]
            playbook = root / "playbook.yaml"
            playbook.write_text(yaml.safe_dump(play, sort_keys=False))
            env = os.environ.copy()
            env.update(ANSIBLE_NOCOLOR="1", ANSIBLE_CONFIG=str(root / "ansible.cfg"))
            (root / "ansible.cfg").write_text("[defaults]\nretry_files_enabled = False\n")
            result = subprocess.run(
                [self.ansible, "-i", "localhost,", str(playbook),
                 "-e", json.dumps(dict(ansible_python_interpreter=shutil.which("python")))],
                cwd=root, env=env, text=True, capture_output=True, timeout=60,
            )
            output = result.stdout + result.stderr
            self.assertEqual(result.returncode == 0, expected_success, output)
            self.assertNotIn("undefined", output.lower(), output)
            if expected_success:
                self.assertNotIn("Collect OLM installation diagnostics", output)
            else:
                self.assertIn("Collect OLM installation diagnostics", output)
                self.assertIn("installation failed at", output)
                if scenario != "diagnostics_unavailable":
                    self.assertIn("TRANSIENT_FAILURE", output)
                    self.assertIn("fixture event message", output)
                else:
                    self.assertIn("fixture API unavailable", output)
            return output

    def test_provisioning_lets_rhcl_resolve_its_dependencies(self):
        tasks = yaml.safe_load((TASKS.parent / "provision_cl_kuadrant.yaml").read_text())
        definitions = [task.get("k8s", {}).get("resource_definition", "") for task in tasks]
        self.assertFalse(any("limitador-subscription" in value for value in definitions))
        gates = [task for task in tasks if "ansible.builtin.include_tasks" in task]
        self.assertEqual(len(gates), 1)
        self.assertEqual(gates[0]["vars"]["app_connect_ai_operator_name"], "rhcl-operator")
        dependency = next(i for i, task in enumerate(tasks)
                          if task.get("kubernetes.core.k8s_info", {}).get("name")
                          == "limitadors.limitador.kuadrant.io")
        instance = next(i for i, task in enumerate(tasks)
                        if task["name"] == "Create Kuadrant instance")
        self.assertLess(tasks.index(gates[0]), dependency)
        self.assertLess(dependency, instance)
        self.assertNotIn("state: absent", (TASKS.parent / "provision_cl_kuadrant.yaml").read_text())

    def test_success(self):
        self.run_scenario("success", True)

    def test_failure_paths(self):
        scenarios = [
            "subscription_absent", "subscription_no_status",
            "subscription_unresolved", "subscription_empty_csv",
            "subscription_no_installplan",
            "csv_absent", "csv_no_status", "csv_failed",
            "installplan_absent", "installplan_no_status",
            "installplan_installing", "installplan_failed",
            "crd_absent", "crd_no_status", "crd_unestablished",
            "diagnostics_unavailable",
        ]
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                self.run_scenario(scenario, False)


if __name__ == "__main__":
    unittest.main()
