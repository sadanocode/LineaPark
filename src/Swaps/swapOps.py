import random
import src.logger as logger
import src.Swaps.iZUMiSwap_wstETH as iZUMi_wstETH
import settings as settings
import src.Helpers.helper as helper
import src.Swaps.tokens as tokens
import src.Swaps.swapHelper as swapHelper


def wstETH_swaps(wallet):
    txn_count = swapHelper.get_txn_count(settings.wstETH_txn_count)

    price_wstETH = helper.get_price_wstETH('wstETH')
    price_ETH = helper.get_price('ETH')
    wstETH_volume = random.randint(settings.wstETH_volume[0], settings.wstETH_volume[1])
    logger.cs_logger.info(f'Свапаем эфир на {wstETH_volume} $ wstETH - транзакций: {txn_count}')
    swap_balance_eth = helper.trunc_value(wstETH_volume / price_ETH, 4, 6)
    iZUMi_wstETH.swapping(wallet, swap_balance_eth, price_wstETH, txn_count)


def wstETH_sell(wallet):
    price_wstETH = helper.get_price_wstETH('wstETH')
    value_token_wei = tokens.contract_wstETH.functions.balanceOf(wallet.address).call()
    iZUMi_wstETH.swap_wstETH_to_ETH(wallet, value_token_wei, price_wstETH, wallet.txn_num)
    wallet.txn_num += 1
