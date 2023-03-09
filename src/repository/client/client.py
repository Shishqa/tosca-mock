import httpx
from fastapi import HTTPException

REPOSITORY_ADDRESS = "http://localhost:10001"


def get_substitutions(type_name):
    try:
        r = httpx.get(f"{REPOSITORY_ADDRESS}/substitutions/{type_name}")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                'error': "Could not connect to repository",
                'response': exc.response
            }
        )


def get_template(template_id):
    try:
        r = httpx.get(f"{REPOSITORY_ADDRESS}/templates/{template_id}")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                'error': "Could not connect to repository",
                'response': exc.response
            }
        )


def create_topology(template_id):
    try:
        r = httpx.post(
            f"{REPOSITORY_ADDRESS}/topologies",
            json={ 'template_id': template_id },
        )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                'error': "Could not connect to repository",
                'response': exc.response
            }
        )


def get_topology(topology_id):
    try:
        r = httpx.get(f"{REPOSITORY_ADDRESS}/topologies/{topology_id}")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                'error': "Could not connect to repository",
                'response': exc.response
            }
        )


def update_topology(topology_id, updated_topology):
    try:
        r = httpx.put(
            f"{REPOSITORY_ADDRESS}/topologies/{topology_id}",
            json=updated_topology
        )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                'error': "Could not connect to repository",
                'response': exc.response
            }
        )


def delete_topology(topology_id):
    try:
        r = httpx.delete(
            f"{REPOSITORY_ADDRESS}/topologies/{topology_id}"
        )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                'error': "Could not connect to repository",
                'response': exc.response
            }
        )

