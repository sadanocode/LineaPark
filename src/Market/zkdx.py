import src.logger as logger
from src.Swaps.tokens import USDC_token, contract_ZUSD, contract_USDC
from src.Helpers.helper import get_curr_time, delay_sleep, trunc_value
from src.Swaps.swapHelper import get_usdc_balance
from src.Helpers.txnHelper import exec_txn, get_txn_dict, check_estimate_gas, approve_amount
import eth_abi
import settings
from src.networks import linea_net


contract_address = '0x3a85b87e81cD99D4A6670f95A4F0dEdAaC207Da0'


def approve_usdc(wallet, token_amount):
    approve_amount(wallet.key, wallet.address, contract_address, contract_USDC, linea_net, token_amount, token_amount)


def get_zusd_balance(address):
    zusd_balance = contract_ZUSD.functions.balanceOf(address).call()
    return zusd_balance


def build_txn_deposit(wallet, usdc_amount):
    try:
        txn = get_txn_dict(wallet.address, linea_net)
        txn['to'] = contract_address
        method = '0x045d0389'
        data = eth_abi.encode(
            ['address', 'uint256'],
            [USDC_token.address, usdc_amount]
        )
        txn_data = method + data.hex().removeprefix('0x')
        txn['data'] = txn_data
        return txn
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (zkdx: build_txn_deposit) {ex.args}')


def build_txn_redeem(wallet, zusd_amount):
    try:
        txn = get_txn_dict(wallet.address, linea_net)
        txn['to'] = contract_address
        method = '0x1e9a6950'
        data = eth_abi.encode(
            ['address', 'uint256'],
            [USDC_token.address, zusd_amount]
        )
        txn_data = method + data.hex().removeprefix('0x')
        txn['data'] = txn_data
        return txn
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (zkdx: build_txn_redeem) {ex.args}')


def deposit(wallet):
    try:
        script_time = get_curr_time()
        token_amount = get_usdc_balance(wallet.address)
        if token_amount == 0:
            logger.cs_logger.info(f'#   Баланс USDC равен 0')
            return True

        balance_start_usdc = token_amount / 10 ** 6
        logger.cs_logger.info(f'#   Меняем {balance_start_usdc} USDC на ZUSD в ZKDX')

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
            wallet.zkdx_value += balance_start_usdc
            delay_sleep(settings.txn_delay[0], settings.txn_delay[1])
            balance_end_usdc = get_usdc_balance(wallet.address) / 10 ** 6

            operation_value = f'- {trunc_value(balance_start_usdc,2,2)} USDC'
            log = logger.LogMarket(wallet.wallet_num, wallet.txn_num, wallet.address, 'ZKDX deposit',
                                   operation_value, txn_hash, balance_start_usdc, balance_end_usdc)
            log.write_log(script_time)
        return True
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (zkdx: deposit) {ex.args}')
        return False


def redeem(wallet):
    try:
        script_time = get_curr_time()

        token_amount = get_zusd_balance(wallet.address)
        if token_amount == 0:
            logger.cs_logger.info(f'#   Баланс ZUSD равен 0')
            return True
        balance_start_usdc = get_usdc_balance(wallet.address) / 10 ** 6
        balance_start_zusd = linea_net.web3.from_wei(token_amount, 'ether')
        logger.cs_logger.info(f'#   Меняем {balance_start_zusd} ZUSD на USDC в ZKDX')

        txn = build_txn_redeem(wallet, token_amount)
        estimate_gas = check_estimate_gas(txn, linea_net)

        if type(estimate_gas) is str:
            logger.cs_logger.info(f'{estimate_gas}')
            return False
        else:
            txn['gas'] = estimate_gas
            txn_hash, status = exec_txn(wallet.key, txn, linea_net)
            logger.cs_logger.info(f'Hash: {txn_hash}')

            wallet.txn_num += 1
            delay_sleep(settings.txn_delay[0], settings.txn_delay[1])
            balance_end_usdc = get_usdc_balance(wallet.address) / 10 ** 6
            operation_value = f'- {trunc_value(balance_start_zusd, 2, 2)} ZUSD'
            log = logger.LogMarket(wallet.wallet_num, wallet.txn_num, wallet.address,'ZKDX redeem',
                                   operation_value, txn_hash, balance_start_usdc, balance_end_usdc)
            log.write_log(script_time)
        return True
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (zkdx: redeem) {ex.args}')
        return False
