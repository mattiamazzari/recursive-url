from pydantic import BaseModel, Field
from cat.mad_hatter.decorators import plugin
from enum import Enum
from typing import Union, List

class PluginSettings(BaseModel):
    chunk_size: int = 512
    chunk_overlap: int = 128
    recursive: bool = False
    option_exclude_dirs: str = ""
    option_max_depth: int = 2
    option_timeout: int = 10
    option_prevent_outside: bool = True

    class Config:
        title = "Plugin Settings"

# hook to give the cat settings
@plugin
def settings_schema():
    return PluginSettings.schema()