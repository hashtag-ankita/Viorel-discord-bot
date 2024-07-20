#this file will have little functions for quick help

import random
from discord.ext import commands

def random_color():
    """
    Generates a random color hex code and returns it.
    """
    hex = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

    hex_code = random.choice(hex)

    for i in range(5):
        hex_code += random.choice(hex)

    return hex_code


def convert_to_message_id(argument):
    """
    Function to convert the input argument to a message ID.
    Parameter:
        argument: The input to be converted to a message ID.
    Returns:
        message_id: The converted message ID if it is a positive integer.
    Raises:
        ValueError: If the input is not a positive integer.
    """
    try:
        message_id = int(argument)
        if message_id > 0:
            return message_id
        else:
            raise ValueError("Message ID must be a positive integer.")
    except ValueError:
        raise commands.BadArgument("Invalid message ID. Please provide a valid positive integer.")
