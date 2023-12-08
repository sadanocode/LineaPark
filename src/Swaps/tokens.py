import settings
import src.networks as nt
import src.ABIs as ABIs
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
contract_USDC = linea_net.web3.eth.contract(Web3.to_checksum_address(USDC_token.address), abi=ABIs.ERC20_ABI)
