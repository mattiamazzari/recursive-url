from pydantic import BaseModel, Field
from cat.mad_hatter.decorators import plugin
from enum import Enum
from typing import Union, List

class PluginSettings(BaseModel):
    
    filter_key_words: str =""
    max_depth: int = 2
    timeout : int = 10

    class Config:
        title = "Plugin Settings"

# hook to give the cat settings
@plugin
def settings_schema():
    return PluginSettings.schema()