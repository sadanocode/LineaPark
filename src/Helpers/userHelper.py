import settings as stgs
import src.logger as logger
from src.networks import ethereum_net


def get_info(wallets):
    logger.cs_logger.info(f'Цена газа в Ethereum: {ethereum_net.web3.from_wei(ethereum_net.web3.eth.gas_price, "gWei")} gWei')
    if stgs.exc_withdraw == 1:
        logger.cs_logger.info(f'Вывод с биржи в сеть включен!')
        if stgs.exc_mode == 1:
            logger.cs_logger.info(f'Выводим {stgs.exc_percent[0]*100} - {stgs.exc_percent[1]*100} % от баланса')
        if stgs.exc_mode == 2:
            logger.cs_logger.info(f'Выводим весь доступный баланс')
        if stgs.exc_mode == 3:
            logger.cs_logger.info(f'Выводим сумму от {stgs.exc_sum[0]} до {stgs.exc_sum[1]} ETH')

    else:
        logger.cs_logger.info(f'Вывод с биржи в сеть отключен!')

    if stgs.exc_deposit == 1:
        logger.cs_logger.info(f'Депозит на адрес биржи включен!')
        if stgs.switch_bridge_exc == 0:
            logger.cs_logger.info(f'Депозит на биржу осуществляется из Linea!')
        if stgs.switch_bridge_exc == 1:
            logger.cs_logger.info(f'Депозит на биржу осуществляется из Arbitrum!')
    else:
        logger.cs_logger.info(f'Депозит на адрес биржи отключен!')

    logger.cs_logger.info(f'Депозит ликвидности ETH на сумму: {stgs.liq_volume[0]} - {stgs.liq_volume[1]} USD')

    logger.cs_logger.info(f'Задержки между кошельками: от {stgs.wallet_delay[0]} до {stgs.wallet_delay[1]} сек')
    logger.cs_logger.info(f'Задержки между транзакциями: от {stgs.txn_delay[0]} до {stgs.txn_delay[1]} сек')
    logger.cs_logger.info(f'Задержки после бриджа: от {stgs.bridge_delay[0]} до {stgs.bridge_delay[1]} сек')

    logger.cs_logger.info('Список обнаруженных адресов кошельков -- адресов бирж')
    for wallet in wallets:
        logger.cs_logger.info(f'№ {wallet.wallet_num} | {wallet.address} -- {wallet.exchange_address}')

    while True:
        logger.cs_logger.info(f'Подтвердить? Y/N: ')
        answer = input('')
        if answer.lower() == 'y':
            stgs.start_flag = True
            break
        if answer.lower() == 'n':
            break
