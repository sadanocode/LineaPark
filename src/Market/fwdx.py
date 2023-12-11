import settings as settings
from src.networks import linea_net
import eth_abi
from src.Swaps.tokens import USDC_token, wETH_token, contract_USDC
from src.Helpers.txnHelper import get_txn_dict, exec_txn, check_estimate_gas, approve_amount
import src.logger as logger
from src.Helpers.helper import get_curr_time, delay_sleep, get_random_value, trunc_value
from src.Swaps.swapHelper import get_usdc_balance
from random import randint
import datetime


contract_address = '0x5563E1dbA939db0E3041A423dC489976AABC2d6e'


def get_timeout():
    epoch = datetime.datetime(1970, 1, 1)
    day_now = datetime.date.today().day
    year_now = datetime.date.today().year
    month_now = datetime.date.today().month
    date = datetime.datetime(year_now, month_now, day_now + 1, 13, 0, 0)
    timeout_date = date - epoch
    return int(timeout_date.total_seconds())


def approve_usdc(wallet, token_amount):
    approve_amount(wallet.key, wallet.address, contract_address, contract_USDC, linea_net, token_amount, token_amount)


def build_txn_deposit(wallet, amount_token):
    try:
        txn = get_txn_dict(wallet.address, linea_net)
        txn['to'] = contract_address
        digs = randint(settings.weth_digs[0], settings.weth_digs[1])
        weth_amount = linea_net.web3.to_wei(get_random_value(settings.weth_volume[0], settings.weth_volume[1], digs), 'ether')
        timeout = get_timeout()
        method = '0xe578997d'
        data = eth_abi.encode(
            ['address', 'address', 'uint256', 'uint256', 'uint256', 'uint256'],
            [USDC_token.address, wETH_token.address, amount_token, weth_amount, timeout, 1]
        )
        txn_data = method + data.hex().removeprefix('0x')
        txn['data'] = txn_data
        return txn
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (fwdx: build_txn_deposit) {ex.args}')


def deposit(wallet):
    try:
        script_time = get_curr_time()
        token_balance = get_usdc_balance(wallet.address) / 10 ** 6
        token_amount_trunc = trunc_value(token_balance, 2, 2) - get_random_value(0.30, 0.95, 2)
        token_amount = int(token_amount_trunc * 10 ** 6)
        if token_amount == 0:
            logger.cs_logger.info(f'#   Баланс USDС равен 0')
            return True

        balance_start_usdc = token_amount_trunc
        logger.cs_logger.info(f'#   Делаем депозит {balance_start_usdc} USDC в FWDX')

        approve_usdc(wallet, token_amount)
        txn = build_txn_deposit(wallet, token_amount)
        estimate_gas = check_estimate_gas(txn, linea_net)

        if type(estimate_gas) is str:
            logger.cs_logger.info(f'{estimate_gas}')
            return False
        else:
            txn['gas'] = estimate_gas
            txn_hash, status = exec_txn(wallet.key, txn, linea_net)
            logger.cs_logger.info(f'Hash: {txn_hash}')

            wallet.txn_num += 1
            wallet.fwdx_value += balance_start_usdc
            delay_sleep(settings.txn_delay[0], settings.txn_delay[1])
            balance_end_usdc = get_usdc_balance(wallet.address) / 10 ** 6
            operation_value = f'- {trunc_value(balance_start_usdc, 2, 2)} USDC'
            log = logger.LogMarket(wallet.wallet_num, wallet.txn_num, wallet.address, 'FWDX deposit',
                                   operation_value, txn_hash, balance_start_usdc, balance_end_usdc)
            log.write_log(script_time)
        return True
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (fwdx: deposit) {ex.args}')
        return False
