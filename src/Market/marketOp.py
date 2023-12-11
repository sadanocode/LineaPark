import settings as settings
from src.Swaps.swapHelper import get_eth_value, get_usdc_balance
from src.Swaps.iZUMiSwapUSDC import swap_usdc_to_eth, swap_eth_to_usdc
from src.Helpers.gasPriceChecker import check_limit
from src.logger import cs_logger, rewrite_overall
from src.Market.zkdx import deposit as zkdx_deposit, redeem as zkdx_redeem
from src.Market.fwdx import deposit as fwdx_deposit
from src.networks import linea_net
from src.Helpers.helper import delay_sleep


def rewrite_ov(wallet):
    balance_end = linea_net.web3.from_wei(linea_net.web3.eth.get_balance(wallet.address), 'ether')
    nonce = linea_net.web3.eth.get_transaction_count(wallet.address)
    rewrite_overall(wallet, balance_end, nonce)


def market_ops(wallet):
    txn_status1 = False
    txn_status2 = False
    txn_status3 = False
    txn_status4 = False
    txn_status5 = False

    swap_value_eth = get_eth_value()

    if settings.eth_swap_switch == 1:
        while txn_status1 is False:
            check_limit()
            attempt = 1
            txn_status1 = swap_eth_to_usdc(wallet, swap_value_eth)
            if txn_status1 is False:
                attempt += 1
                delay_sleep(settings.try_delay[0], settings.try_delay[1])
                cs_logger.info(f'Делаем доп попытку № {attempt}')

        rewrite_ov(wallet)

    if settings.zkdx_switch == 1:
        while txn_status2 is False:
            check_limit()
            attempt = 1
            txn_status2 = zkdx_deposit(wallet)
            if txn_status2 is False:
                attempt += 1
                delay_sleep(settings.try_delay[0], settings.try_delay[1])
                cs_logger.info(f'Делаем доп попытку № {attempt}')

        rewrite_ov(wallet)

        while txn_status3 is False:
            check_limit()
            attempt = 1
            txn_status3 = zkdx_redeem(wallet)
            if txn_status3 is False:
                attempt += 1
                delay_sleep(settings.try_delay[0], settings.try_delay[1])
                cs_logger.info(f'Делаем доп попытку № {attempt}')

        rewrite_ov(wallet)

    if settings.fwdx_swith == 1:
        while txn_status4 is False:
            check_limit()
            attempt = 1
            txn_status4 = fwdx_deposit(wallet)
            if txn_status4 is False:
                attempt += 1
                delay_sleep(settings.try_delay[0], settings.try_delay[1])
                cs_logger.info(f'Делаем доп попытку № {attempt}')

        rewrite_ov(wallet)

    if settings.usdc_swap_switch == 1:
        token_value = get_usdc_balance(wallet.address)
        if token_value != 0:
            while txn_status5 is False:
                check_limit()
                attempt = 1
                txn_status5 = swap_usdc_to_eth(wallet, token_value)
                if txn_status5 is False:
                    attempt += 1
                    delay_sleep(settings.try_delay[0], settings.try_delay[1])
                    cs_logger.info(f'Делаем доп попытку № {attempt}')

            rewrite_ov(wallet)
