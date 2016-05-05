#!/usr/bin/env python
"""Jobs running in scriptworker will use functions in this file.
"""
import arrow
import glob
import json
import jsonschema
import os
from scriptworker.exceptions import ScriptWorkerTaskException


def get_task(config):
    try:
        path = os.path.join(config['work_dir'], "task.json")
        with open(path, "r") as fh:
            contents = json.load(fh)
            return contents['task']
    except (OSError, ValueError) as exc:
        raise ScriptWorkerTaskException(
            "Can't read task from {}!".format(path),
            super_exc=exc
        )


def get_temp_creds_from_file(config):
    path = os.path.join(config['work_dir'], "credentials.*.json")
    files = glob.glob(path)
    # TODO


def validate_task_schema(task, schema):
    try:
        jsonschema.validate(task, schema)
    except jsonschema.exceptions.ValidationError as exc:
        raise ScriptWorkerTaskException(
            "Can't validate task schema!",
            super_exc=exc
        )


def integration_create_task_payload(config, task_group_id, scopes=None,
                                    task_payload=None, task_extra=None):
    """For various integration tests, we need to call createTask for test tasks.

    This function creates a dummy payload for those createTask calls.
    """
    now = arrow.utcnow()
    deadline = now.replace(hours=1)
    expires = now.replace(days=3)
    scopes = scopes or []
    task_payload = task_payload or {}
    task_extra = task_extra or {}
    return {
        'provisionerId': config['provisioner_id'],
        'schedulerId': config['scheduler_id'],
        'workerType': config['worker_type'],
        'taskGroupId': task_group_id,
        'dependencies': [],
        'requires': 'all-completed',
        'routes': [],
        'priority': 'normal',
        'retries': 5,
        'created': now.isoformat(),
        'deadline': deadline.isoformat(),
        'expires': expires.isoformat(),
        'scopes': scopes,
        'payload': task_payload,
        'metadata': {
            'name': 'ScriptWorker Integration Test',
            'description': 'ScriptWorker Integration Test',
            'owner': 'release+python@mozilla.com',
            'source': 'https://github.com/escapewindow/scriptworker/'
        },
        'tags': {},
        'extra': task_extra,
    }
