import json
from pathlib import Path
from typing import Any
from src.logger import logger

DEFAULT_CONFIG_PATH = Path('other/config.json')
PRETTY_NAMES = {
    "listener_rng_remember_enabled": "Listen chat",
    "listener_rng_remember": "Chance to remember message",
    "listener_parameters_disable_rng_on_answer": "Disable RNG on message answer",
    "listener_markov_enabled": "Enable markov learning",
    "listener_markov_learn_chance": "Markov learn chance",
    "listener_markov_prediction_enabled": "Enable markov message prediction",
    "listener_markov_prediction_chance": "Markov prediction chance",
    "listener_type_remember_message": "Remember messages",
    "listener_type_remember_video": "Remember video's",
    "listener_type_remember_video_message": "Remember video messages",
    "listener_type_remember_picture": "Remember pictures",
    "listener_type_remember_voice_message": "Remember voice messages",
    "listener_type_remember_sticker": "Remember stickers",
    "listener_type_remember_animation": "Remember GIFs",
    "sender_rng_sending_enabled": "Sending",
    "sender_rng_sending": "Chance to send message",
    "sender_type_types_chance": "Content type chance",
    "sender_type_message_chance": "Message chance",
    "sender_type_video_chance": "Video chance",
    "sender_type_video_message_chance": "Video message chance",
    "sender_type_picture_chance": "Picture chance",
    "sender_type_voice_message_chance": "Voice message chance",
    "sender_type_sticker_chance": "Sticker chance",
    "sender_type_animation_chance": "GIF chance",
    "emoji_reactions_enabled": "Reacts to messages",
    "emoji_reactions_chance": "React chance",
    "emoji_reactions_available": "Set available emojis"
}


def clamp(value: int, min_val: int, max_val: int):
    return max(min_val, min(max_val, value))


class Config:
    def __init__(self):
        self.listener_rng_remember_enabled: bool = True
        self.listener_rng_remember: int = 80

        self.listener_parameters_disable_rng_on_answer: bool = True

        self.listener_markov_enabled: bool = True
        self.listener_markov_learn_chance: int = 60
        self.listener_markov_prediction_enabled: bool = True
        self.listener_markov_prediction_chance: int = 80

        self.listener_type_remember_message: bool = True
        self.listener_type_remember_video: bool = True
        self.listener_type_remember_video_message: bool = True
        self.listener_type_remember_picture: bool = True
        self.listener_type_remember_voice_message: bool = True
        self.listener_type_remember_sticker: bool = True
        self.listener_type_remember_animation: bool = True

        self.sender_rng_sending_enabled: bool = True
        self.sender_rng_sending: int = 40

        # First Message
        self.sender_type_message_chance: int = 100
        self.sender_type_video_chance: int = 5
        self.sender_type_video_message_chance: int = 5
        self.sender_type_picture_chance: int = 25
        self.sender_type_voice_message_chance: int = 5
        self.sender_type_sticker_chance: int = 10
        self.sender_type_animation_chance: int = 10

        self.emoji_reactions_enabled: bool = True
        self.emoji_reactions_chance: int = 200
        self.emoji_reactions_available: str = "👍 👎 ❤ 🔥 🥰 👏 😁 🤔 🤯 😱 🤬 😢 🎉 🤩 🤮 💩 🙏 👀 🤣 💔 😭"

    def __setattr__(self, key: str, value: Any):
        if key == "listener_rng_remember" and isinstance(value, int):
            value = clamp(value, 1, 1000)

        super().__setattr__(key, value)

    @staticmethod
    def get_pretty_label(key: str) -> str | None:
        return PRETTY_NAMES.get(key)

    def to_dict(self) -> dict[str, Any]:
        d = {}
        for k, v in self.__dict__.items():
            if not k.startswith('__'):
                d[k] = v
        return d

    def load(self):
        if not DEFAULT_CONFIG_PATH.exists():
            DEFAULT_CONFIG_PATH.write_text(json.dumps(self.to_dict()), encoding='utf-8')
        else:
            config_json: dict = json.loads(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))
            if not isinstance(config_json, dict):
                logger.error(f'Config file is invalid. Expected JSON dictionary object but got {type(config_json)}')
                raise ValueError("Config must be a dictionary")
            config_keys = {
                key: value
                for key, value in vars(self).items()
                if not key.startswith('__') and not callable(value)
            }
            for key, value in config_json.items():
                if key not in config_keys:
                    logger.warning(f"Unknown configuration option '{key}' has been ignored on startup loading config")
                    continue
                setattr(self, key, value)

    def save(self):
        DEFAULT_CONFIG_PATH.write_text(json.dumps(self.to_dict()), encoding='utf-8')
