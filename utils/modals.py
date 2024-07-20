from discord import *
from discord.ext import commands
from discord.ui import *
import time
import os
import dotenv
import typing

class CustomModal1(Modal):
    def __init__(self, modal_type: str, label: str, title: str, custom_id: str, placeholder: str, timeout: int = 60):
        super().__init__(title=title, custom_id=custom_id, timeout=timeout)
        self.modal_type = modal_type

        self.input = TextInput(
            label=label,
            placeholder=placeholder,
            custom_id=f"{modal_type}_input",
            style=TextStyle.short
        )
        self.add_item(self.input)
        
