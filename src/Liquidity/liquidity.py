import eth_abi
from src.networks import linea_net
import src.logger as logger
from src.Helpers.txnHelper import exec_txn, get_txn_dict, check_estimate_gas
from src.Helpers.helper import delay_sleep, get_curr_time, get_price, trunc_value
import settings as settings
from src.ABIs import Lens
from random import randint
from src.Helpers.gasPriceChecker import check_limit


POOL_ADDRESS = '0x1d0188c4B276A09366D05d6Be06aF61a73bC7535'
max_f = 0xffffffffffffffffffffffffffffffff
Lens_contract = linea_net.web3.eth.contract(address='0xaA18cDb16a4DD88a59f4c2f45b5c91d009549e06',
                                            abi=Lens)


def get_token_balance(address):
    gauge = Lens_contract.functions.queryGauge(
        linea_net.web3.to_checksum_address('0xE0c6FDf4EFC676EB35EA094f2B01Af216F9C232c'),
        address
    ).call()
    balance = gauge[-2]
    return balance[0]


def build_txn_liq_deposit(wallet, amount, min_output):
    try:
        txn = get_txn_dict(wallet.address, linea_net, amount)
        txn['to'] = POOL_ADDRESS
        txn['data'] = ''
        amount_byte = eth_abi.encode(['uint256'], [amount]).hex()
        amount_data = amount_byte.replace(amount_byte[0:2], '03', 1)
        amount_f = max_f - amount + 1
        min_output_f = max_f - min_output + 1

        txn_data = (
            '0xd3115a8a'
            '0000000000000000000000000000000000000000000000000000000000000060'
            '0000000000000000000000000000000000000000000000000000000000000100'
            '00000000000000000000000000000000000000000000000000000000000001a0'
            '0000000000000000000000000000000000000000000000000000000000000004'
            '000000000000000000000000b30e7a2e6f7389ca5ddc714da4c991b7a1dcc88e'
            '000000000000000000000000cc22f6aa610d1b2a0e89ef228079cb3e1831b1d1'
            '0200000000000000000000021d312eedd57e8d43bcb6369e4b8f02d3c18aaf13'
            'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
            '0000000000000000000000000000000000000000000000000000000000000004'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000000000000000000000000000000000000000000006'
            '00000000000000000000000000000000000000000000000000000000000000c0'
            '00000000000000000000000000000000000000000000000000000000000001a0'
            '0000000000000000000000000000000000000000000000000000000000000280'
            '0000000000000000000000000000000000000000000000000000000000000380'
            '0000000000000000000000000000000000000000000000000000000000000480'
            '0000000000000000000000000000000000000000000000000000000000000560'
            '040000000000000000000000' + wallet.address.removeprefix('0x') +
            '0000000000000000000000000000000000000000000000000000000000000060'
            '00000000000000000000000000000000000000000000000000000000000000a0'
            '0000000000000000000000000000000000000000000000000000000000000001'
            + amount_data +
            '0000000000000000000000000000000000000000000000000000000000000001'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '040000000000000000000000' + wallet.address.removeprefix('0x') +
            '0000000000000000000000000000000000000000000000000000000000000060'
            '00000000000000000000000000000000000000000000000000000000000000a0'
            '0000000000000000000000000000000000000000000000000000000000000001'
            '03000000000000000000000000000000' + hex(amount_f).removeprefix('0x') +
            '0000000000000000000000000000000000000000000000000000000000000001'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000002bd146e7d95cea62c89fcca8e529e06eec1b053c'
            '0000000000000000000000000000000000000000000000000000000000000060'
            '00000000000000000000000000000000000000000000000000000000000000c0'
            '0000000000000000000000000000000000000000000000000000000000000002'
            '000100000000000000000000000000007fffffffffffffffffffffffffffffff'
            '030200000000000000000000000000007fffffffffffffffffffffffffffffff'
            '0000000000000000000000000000000000000000000000000000000000000001'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000001d312eedd57e8d43bcb6369e4b8f02d3c18aaf13'
            '0000000000000000000000000000000000000000000000000000000000000060'
            '00000000000000000000000000000000000000000000000000000000000000c0'
            '0000000000000000000000000000000000000000000000000000000000000002'
            '000200000000000000000000000000007fffffffffffffffffffffffffffffff'
            '020100000000000000000000000000007fffffffffffffffffffffffffffffff'
            '0000000000000000000000000000000000000000000000000000000000000001'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0500000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000000000000000000000000000000000000000000060'
            '00000000000000000000000000000000000000000000000000000000000000a0'
            '0000000000000000000000000000000000000000000000000000000000000001'
            '02010000000000000000000000000000' + hex(min_output_f).removeprefix('0x') +
            '0000000000000000000000000000000000000000000000000000000000000001'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '010000000000000000000000e0c6fdf4efc676eb35ea094f2b01af216f9c232c'
            '0000000000000000000000000000000000000000000000000000000000000060'
            '00000000000000000000000000000000000000000000000000000000000000c0'
            '0000000000000000000000000000000000000000000000000000000000000002'
            '0101000000000000000000000000000000000000000000000000000000000000'
            '020200000000000000000000000000007fffffffffffffffffffffffffffffff'
            '0000000000000000000000000000000000000000000000000000000000000001'
            '0000000000000000000000000000000000000000000000000000000000000000'
        )
        txn['data'] = txn_data
        return txn
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (liquidity: build_txn_liq_deposit) {ex.args}')


def build_txn_liq_withdraw(wallet, token_amount, min_output):
    try:
        txn = get_txn_dict(wallet.address, linea_net)
        txn['to'] = POOL_ADDRESS
        token_amount_f = max_f - token_amount
        min_output_f = max_f - min_output + 1

        txn_data = (
            '0xd3115a8a'
            '0000000000000000000000000000000000000000000000000000000000000060'
            '0000000000000000000000000000000000000000000000000000000000000100'
            '00000000000000000000000000000000000000000000000000000000000001a0'
            '0000000000000000000000000000000000000000000000000000000000000004'
            '000000000000000000000000b30e7a2e6f7389ca5ddc714da4c991b7a1dcc88e'
            '000000000000000000000000cc22f6aa610d1b2a0e89ef228079cb3e1831b1d1'
            '0200000000000000000000021d312eedd57e8d43bcb6369e4b8f02d3c18aaf13'
            'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
            '0000000000000000000000000000000000000000000000000000000000000004'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000000000000000000000000000000000000000000004'
            '0000000000000000000000000000000000000000000000000000000000000080'
            '0000000000000000000000000000000000000000000000000000000000000180'
            '0000000000000000000000000000000000000000000000000000000000000280'
            '0000000000000000000000000000000000000000000000000000000000000380'
            '010000000000000000000000e0c6fdf4efc676eb35ea094f2b01af216f9c232c'
            '0000000000000000000000000000000000000000000000000000000000000060'
            '00000000000000000000000000000000000000000000000000000000000000c0'
            '0000000000000000000000000000000000000000000000000000000000000002'
            '0101000000000000000000000000000000000000000000000000000000000000'
            '02000000000000000000000000000000' + hex(token_amount_f).removeprefix('0x') +
            '0000000000000000000000000000000000000000000000000000000000000001'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000001d312eedd57e8d43bcb6369e4b8f02d3c18aaf13'
            '0000000000000000000000000000000000000000000000000000000000000060'
            '00000000000000000000000000000000000000000000000000000000000000c0'
            '0000000000000000000000000000000000000000000000000000000000000002'
            '000100000000000000000000000000007fffffffffffffffffffffffffffffff'
            '020200000000000000000000000000007fffffffffffffffffffffffffffffff'
            '0000000000000000000000000000000000000000000000000000000000000001'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000002bd146e7d95cea62c89fcca8e529e06eec1b053c'
            '0000000000000000000000000000000000000000000000000000000000000060'
            '00000000000000000000000000000000000000000000000000000000000000c0'
            '0000000000000000000000000000000000000000000000000000000000000002'
            '000200000000000000000000000000007fffffffffffffffffffffffffffffff'
            '030100000000000000000000000000007fffffffffffffffffffffffffffffff'
            '0000000000000000000000000000000000000000000000000000000000000001'
            '0000000000000000000000000000000000000000000000000000000000000000'
            '0500000000000000000000000000000000000000000000000000000000000000'
            '0000000000000000000000000000000000000000000000000000000000000060'
            '00000000000000000000000000000000000000000000000000000000000000a0'
            '0000000000000000000000000000000000000000000000000000000000000001'
            '03010000000000000000000000000000' + hex(min_output_f).removeprefix('0x') +
            '0000000000000000000000000000000000000000000000000000000000000001'
            '0000000000000000000000000000000000000000000000000000000000000000'
        )
        txn['data'] = txn_data
        return txn
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (liquidity: build_txn_liq_withdraw) {ex.args}')


def liq_deposit(wallet, amount_eth, slippage):
    try:
        check_limit()
        script_time = get_curr_time()
        balance_start = linea_net.web3.from_wei(linea_net.web3.eth.get_balance(wallet.address), 'ether')

        logger.cs_logger.info(f'#   Добавляем ликвидность {amount_eth} ETH | slippage = {slippage * 100.0} %')
        amount = linea_net.web3.to_wei(amount_eth, 'ether')
        price = get_price('ETH')
        output = int((float(linea_net.web3.from_wei(amount, 'ether')) * price) * 10 ** 6)
        min_output = int(output * (1 - slippage))

        txn = build_txn_liq_deposit(wallet, amount, min_output)
        estimate_gas = check_estimate_gas(txn, linea_net)

        if type(estimate_gas) is str:
            logger.cs_logger.info(f'{estimate_gas}')
            return False
        else:
            txn['gas'] = estimate_gas
            txn_hash, status = exec_txn(wallet.key, txn, linea_net)
            logger.cs_logger.info(f'Hash: {txn_hash}')

            wallet.txn_num += 1
            wallet.deposit_value = float(amount_eth) * price
            delay_sleep(settings.txn_delay[0], settings.txn_delay[1])
            balance_end = linea_net.web3.from_wei(linea_net.web3.eth.get_balance(wallet.address), 'ether')

            log = logger.LogLiq(wallet.wallet_num, wallet.address, amount_eth, '-', txn_hash,
                                balance_start, balance_end)
            log.write_log(script_time)
        return True
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (liquidity: liq_deposit) {ex.args}')
        return False


def liq_withdraw(wallet, token_amount, slippage):
    try:
        check_limit()
        script_time = get_curr_time()
        balance_start = linea_net.web3.from_wei(linea_net.web3.eth.get_balance(wallet.address), 'ether')

        price = get_price('ETH')
        output_eth = token_amount / (price * 10 ** 6)
        output = linea_net.web3.to_wei(output_eth, 'ether')
        min_output = int(output * (1 - slippage))
        min_output_eth = linea_net.web3.from_wei(min_output, "ether")

        logger.cs_logger.info(f'#   Выводим ликвидность {min_output_eth} ETH | slippage = {slippage * 100.0} %')
        txn = build_txn_liq_withdraw(wallet, token_amount, min_output)
        estimate_gas = check_estimate_gas(txn, linea_net)
        if type(estimate_gas) is str:
            logger.cs_logger.info(f'{estimate_gas}')
            return False
        else:
            txn['gas'] = estimate_gas
            txn_hash, status = exec_txn(wallet.key, txn, linea_net)
            logger.cs_logger.info(f'Hash: {txn_hash}')

            wallet.txn_num += 1
            wallet.withdraw_value = token_amount / 10 ** 6
            delay_sleep(settings.txn_delay[0], settings.txn_delay[1])

            balance_end = linea_net.web3.from_wei(linea_net.web3.eth.get_balance(wallet.address), 'ether')

            log = logger.LogLiq(wallet.wallet_num, wallet.address, '-', min_output_eth, txn_hash,
                                balance_start, balance_end,)
            log.write_log(script_time)
        return True
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (liquidity: liq_withdraw) {ex.args}')
        return False


def get_eth_sum():
    price = get_price('ETH')
    usd_volume = randint(settings.liq_volume[0], settings.liq_volume[1])
    eth_sum = trunc_value(usd_volume/price, settings.liq_digs[0], settings.liq_digs[1])
    return eth_sum


def liq_ops(wallet):
    amount_eth = get_eth_sum()

    dep_status = False
    if settings.liq_deposit_swith == 0:
        dep_status = True

    wit_status = False
    if settings.liq_withdraw_switch == 0:
        wit_status = True

    slippage_dep = settings.deposit_slippage
    attempt = 0
    while dep_status is False:
        dep_status = liq_deposit(wallet, amount_eth, slippage_dep)
        if dep_status is False:
            delay_sleep(settings.try_delay[0], settings.try_delay[1])
            attempt += 1
            logger.cs_logger.info(f'Делаем доп попытку № {attempt}')
            if attempt % 2 == 0 and slippage_dep < settings.deposit_slippage_max:
                slippage_dep += 0.005

    if dep_status is True:
        attempt = 0
        slippage_wth = settings.withdraw_slippage
        while wit_status is False:
            token_amount = get_token_balance(wallet.address) #- 1000
            if token_amount <= 1000:
                logger.cs_logger.info(f'Баланс ликвидности слишком мал для вывода: {token_amount / 10 ** 6} USDT')
                break
            wit_status = liq_withdraw(wallet, token_amount, slippage_wth)
            if wit_status is False:
                delay_sleep(settings.try_delay[0], settings.try_delay[1])
                attempt += 1
                logger.cs_logger.info(f'Делаем доп попытку № {attempt}')
                if attempt % 2 == 0 and slippage_wth < settings.withdraw_slippage_max:
                    slippage_wth += 0.005
