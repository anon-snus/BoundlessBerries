import json

from libs.eth_async.models import RawContract, DefaultABIs
from libs.eth_async.utils.utils import read_json
from libs.eth_async.classes import Singleton

from config import ABIS_DIR

class Contracts(Singleton):
	BoundlessBerries = RawContract(
		title='BoundlessBerries',
		address= '0xa25e0AF7Dd580fcE7121FD78E95c3f3beE258e8f',
		abi=read_json(path=(ABIS_DIR, 'abi.json'))
	)