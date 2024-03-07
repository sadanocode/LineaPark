from src.networks import linea_net
import settings
from src.logger import cs_logger
from src.Helpers.txnHelper import get_txn_dict, check_estimate_gas, exec_txn
from src.Helpers.helper import delay_sleep


def build_txn(wallet):
    try:
        txn = get_txn_dict(wallet.address, linea_net)
        txn['to'] = linea_net.web3.to_checksum_address('0xc0B4ab5CB0Fdd6f5DFddb2F7C10c4c6013F97bF2')
        txn['data'] = '0x1249c58b'
        return txn
    except Exception as ex:
        cs_logger.info(f'Ошибка в (GamerBoom/mint: build_txn) {ex.args}')


def mint_nft(wallet):
    try:
        cs_logger.info(f'Минтим GamerBoom')
        txn = build_txn(wallet)
        estimate_gas = check_estimate_gas(txn, linea_net)
        if type(estimate_gas) is str:
            cs_logger.info(f'{estimate_gas}')
            return False
        else:
            txn['gas'] = estimate_gas
            txn_hash, txn_status = exec_txn(wallet.key, txn, linea_net)
            cs_logger.info(f'Hash: {txn_hash}')

            wallet.txn_num += 1
            delay_sleep(settings.txn_delay[0], settings.txn_delay[1])
            return True

    except Exception as ex:
        cs_logger.info(f'Ошибка в (GamerBoom/mint: mint_nft) {ex.args}')


def minting(wallet):
    attempt = 1
    txn_status = False
    while txn_status is False and attempt < 4:
        cs_logger.info(f' _ Попытка №: {attempt}')
        txn_status = mint_nft(wallet)
        attempt += 1
        if txn_status is False:
            delay_sleep(settings.try_delay[0], settings.try_delay[1])
