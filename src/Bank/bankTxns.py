import settings as settings
import src.Swaps.tokens as tokens
import src.Bank.gTokens as gTokens
from src.networks import linea_net
from src.ABIs import Bank_ABI
import src.Helpers.helper as helper
import src.logger as logger
from src.Helpers.txnHelper import get_txn_dict, check_estimate_gas, exec_txn, approve_amount


bank_contract_address = '0x009a0b7C38B542208936F1179151CD08E2943833'
contract = linea_net.web3.eth.contract(linea_net.web3.to_checksum_address(bank_contract_address),
                                       abi=Bank_ABI)


def get_borrow_balance(address, l_contract):
    borrow_balance = l_contract.functions.borrowBalanceOf(address).call()
    return borrow_balance


def get_account_liq(address):
    liq = contract.functions.accountLiquidityOf(address).call()
    return liq[0]


def approve_usdc(wallet, token_amount):
    approve_amount(wallet.key, wallet.address, gTokens.lUSDC_token.address, tokens.contract_USDC, linea_net, token_amount)


def approve_wsteth(wallet, token_amount):
    approve_amount(wallet.key, wallet.address, gTokens.lwstETH_token.address, tokens.contract_wstETH, linea_net, token_amount)
    wallet.txn_num += 1


def build_txn_enter_markets(wallet, g_token):
    try:
        dict_transaction = get_txn_dict(wallet.address, linea_net)

        txn = contract.functions.enterMarkets(
            [g_token.address]
        ).build_transaction(dict_transaction)

        return txn
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (bankTxns: build_txn_enter_markets) {ex.args}')


def build_txn_supply(wallet, g_token, token_amount):
    try:
        dict_transaction = get_txn_dict(wallet.address, linea_net)

        txn = contract.functions.supply(
            g_token.address, token_amount
        ).build_transaction(dict_transaction)

        return txn
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (bankTxns: build_txn_supply) {ex.args}')


def build_txn_borrow(wallet, g_token, token_amount):
    try:
        dict_transaction = get_txn_dict(wallet.address, linea_net)

        txn = contract.functions.borrow(
            g_token.address, token_amount
        ).build_transaction(dict_transaction)

        return txn
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (bankTxns: build_txn_borrow) {ex.args}')


def build_txn_repay_borrow(wallet, g_token, token_amount):
    try:
        dict_transaction = get_txn_dict(wallet.address, linea_net, token_amount)

        txn = contract.functions.repayBorrow(
            g_token.address, token_amount
        ).build_transaction(dict_transaction)

        return txn
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (bankTxns: build_txn_repay_borrow) {ex.args}')


def build_txn_redeem_token(wallet, g_token, token_amount):
    try:
        dict_transaction = get_txn_dict(wallet.address, linea_net)

        txn = contract.functions.redeemToken(
            g_token.address, token_amount
        ).build_transaction(dict_transaction)

        return txn
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (bankTxns: build_txn_redeem_token) {ex.args}')


def enter_markets(wallet, g_token):
    try:
        logger.cs_logger.info(f'#   Делаем транзакцию enterMarkets')
        txn = build_txn_enter_markets(wallet, g_token)
        estimate_gas = check_estimate_gas(txn, linea_net)

        if type(estimate_gas) is str:
            logger.cs_logger.info(f'{estimate_gas}')
            return False
        else:
            txn['gas'] = estimate_gas
            txn_hash, status = exec_txn(wallet.key, txn, linea_net)
            logger.cs_logger.info(f'Hash: {txn_hash}')

            wallet.txn_num += 1
            helper.delay_sleep(settings.txn_delay[0], settings.txn_delay[1])

        return True
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (bankTxns: enter_markets) {ex.args}')
        return False


def supply_wsteth(wallet):
    try:
        token_amount = tokens.contract_wstETH.functions.balanceOf(wallet.address).call()
        token_amount_eth = linea_net.web3.from_wei(token_amount, 'ether')
        logger.cs_logger.info(f'#   Делаем supply {token_amount_eth} wstETH')
        txn = build_txn_supply(wallet, gTokens.lwstETH_token, token_amount)
        estimate_gas = check_estimate_gas(txn, linea_net)

        if type(estimate_gas) is str:
            logger.cs_logger.info(f'{estimate_gas}')
            return False
        else:
            txn['gas'] = estimate_gas
            txn_hash, status = exec_txn(wallet.key, txn, linea_net)
            logger.cs_logger.info(f'Hash: {txn_hash}')

            wallet.txn_num += 1
            helper.delay_sleep(settings.txn_delay[0], settings.txn_delay[1])

        return True
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (bankTxns: supply_wsteth) {ex.args}')
        return False


def borrow_eth(wallet):
    try:
        script_time = helper.get_curr_time()
        balance_start_eth = linea_net.web3.from_wei(linea_net.web3.eth.get_balance(wallet.address), 'ether')

        liq_usd = linea_net.web3.from_wei(get_account_liq(wallet.address), 'ether')
        eth_price = helper.get_price('ETH')
        token_mult = helper.get_random_value(settings.borrow_mult[0], settings.borrow_mult[1], 3)
        token_amount_eth = helper.trunc_value((float(liq_usd) / eth_price) * token_mult,
                                              settings.borrow_digs[0], settings.borrow_digs[1])

        logger.cs_logger.info(f'#   Делаем borrow {token_amount_eth} ETH')
        token_amount = linea_net.web3.to_wei(token_amount_eth, 'ether')

        txn = build_txn_borrow(wallet, gTokens.lETH_token, token_amount)
        estimate_gas = check_estimate_gas(txn, linea_net)

        if type(estimate_gas) is str:
            logger.cs_logger.info(f'{estimate_gas}')
            return False
        else:
            txn['gas'] = estimate_gas
            txn_hash, status = exec_txn(wallet.key, txn, linea_net)

            logger.cs_logger.info(f'Hash: {txn_hash}')

            wallet.txn_num += 1
            balance_end_eth = linea_net.web3.from_wei(linea_net.web3.eth.get_balance(wallet.address), 'ether')

            borrow_value = token_amount_eth * eth_price
            wallet.borrow_value += borrow_value

            log = logger.LogBank(wallet.wallet_num, wallet.address, borrow_value, '---', txn_hash,
                                 balance_start_eth, balance_end_eth)
            log.write_log(script_time)

            helper.delay_sleep(settings.txn_delay[0], settings.txn_delay[1])

        return True
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (bankTxns: borrow_eth) {ex.args}')
        return False


def repay_borrow_token(wallet, g_token, token, l_contract):
    try:
        script_time = helper.get_curr_time()
        balance_start_eth = linea_net.web3.from_wei(linea_net.web3.eth.get_balance(wallet.address), 'ether')

        token_amount = int(get_borrow_balance(wallet.address, l_contract) * 1.01)
        token_amount_eth = linea_net.web3.from_wei(token_amount, 'ether')
        logger.cs_logger.info(f'#   Делаем repayBorrow {token_amount_eth} {token}')

        txn = build_txn_repay_borrow(wallet, g_token, token_amount)
        estimate_gas = check_estimate_gas(txn, linea_net)

        if type(estimate_gas) is str:
            logger.cs_logger.info(f'{estimate_gas}')
            return False
        else:
            txn['gas'] = estimate_gas
            txn_hash, status = exec_txn(wallet.key, txn, linea_net)

            logger.cs_logger.info(f'Hash: {txn_hash}')

            wallet.txn_num += 1
            balance_end_eth = linea_net.web3.from_wei(linea_net.web3.eth.get_balance(wallet.address), 'ether')

            eth_price = helper.get_price('ETH')
            repay_value = float(token_amount_eth) * eth_price

            wallet.repay_value += repay_value
            log = logger.LogBank(wallet.wallet_num, wallet.address, '---', repay_value, txn_hash,
                                 balance_start_eth, balance_end_eth)
            log.write_log(script_time)
            helper.delay_sleep(settings.txn_delay[0], settings.txn_delay[1])

        return True
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (bankTxns: repay_borrow_token) {ex.args}')
        return False


def redeem_wsteth(wallet):
    try:
        logger.cs_logger.info(f'#   Делаем redeemToken wstETH')
        token_amount = gTokens.contract_lwstETH.functions.balanceOf(wallet.address).call()

        txn = build_txn_redeem_token(wallet, gTokens.lwstETH_token, token_amount)
        estimate_gas = check_estimate_gas(txn, linea_net)

        if type(estimate_gas) is str:
            logger.cs_logger.info(f'{estimate_gas}')
            return False
        else:
            txn['gas'] = estimate_gas
            txn_hash, status = exec_txn(wallet.key, txn, linea_net)
            logger.cs_logger.info(f'Hash: {txn_hash}')

            wallet.txn_num += 1
            helper.delay_sleep(settings.txn_delay[0], settings.txn_delay[1])

        return True
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (bankTxns: redeem_wsteth) {ex.args}')
        return False


def bank_eth_wsteth(wallet):
    enter_markets(wallet, gTokens.lwstETH_token)

    token_approve = tokens.contract_wstETH.functions.balanceOf(wallet.address).call()
    approve_wsteth(wallet, token_approve)

    supply_wsteth(wallet)

    borrow_eth(wallet)

    repay_borrow_token(wallet, gTokens.lETH_token, 'ETH', gTokens.contract_lETH)

    redeem_wsteth(wallet)
