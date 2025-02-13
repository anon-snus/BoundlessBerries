import json
import os
import random
from decimal import Decimal
import aiohttp
from aiohttp_proxy import ProxyConnector
from libs.eth_async import exceptions


def randfloat(from_: int | float | str, to_: int | float | str,
              step: int | float | str | None = None) -> float:
    """
    Return a random float from the range.

    :param Union[int, float, str] from_: the minimum value
    :param Union[int, float, str] to_: the maximum value
    :param Optional[Union[int, float, str]] step: the step size (calculated based on the number of decimal places)
    :return float: the random float
    """
    from_ = Decimal(str(from_))
    to_ = Decimal(str(to_))
    if not step:
        step = 1 / 10 ** (min(from_.as_tuple().exponent, to_.as_tuple().exponent) * -1)

    step = Decimal(str(step))
    rand_int = Decimal(str(random.randint(0, int((to_ - from_) / step))))
    return float(rand_int * step + from_)

def join_path(path: str | tuple | list) -> str:
    if isinstance(path, str):
        return path
    return str(os.path.join(*path))


def read_json(path: str | tuple | list, encoding: str | None = None) -> list | dict:
    path = join_path(path)
    return json.load(open(path, encoding=encoding))


def update_dict(modifiable: dict, template: dict, rearrange: bool = True, remove_extra_keys: bool = False) -> dict:
    """
    Update the specified dictionary with any number of dictionary attachments based on the template without changing the values already set.

    :param dict modifiable: a dictionary for template-based modification
    :param dict template: the dictionary-template
    :param bool rearrange: make the order of the keys as in the template, and place the extra keys at the end (True)
    :param bool remove_extra_keys: whether to remove unnecessary keys and their values (False)
    :return dict: the modified dictionary
    """
    for key, value in template.items():
        if key not in modifiable:
            modifiable.update({key: value})

        elif isinstance(value, dict):
            modifiable[key] = update_dict(
                modifiable=modifiable[key], template=value, rearrange=rearrange, remove_extra_keys=remove_extra_keys
            )

    if rearrange:
        new_dict = {}
        for key in template.keys():
            new_dict[key] = modifiable[key]

        for key in tuple(set(modifiable) - set(new_dict)):
            new_dict[key] = modifiable[key]

    else:
        new_dict = modifiable.copy()

    if remove_extra_keys:
        for key in tuple(set(modifiable) - set(template)):
            del new_dict[key]

    return new_dict

async def async_post(
        url: str,
        data: dict | None = None,
        json: dict | None = None,
        proxy: str | None = None,
        headers: dict | None = None,
        response_type: str = 'json',
        **kwargs
) -> dict | str | None:
    """
    Asynchronously send a POST request.

    :param url: Target URL.
    :param data: Form-encoded data to send in the body of the request.
    :param json: JSON data to send in the body of the request.
    :param proxy: Proxy URL (e.g., 'http://proxyserver:port').
    :param headers: HTTP headers.
    :param response_type: Expected response type ('json' or 'text').
    :param kwargs: Additional parameters for aiohttp.ClientSession.post().
    :return: Parsed response based on response_type.
    """
    if proxy and 'http://' not in proxy:
        proxy = f'http://{proxy}'

    connector = ProxyConnector.from_url(
        url=proxy
    ) if proxy else None

    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        async with session.post(url=url, data=data, json=json, **kwargs) as response:
            status_code = response.status
            if response_type == "json":
                response = await response.json()
            elif response_type == "text":
                response = await response.text()
            if status_code <= 201:
                return response

            raise exceptions.HTTPException(response=response, status_code=status_code)

async def async_get(
        url: str,
        proxy: str | None = None,
        headers: dict | None = None,
        response_type: str = 'json',
        **kwargs
) -> dict | str | None:

    connector = ProxyConnector.from_url(
        url=proxy
    ) if proxy else None

    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        async with session.get(url=url, **kwargs) as response:
            status_code = response.status
            if response_type == "json":
                response = await response.json()
            elif response_type == "text":
                response = await response.text()
            if status_code <= 201:
                return response

            raise exceptions.HTTPException(response=response, status_code=status_code)

def api_key_required(func):
    """Check if the Blockscan API key is specified."""

    def func_wrapper(self, *args, **kwargs):
        if not self.client.network.api.key or not self.client.network.api.functions:
            raise exceptions.APIException('To use this function, you must specify the explorer API key!')

        else:
            return func(self, *args, **kwargs)

    return func_wrapper


