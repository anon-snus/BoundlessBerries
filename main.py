from config import delay, base_rpc
from random import randint
from tasks.base import Base
import asyncio
from libs.eth_async.client import Client
from libs.eth_async.models import Networks, TokenAmount

with open('data/privatekeys.txt') as f:
	keys = f.read().splitlines()
with open('data/proxies.txt') as f:
	proxies = f.read().splitlines()

async def main():
	if base_rpc:
		Networks.Base.rpc = base_rpc
	for key in keys:
		client = Client(private_key=key, network=Networks.Base)
		base = Base(client=client)
		a = await base.mint_nft()
		print(a)
		sleep = randint(delay['from'], delay['to'])
		print(f'Sleeping {sleep}')
		await asyncio.sleep(sleep)


if __name__ == '__main__':
	asyncio.run(main())
