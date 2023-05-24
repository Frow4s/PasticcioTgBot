from dataclasses import dataclass
from typing import Optional

from environs import Env
import os

@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: Optional[str] = None) -> Config:
    try:
        env = Env()
        env.read_env(path)
        return Config(tg_bot=TgBot(token=env('BOT_TOKEN')))
    except IOError:
        return Config(tg_bot=TgBot(token=os.environ['BOT_TOKEN']))
