import settings
import random
import src.Helpers.helper as helper
import src.networks as nt


def get_txn_count(txns_count):
    txn_count = random.randint(txns_count[0], txns_count[1])  # Рандомим количество транзакций
    return txn_count


def get_open_balance(net, address, balance_percents):
    percent = helper.get_random_value(balance_percents[0], balance_percents[1], 3)
    balance = net.web3.eth.get_balance(address)
    balance_perc = nt.linea_net.web3.from_wei(int(balance * percent), 'ether')
    open_balance = helper.trunc_value(balance_perc, settings.swap_sum_digs[0], settings.swap_sum_digs[1])
    return open_balance
