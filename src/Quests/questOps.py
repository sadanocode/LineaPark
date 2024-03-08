import settings
from src.logger import cs_logger
from src.Quests.Week2.yooldo.daily import sending
from src.Quests.Week2.yooldo.trobSwap import swapping
from src.Quests.Week2.Pictographs.mint import minting as pictographs_mint, staking as pictographs_stake
from src.Quests.Week2.AbyssWorld.mint import minting as abyss_mint
from src.Quests.Week2.Omnisea.mint import minting as omnisea_mint
from src.Quests.Week1.GamerBoom.mint import gamer_boom_mint
from src.Quests.Week1.GamerBoom.proof import gamer_boom_proof
from src.Quests.Week3.AsMatch.mint import as_match_mint
from src.Helpers.gasPriceChecker import check_limit
from src.Quests.Week3.Dmail.sendMail import dmail_send
from src.Quests.questHelper import running
from src.Quests.Week3.ReadOn.curate import read_on_curate
from src.Quests.Week3.SendingMe.abuse import sending_me


def quest_ops(wallet, modules):
    for module in modules:

        if module == 'yooldo':
            cs_logger.info(f'    ***   Модуль Yooldo   ***   ')
            if settings.daily_switch == 1:
                check_limit()
                sending(wallet)

            if settings.trob_swap_switch == 1:
                check_limit()
                swapping(wallet)

        if module == 'pictographs':
            cs_logger.info(f'    ***   Модуль Pictographs   ***   ')
            if settings.pictographs_mint_switch == 1:
                check_limit()
                pictographs_mint(wallet)
            if settings.pictographs_stake_switch == 1:
                check_limit()
                pictographs_stake(wallet)

        if module == 'abyss':
            cs_logger.info(f'    ***   Модуль Abyss World   ***   ')
            check_limit()
            abyss_mint(wallet)

        if module == 'omnisea':
            cs_logger.info(f'    ***   Модуль Omnisea  ***   ')
            check_limit()
            omnisea_mint(wallet)

        if module == 'gamerboom':
            cs_logger.info(f'    ***   Модуль GamerBoom  ***   ')
            if settings.gamer_boom_proof_switch == 1:
                check_limit()
                running(wallet, gamer_boom_proof)
            if settings.gamer_boom_mint_switch == 1:
                check_limit()
                running(wallet, gamer_boom_mint)

        if module == 'dmail':
            cs_logger.info(f'    ***   Модуль Dmail  ***   ')
            check_limit()
            running(wallet, dmail_send)

        if module == 'asmatch':
            cs_logger.info(f'    ***   Модуль AsMatch  ***   ')
            check_limit()
            running(wallet, as_match_mint)

        if module == 'readon':
            cs_logger.info(f'    ***   Модуль ReadOn  ***   ')
            check_limit()
            running(wallet, read_on_curate)

        if module == 'sendingme':
            cs_logger.info(f'    ***   Модуль SendingMe  ***   ')
            check_limit()
            running(wallet, sending_me)
