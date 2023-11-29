from src.Swaps.tokens import Token
from src.networks import linea_net
from src.ABIs import LineaBank_Token_ABI


lUSDC_token = Token(
    token_name='lUSDC',
    token_address='0x2aD69A0Cf272B9941c7dDcaDa7B0273E9046C4B0'
)
contract_lUSDC = linea_net.web3.eth.contract(linea_net.web3.to_checksum_address(lUSDC_token.address),
                                             abi=LineaBank_Token_ABI)

lETH_token = Token(
    token_name='lETH',
    token_address='0xc7D8489DaE3D2EbEF075b1dB2257E2c231C9D231'
)
contract_lETH = linea_net.web3.eth.contract(linea_net.web3.to_checksum_address(lETH_token.address),
                                            abi=LineaBank_Token_ABI)

lwstETH_token = Token(
    token_name='lwstETH',
    token_address='0xE33520c74bac3c537BfEEe0F65e80471F3d564b9'
)
contract_lwstETH = linea_net.web3.eth.contract(linea_net.web3.to_checksum_address(lwstETH_token.address),
                                               abi=LineaBank_Token_ABI)
