#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import pickle

import aiohttp
from aiogram import Bot, Dispatcher, executor, types


def main():
    logging.basicConfig(level=logging.INFO)

    args = parse_command_line()

    bot = Bot(args.token)
    dispatcher = Dispatcher(bot)

    @dispatcher.message_handler(commands=("get_ip",))
    async def handler(message: types.Message):  # pylint: disable=W0612
        if not is_allowed(message.chat.id, args.allowed_clients, args.setup):
            return

        await bot.send_message(message.chat.id, await get_ip_address())

    executor.start_polling(dispatcher, skip_updates=True)


def parse_command_line():
    parser = argparse.ArgumentParser(description="Telegram bot that replies "
                                                 "with its own IP address")
    parser.add_argument("token", help="API token of the Telegram bot.")
    parser.add_argument("allowed_clients",
                        help="Database of chat IDs that can query the bot. "
                             "The file will be created if it does not exist.")
    parser.add_argument("--setup",
                        action="store_true",
                        help="Allow anyone to query the bot. "
                             "All clients will be added to the "
                             "allowed database.")

    return parser.parse_args()


def is_allowed(chat_id, allowed_clients_file, setup):
    try:
        with open(allowed_clients_file, mode="rb") as input_file:
            allowed_list = pickle.load(input_file)
    except OSError:
        allowed_list = set()

    if not setup:
        return chat_id in allowed_list

    allowed_list.add(chat_id)

    with open(allowed_clients_file, mode="wb") as output_file:
        pickle.dump(allowed_list, output_file)

    return True


async def get_ip_address():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://icanhazip.com/") as response:
            return await response.text()


if __name__ == "__main__":
    main()
