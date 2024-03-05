import settings
from random import randint
from src.Helpers.helper import get_price, trunc_value
from src.Swaps.tokens import contract_USDC


def get_txn_count(txns_count):
    txn_count = randint(txns_count[0], txns_count[1])  # Рандомим количество транзакций
    return txn_count


def get_eth_value(usdc_volume):
    usdc_value = randint(usdc_volume[0], usdc_volume[1])
    price = get_price('ETH')
    eth_value = usdc_value / price
    eth_value_trunc = trunc_value(eth_value, settings.eth_volume_digs[0], settings.eth_volume_digs[1])
    return eth_value_trunc


def get_usdc_balance(address):
    usdc_balance = contract_USDC.functions.balanceOf(address).call()
    return usdc_balance
