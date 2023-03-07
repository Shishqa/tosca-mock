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


def get_template(author, template_name):
    try:
        r = httpx.get(f"{REPOSITORY_ADDRESS}/repository/{author}/templates/{template_name}")
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


def create_topology(author, topology_name, template_author, template_name):
    try:
        r = httpx.post(
            f"{REPOSITORY_ADDRESS}/repository/{author}/topologies/{topology_name}",
            json={ 'template_author': template_author, 'template_name': template_name  },
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


def get_topology(author, topology_name):
    try:
        r = httpx.get(f"{REPOSITORY_ADDRESS}/repository/{author}/topologies/{topology_name}")
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


def update_topology(author, topology_name, updated_topology):
    try:
        r = httpx.put(
            f"{REPOSITORY_ADDRESS}/repository/{author}/topologies/{topology_name}",
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


def delete_topology(author, topology_name):
    try:
        r = httpx.delete(
            f"{REPOSITORY_ADDRESS}/repository/{author}/topologies/{topology_name}"
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

