from libs.eth_async.client import Client
from libs.eth_async.utils.utils import async_post
from libs.eth_async.contracts import Contracts
from libs.eth_async.models import TokenAmount, TxArgs
import asyncio
from data.models import Contracts
from web3.types import TxParams

class Base:
	def __init__(self, client: Client):
		self.client = client



	async def get_signature(self):
		url = 'https://berry.beboundless.xyz/signed-message'
		json_data = {
			'address': str(self.client.account.address)
		}
		for i in range(3):
			try:
				signature = await async_post(url=url, json=json_data, proxy=self.client.proxy)
				sig = signature.get('signature')
				timestamp = signature.get('timestamp')
				return (sig, timestamp)
			except Exception as e:
				print(e)
				i+=1
				await asyncio.sleep(1)
		print(f'Failed to get signature for {self.recipient}')
		return None

	async def mint_nft(self, signature:str|None = None ):
		if signature is None:
			signature = await self.get_signature()
		contract = await self.client.contracts.get(contract_address=Contracts.BoundlessBerries)
		args = TxArgs(_recipient=self.client.account.address, _signature=signature[0], _timestamp=signature[1])
		tx_params = TxParams(
			to=contract.address, data=contract.encodeABI('mintTo', args=args.tuple()), value=0
		)
		try:
			tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
			receipt = await tx.wait_for_receipt(client=self.client, timeout=500)
			if receipt:
				return f'mint for {self.client.account.address} is successful, hash: {tx.hash.hex()}, '
			return f'tx {self.client.account.address} failed'
		except Exception as e:
			print(e)
			return f'mint for {self.client.account.address} is failed'


