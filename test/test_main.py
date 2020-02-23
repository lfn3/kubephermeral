from pathlib import Path

from kubephemeral.main import api_client_from_config, create_ns
from kubernetes import client


def test_creates_namespace():
    api = api_client_from_config()
    with create_ns(api) as ns:
        ns_names = [ns.metadata.name for ns in client.CoreV1Api(api).list_namespace().items]
        assert ns.name in ns_names


def test_cleans_up_namespace():
    api = api_client_from_config()
    with create_ns(api) as eph_ns:
        ns_names = [ns.metadata.name for ns in client.CoreV1Api(api).list_namespace().items]
        assert eph_ns.name in ns_names

    matching_nses = [ns for ns in client.CoreV1Api(api).list_namespace().items if ns.metadata.name == eph_ns.name]
    if matching_nses == 0:
        return  # Already terminated, success!

    # Or, there should only be one...
    assert len(matching_nses) == 1
    k8s_ns = matching_nses[0]
    # ... that is being cleaned up.
    assert k8s_ns.status.phase == 'Terminating'


def test_with_manifests():
    api = api_client_from_config()
    job_api = client.BatchV1Api(api)
    with create_ns(api) as eph_ns:
        eph_ns.apply_manifests([Path("..") / "job.yaml"])
        jobs = job_api.list_namespaced_job(eph_ns.name).items
        assert len(jobs) == 1
