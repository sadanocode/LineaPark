from random import shuffle
import settings


def get_modules_list():
    modules = list()
    # Операции
    if settings.yooldo_enable == 1:
        modules.append('yooldo')
        shuffle(modules)

    if settings.pictographs_enable == 1:
        modules.append('pictographs')
        shuffle(modules)

    if settings.abyss_world_mint_switch == 1:
        modules.append('abyss')
        shuffle(modules)

    if settings.omnisea_mint_switch == 1:
        modules.append('omnisea')
        shuffle(modules)

    if settings.gamer_boom_mint_switch == 1:
        modules.append('gamerboom')
        shuffle(modules)

    return modules
