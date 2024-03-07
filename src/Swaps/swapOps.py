from src.Swaps.iZUMiSwapUSDC import swap_usdc_to_eth
import settings
from src.Swaps.swapHelper import get_usdc_balance
from src.logger import cs_logger
from src.Helpers.helper import delay_sleep


def swap_usdc_remains(wallet):
    cs_logger.info(f'    ***   Свапаем остатки USDC на эфир  ***   ')
    txn_status = False
    if settings.usdc_swap_switch == 1:
        token_value = get_usdc_balance(wallet.address)
        if token_value != 0:
            while txn_status is False:
                attempt = 1
                txn_status = swap_usdc_to_eth(wallet, token_value)
                if txn_status is False:
                    attempt += 1
                    delay_sleep(settings.try_delay[0], settings.try_delay[1])
                    cs_logger.info(f'Делаем доп попытку № {attempt}')
