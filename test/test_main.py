from pathlib import Path

from main import with_manifests, api_client_from_config, EphermeralNameSpace


@with_manifests([Path('..') / 'job.yaml'])
def test_fixture(kubephemeral: EphermeralNameSpace):
    # TODO: get job
    pass
