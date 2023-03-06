import httpx
from fastapi import HTTPException

REPOSITORY_ADDRESS = "http://localhost:10001"


def get_template(author, name):
    try:
        r = httpx.get(f"{REPOSITORY_ADDRESS}/{author}/{name}")
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