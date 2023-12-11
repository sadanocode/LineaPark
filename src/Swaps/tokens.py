import settings
import src.networks as nt
from src.ABIs import ERC20_ABI
from web3 import Web3


class Token(object):
    def __init__(self, token_name, token_address):
        self.name = token_name
        self.address = token_address


linea_net = nt.linea_net

USDC_token = Token(
    'USDC',
    '0x176211869cA2b568f2A7D4EE941E073a821EE1ff'
)
contract_USDC = linea_net.web3.eth.contract(Web3.to_checksum_address(USDC_token.address), abi=ERC20_ABI)

wETH_token = Token(
    'wETH',
    '0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f'
)
contract_wETH = linea_net.web3.eth.contract(Web3.to_checksum_address(wETH_token.address), abi=ERC20_ABI)

ZUSD_token = Token(
    'ZUSD',
    '0x2167C4D5FE05A1250588F0B8AA83A599e7732eae'
)
contract_ZUSD = linea_net.web3.eth.contract(Web3.to_checksum_address(ZUSD_token.address), abi=ERC20_ABI)
