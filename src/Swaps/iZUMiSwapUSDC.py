import settings
import eth_abi
import math
import time
import src.networks as nt
import src.Swaps.tokens as tokens
import src.logger as logger
import src.ABIs as ABIs
import src.Helpers.txnHelper as txnHelper
import src.Helpers.helper as helper
import decimal


swap_contract_address = '0x032b241De86a8660f1Ae0691a4760B426EA246d7'

contract_swap = nt.linea_net.web3.eth.contract(nt.linea_net.web3.to_checksum_address(swap_contract_address),
                                               abi=ABIs.iZUMi_Swap_ABI)
pool_address = '0x0A3BB08b3a15A19b4De82F8AcFc862606FB69A2D'


def build_txn_swap_in(wallet, value_eth, price):
    try:
        contract = contract_swap
        slippage = settings.slippage_USDC
        gas_price_mult = helper.get_random_value(settings.gas_price_mult[0], settings.gas_price_mult[1], 3)
        gas_price = int(nt.linea_net.web3.eth.gas_price * gas_price_mult)

        value_wei = nt.linea_net.web3.to_wei(value_eth, 'ether')
        token_out_wei = int(float(value_eth) * price * (10 ** 6))
        min_output = int(token_out_wei * (1 - slippage))
        nonce = nt.linea_net.web3.eth.get_transaction_count(wallet.address)

        dict_transaction = {
            'chainId': nt.linea_net.chain_id,
            'from': wallet.address,
            'value': value_wei,
            'gas': 650000,
            'gasPrice': gas_price,
            'nonce': nonce,
        }

        deadline = math.ceil(time.time()) + 30 * 60
        usdc_address = tokens.USDC_token.address
        weth_address = tokens.wETH_token.address

        path_str = (weth_address.removeprefix('0x') + '0001f4' + #pool_address.removeprefix('0x') + '0001f4' +
                    usdc_address.removeprefix('0x'))
        path = bytes.fromhex(path_str)

        contract_code = eth_abi.encode(
            ['bytes', 'address',  'uint256', 'uint256', 'uint256'],
            [path, wallet.address, value_wei, min_output, deadline]
        )
        txn_code_hex = '75ceafe6' + '0000000000000000000000000000000000000000000000000000000000000020' + contract_code.hex()
        txn_code = bytes.fromhex(txn_code_hex)
        ref = bytes.fromhex('12210e8a')

        txn_swap = contract.functions.multicall(
            [txn_code, ref]
        ).build_transaction(dict_transaction)

        wallet.USDC_value += min_output / 10**6

        return txn_swap
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (iZUMiSwapUSDC: build_txn_swap_in) {ex.args}')


def build_txn_swap_out(wallet, value_token_wei, price):
    try:
        slippage = settings.slippage_USDC
        contract = contract_swap
        nonce = nt.linea_net.web3.eth.get_transaction_count(wallet.address)
        gas_price_mult = helper.get_random_value(settings.gas_price_mult[0], settings.gas_price_mult[1], 3)
        gas_price = int(nt.linea_net.web3.eth.gas_price * gas_price_mult)
        ether_out = value_token_wei / price / 10 ** 6
        min_output = int(nt.linea_net.web3.to_wei(ether_out * (1 - slippage), 'ether'))

        dict_transaction = {
            'chainId': nt.linea_net.chain_id,
            'from': wallet.address,
            'gas': 650000,
            'gasPrice': gas_price,
            'nonce': nonce,
        }

        zero_address = '0x0000000000000000000000000000000000000000'
        deadline = math.ceil(time.time()) + 20 * 60
        usdc_address = tokens.USDC_token.address
        weth_address = tokens.wETH_token.address

        path_str = (usdc_address.removeprefix('0x') + '0001f4' + #pool_address.removeprefix('0x') + '0001f4' +
                    weth_address.removeprefix('0x'))
        path = bytes.fromhex(path_str)

        contract_code = eth_abi.encode(
            ['bytes', 'address', 'uint256', 'uint256', 'uint256'],
            [path, zero_address, value_token_wei, min_output, deadline]
        )
        txn_code_hex = '75ceafe6' + '0000000000000000000000000000000000000000000000000000000000000020' + contract_code.hex()
        txn_code = bytes.fromhex(txn_code_hex)

        address_code = eth_abi.encode(['uint256', 'address'], [0, wallet.address])
        ref = bytes.fromhex('49404b7c' + address_code.hex())

        txn_swap = contract.functions.multicall(
            [txn_code, ref]
        ).build_transaction(dict_transaction)

        wallet.USDC_value += float(nt.linea_net.web3.from_wei(min_output, 'ether')) * price

        return txn_swap
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (iZUMiSwapUSDC: build_txn_swap_out) {ex.args}')


def swap_ETH_to_USDC(wallet, swap_value_eth, price, txn_num):
    try:
        key = wallet.key
        address = wallet.address
        script_time = helper.get_curr_time()

        logger.cs_logger.info(f'Свапаем {swap_value_eth} ETH через iZUMiSwap_USDC')
        balance_start_eth = nt.linea_net.web3.from_wei(nt.linea_net.web3.eth.get_balance(address), 'ether')
        balance_start_token = tokens.contract_USDC.functions.balanceOf(address).call() / 10 ** 6

        txn_swap = build_txn_swap_in(wallet, swap_value_eth, price)
        estimate_gas = txnHelper.check_estimate_gas(txn_swap, nt.linea_net)
        if type(estimate_gas) is str:
            logger.cs_logger.info(f'{estimate_gas}')
            return False
        else:
            txn_swap['gas'] = estimate_gas
            txn_hash, txn_status = txnHelper.exec_txn(key, txn_swap, nt.linea_net)
            logger.cs_logger.info(f'Hash: {txn_hash}')
            helper.delay_sleep(settings.swap_delay[0], settings.swap_delay[1])

            balance_end_eth = nt.linea_net.web3.from_wei(nt.linea_net.web3.eth.get_balance(address), 'ether')
            balance_end_token = tokens.contract_USDC.functions.balanceOf(address).call() / 10 ** 6

            log = logger.LogSwap(wallet.wallet_num, txn_num + 1, address, 'USDC', swap_value_eth,
                                 txn_hash, balance_start_eth, balance_end_eth, balance_start_token, balance_end_token)
            log.write_log(1, script_time)
            return True
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (iZUMiSwapUSDC: swap_ETH_to_USDC), {ex.args}')
        return False


def swap_USDC_to_ETH(wallet, value_token_wei, price, txn_num):
    try:
        key = wallet.key
        address = wallet.address
        script_time = helper.get_curr_time()
        if value_token_wei != 0:
            logger.cs_logger.info(f'Свапаем {value_token_wei / 10 ** 6} USDC через iZUMiSwap_USDC')
            balance_start_eth = nt.linea_net.web3.from_wei(nt.linea_net.web3.eth.get_balance(address), 'ether')
            balance_start_token = tokens.contract_USDC.functions.balanceOf(address).call() / 10 ** 6

            txnHelper.approve_amount(key, address, swap_contract_address, tokens.contract_USDC, nt.linea_net)
            txn_swap = build_txn_swap_out(wallet, value_token_wei, price)
            estimate_gas = txnHelper.check_estimate_gas(txn_swap, nt.linea_net)
            if type(estimate_gas) is str:
                logger.cs_logger.info(f'{estimate_gas}')
                return False
            else:
                txn_swap['gas'] = estimate_gas
                txn_hash, txn_status = txnHelper.exec_txn(key, txn_swap, nt.linea_net)
                logger.cs_logger.info(f'Hash: {txn_hash}')
                helper.delay_sleep(settings.swap_delay[0], settings.swap_delay[1])

                balance_end_eth = nt.linea_net.web3.from_wei(nt.linea_net.web3.eth.get_balance(address), 'ether')
                balance_end_token = tokens.contract_USDC.functions.balanceOf(address).call() / 10 ** 6
                log = logger.LogSwap(wallet.wallet_num, txn_num + 1, address, 'USDC',
                                     value_token_wei / 10 ** 6, txn_hash,
                                     balance_start_eth, balance_end_eth, balance_start_token, balance_end_token)
                log.write_log(2, script_time)
                return True
        else:
            logger.cs_logger.info(f'Баланс USDC равен 0')
            return True
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (iZUMiSwapUSDC: swap_USDC_to_ETH), {ex.args}')
        return False


def swapping(wallet, swap_balance_eth, price, txn_count):
    txns = wallet.txn_num
    dd = txn_count // 10
    swap_value_max = swap_balance_eth / txn_count

    for i in range(txn_count):
        if i == txn_count - 1:
            swap_value_eth = helper.trunc_value(
                swap_balance_eth,
                settings.swap_sum_digs[0] + 1 + dd,
                settings.swap_sum_digs[1] + 1 + dd)
        else:
            swap_value_eth = helper.trunc_value(
                decimal.Decimal(swap_value_max) * decimal.Decimal(helper.get_random_value(0.80, 0.98, 3)),
                settings.swap_sum_digs[0] + 1 + dd,
                settings.swap_sum_digs[1] + 1 + dd
            )
            swap_balance_eth -= swap_value_eth

        logger.cs_logger.info(f'Транзакция {i+1} из {txn_count}')
        status = swap_ETH_to_USDC(wallet, swap_value_eth, price, wallet.txn_num)
        if status is not True:
            break
        wallet.txn_num += 1

    #wallet.txn_num += txns
    return txns
