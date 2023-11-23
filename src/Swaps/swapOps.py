import random
import src.logger as logger
import src.Swaps.iZUMiSwapUSDC as iZUMiUSDC
import src.Swaps.iZUMiSwap_wstETH as iZUMi_wstETH
import settings as settings
import src.Helpers.helper as helper
import src.Swaps.tokens as tokens
import src.Swaps.swapHelper as swapHelper


def USDC_swaps(wallet):
    txn_count = swapHelper.get_txn_count(settings.USDC_txn_count)
    logger.cs_logger.info(f'Свапы USDC - транзакций: {txn_count}')

    price = helper.get_price('ETH')
    USDC_volume = random.randint(settings.USDC_volume[0], settings.USDC_volume[1])
    swap_balance_eth = helper.trunc_value(USDC_volume/price, 4, 6)
    iZUMiUSDC.swapping(wallet, swap_balance_eth, price, txn_count)

    value_token_wei = tokens.contract_USDC.functions.balanceOf(wallet.address).call()
    iZUMiUSDC.swap_USDC_to_ETH(wallet, value_token_wei, price, wallet.txn_num)
    wallet.txn_num += 1


def wstETH_swaps(wallet):
    txn_count = swapHelper.get_txn_count(settings.wstETH_txn_count)
    logger.cs_logger.info(f'Свапы wstETH - транзакций: {txn_count}')

    price_wstETH = helper.get_price_wstETH('wstETH')
    price_ETH = helper.get_price('ETH')
    wstETH_volume = random.randint(settings.wstETH_volume[0], settings.wstETH_volume[1])
    swap_balance_eth = helper.trunc_value(wstETH_volume / price_ETH, 4, 6)
    iZUMi_wstETH.swapping(wallet, swap_balance_eth, price_wstETH, txn_count)

    price_wstETH = helper.get_price_wstETH('wstETH')
    value_token_wei = tokens.contract_wstETH.functions.balanceOf(wallet.address).call()
    iZUMi_wstETH.swap_wstETH_to_ETH(wallet, value_token_wei, price_wstETH, wallet.txn_num)
    wallet.txn_num += 1


def swaps(wallet):
    mods = list()
    if settings.work_mode_swap == 1:
        mods.extend(['USDC', 'wstETH'])
    if settings.work_mode_swap == 2:
        mods.extend(['wstETH', 'USDC'])
    if settings.work_mode_swap == 0:
        mods.extend(['USDC', 'wstETH'])
        random.shuffle(mods)

    for module in mods:
        if module == 'USDC':
            if settings.USDC_switch == 1:
                USDC_swaps(wallet)
        if module == 'wstETH':
            if settings.wstETH_switch == 1:
                wstETH_swaps(wallet)
