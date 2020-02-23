import logging
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
    def __init__(self, api_client: client.ApiClient, name: str):
        self.name = name
        self.api_client = api_client
        self.core_v1_api = client.CoreV1Api(api_client)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.core_v1_api.delete_namespace(self.name)
        logging.info(f"Deleted {self}")

    def __str__(self):
        return f"EphermeralNameSpace[{self.name}] on [{self.api_client.configuration.host}]"

    def apply_manifests(self, manifests: List[Path]):
        apply_manifests(self.name, manifests)


def create_named_ns(name: str, api: client.ApiClient):
    meta = client.V1ObjectMeta(name=name)
    ns = client.V1Namespace(metadata=meta)
    client.CoreV1Api(api).create_namespace(ns)


def create_ns(api: client.ApiClient) -> EphermeralNameSpace:
    """Returns the (randomly generated) name of the created namespace"""
    name = f'{random.getrandbits(64)}-{int(time.time())}'
    create_named_ns(name, api)
    ns = EphermeralNameSpace(api, name)
    logging.info(f"Created {ns}")
    return ns


def api_client_from_config() -> client.ApiClient:
    configuration = config.load_kube_config()
    return client.ApiClient(configuration)
