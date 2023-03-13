import httpx
from fastapi import HTTPException

from ..tosca.normalized import NormalizedServiceTemplate


RESOLVER_ADDRESS = "http://localhost:10002"


def get_cluster(cluster_id):
    try:
        r = httpx.get(f"{RESOLVER_ADDRESS}/clusters/{cluster_id}")
        r.raise_for_status()
        return NormalizedServiceTemplate.parse_obj(r.json())
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                'error': "Could not connect to repository",
                'response': exc.response
            }
        )
