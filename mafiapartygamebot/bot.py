#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""mafia party game bot"""
import logging
import sys

from telegram.ext import Updater, CommandHandler
from host import Host
from game import GameStatus

token = "7652563058:AAGirGKSQlIPmr1C94z3v62mV8FKTZxRM2k"

logging.basicConfig(filename='bot.log',level=logging.INFO)

logger = logging.getLogger('mafiapartygamebot')

logger.setLevel(logging.INFO)

logger.info('bot started')

host = Host()

def new(bot, update):
    """start new game"""
    game = host.get_game(update.message.chat_id)
    if game and game.state == GameStatus.waiting:
        bot.sendMessage(
            update.message.chat_id,
            'We are already expecting players! \r\n{} {}'
            .format(game.game_master.name, game.game_master.role))
    elif game and game.state == GameStatus.started:
        bot.sendMessage(
            update.message.chat_id,
            'And we are already playing 😁 To end the current game, use the command /cancel')
    else:
        game = host.create_game(update.message.chat_id, update.message.from_user)
        game_master = game.game_master
        bot.sendMessage(
            update.message.chat_id,
            'We're starting a new game, join us quickly! \r\n{} {}'
            .format(game_master.name, game_master.role))

def join(bot, update):
    """join game"""
    game = host.get_game(update.message.chat_id)

    if game is None:
        bot.sendMessage(
            update.message.chat_id,
            'First, create a new game using the command /new')
    else:
        if game.game_master.identity == update.message.from_user.id:
            bot.sendMessage(
                update.message.chat_id,
                'The presenter plays the role of the presenter...')
        else:
            player = game.add_player(update.message.from_user)
            if player:
                bot.sendMessage(
                    update.message.chat_id,
                    'Joined the game {}'.format(player.name))

def play(bot, update):
    """play new game"""
    game = host.get_game(update.message.chat_id)

    if not game:
        bot.sendMessage(
            update.message.chat_id,
            'First you need to create a game using the command /new')

    elif game and game.state == GameStatus.waiting:
        if game.game_master.identity != update.message.from_user.id:
            bot.sendMessage(
                update.message.chat_id,
                'Only the host can start the game.. \r\n{} {}'
                .format(game.game_master.name, game.game_master.role))
        else:
            game.start()
            game_master = game.game_master

            if len(game.players) == 0:
                bot.sendMessage(update.message.chat_id, 'Players are needed to play mafia 😊')
                return

            players = ['Player Roles: \r\n']
            for player in game.players:
                players.append('{} {}'.format(player.role, player.name))
                bot.sendMessage(player.identity, '❗️ Your role {}'.format(player.role))

            bot.sendMessage(game_master.identity, '\r\n'.join(players))

            bot.sendMessage(
                update.message.chat_id,
                'Город засыпает 💤 \r\n{} {}'.format(game_master.name, game_master.role))

    elif game and game.state == GameStatus.started:
        bot.sendMessage(
            update.message.chat_id,
            'And we are already playing 😁 To end the current game, use the command /cancel')

def cancel(bot, update):
    """cancel game"""
    game = host.get_game(update.message.chat_id)

    if game:
        game_master = game.game_master
        if game_master.identity != update.message.from_user.id:
            bot.sendMessage(
                update.message.chat_id,
                'Only the host can stop the game.. \r\n{} {}'
                .format(game_master.name, game_master.role))
        else:
            host.delete_game(update.message.chat_id)
            bot.sendMessage(update.message.chat_id, 'The game has been stopped 😐')
    else:
        bot.sendMessage(update.message.chat_id, 'Game not found 😳')

def help(bot, update):
    """print help"""
    bot.sendMessage(update.message.chat_id,
                    '/new - creating a new game \r\n'+
                    '/join - join the ongoing  game\r\n'+
                    '/play - the city falls asleep... \r\n'+
                    '/cancel - finish the game')

updater = Updater(token)

updater.dispatcher.add_handler(CommandHandler('new', new))
updater.dispatcher.add_handler(CommandHandler('join', join))
updater.dispatcher.add_handler(CommandHandler('play', play))
updater.dispatcher.add_handler(CommandHandler('cancel', cancel))
updater.dispatcher.add_handler(CommandHandler('help', help))

updater.start_polling()

updater.idle()
