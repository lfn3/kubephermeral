import random
import subprocess
import time
from kubernetes import client, config
from pathlib import Path
from typing import List


def apply_manifests(namespace: str, manifests: List[Path]):
    for manifest in manifests:
        subprocess.run([
            'kubectl', 'apply',
            '-f', manifest,
            '--namespace', namespace])


class EphermeralNameSpace:
    def __init__(self, api_client: client.CoreV1Api, name: str):
        self.name = name
        self.api_client = api_client

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.api_client.delete_namespace(self.name)

    def apply_manifests(self, manifests: List[Path]):
        apply_manifests(self.name, manifests)


def create_ns(api: client.CoreV1Api) -> EphermeralNameSpace:
    """Returns the (randomly generated) name of the created namespace"""
    name = f'{random.getrandbits(64)}-{int(time.time())}'
    meta = client.V1ObjectMeta(name=name)
    ns = client.V1Namespace(metadata=meta)
    api.create_namespace(ns)
    print(f"Created namespace {name}")
    return EphermeralNameSpace(api, name)


if __name__ == '__main__':
    configuration = config.load_kube_config()
    api = client.CoreV1Api(client.ApiClient(configuration))
    with create_ns(api) as ns:
        ns.apply_manifests([Path('job.yaml')])

