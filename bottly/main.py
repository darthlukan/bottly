import datetime
import json
import socket
import re
import requests
import time

import utils
import db as database
from logger import log_setup, log

with open("config.json") as json_data:
    data = json.load(json_data)

server = data["Server"]
port = data["Port"]
channels = data["Channel"]
nick = data["BotNick"]

log_dir = data["LogDir"]
log_file = data["LogFile"]

trusted = data["Trusted"]
admins = data["Admins"]
trigger = data["Trigger"]

response = data["Responses"]

if data["DEBUG"]:
    channels = ["#bottly"]
    nick = "bottly"
    trigger = "!"
    trusted = [""]
    admins = ["kekler"]


class Bottly(object):
    """
    Bottly is a class representing a bot. Bots contain their own commands,
    connections, and database.
    """

    def __init__(self, server, port, nick, trusted, admins, trigger, response):
        self.server = server
        self.port = int(port)
        self.nick = nick
        self.trusted = trusted + admins
        self.admins = admins
        self.trigger = trigger
        self.response = response

        self.hushed = False
        self.autotiny = True
        self.start_time = time.time()

        self.db = database.connect()
        self.logger = log_setup(log_dir, log_file)

    def connect_server(self):
        """
        connect_server executes socket.connect on the configured
        server and port supplied via config.json.
        """
        self.irc = socket.socket()
        self.irc.connect((self.server, self.port))

    def disconnect_server(self):
        """
        disconnect_server sends the IRC QUIT message over the socket.
        """
        message = "QUIT :Quit: %s" % self.response["quit"]
        self.send_data(message)

    def pong(self, target=":Pong"):
        """
        pong sends an IRC PONG message.
        """
        message = "PONG %s" % target
        self.send_data(message)

    def join_channel(self, channel, password=''):
        """
        join_channel sends the IRC JOIN message over the socket.
        """
        message = "JOIN %s" % channel
        self.send_data(message)

    def leave_channel(self, channel):
        """
        leave_channel sends IRC PART to the specified channel. Does nothing
        if channel is not provided.
        """
        if channel is not None and channel != "":
            message = "PART %s :%s" % (channel, self.response["leave"])
            self.send_data(message)

    def register_nick(self):
        """
        register_nick attempts to set the USER and NICK of the bot using
        the 'user' and 'nick' values specified in config.json.
        """
        message = "USER {0} {0} {1} {0}".format(self.nick, self.server)
        self.send_data(message)
        message = "NICK %s" % self.nick
        self.send_data(message)

    def send_data(self, data):
        """
        send_data converts 'data' from unicode to bytes and then
        submits IRC formatted messages over the socket.
        """
        if data is not None:
            data = utils.unicode_to_bytes(data + "\r\n")
            self.irc.send(data)

    def get_data(self):
        """
        get_data receives up to 4096 bytes of data from the socket, passes it
        through Bottly.analyze_data, and returns the result.
        """
        data = self.irc.recv(4096)
        data = self.analyze_data(data)
        return data

    def analyze_data(self, data):
        """
        analyze_data receives 'data' as bytes, converts those bytes to a unicode
        string, and attempts to route the data to the appropriate Bottly member
        for processing.
        """
        data = utils.bytes_to_unicode(data)
        data = data.split()
        if len(data) > 1:
            if data[0] in "PING":
                self.pong(data[1])
            else:
                command = None
                message = None
                user = self.get_user(data[0])
                msg_type = data[1]
                destination = data[2]
                if len(data) >= 4:
                    message = data[3:]
                    message[0] = message[0][1:]
                    if message[0].startswith(self.trigger):
                        command = message[0]
                        message = message[1:]

                self.check_input(user, msg_type, destination, command, message)

    def check_input(self, user, msg_type, destination, command, message):
        """
        check_input is a simple validator that attempts to determine whether or not
        the input values constitute a valid command or an error.
        """
        if "ERROR" in msg_type:
            print("Error")
        elif msg_type in ["PRIVMSG", "JOIN", "PART"]:
            self.command_filter(user, msg_type, destination, command, message)
        elif 'KICK' in msg_type:
            self.join_channel(destination)

    def send_message(self, destination, data):
        """
        send_message uses Bottly.send_data to submit an IRC PRIVMSG over the socket.
        """
        message = "PRIVMSG %s :%s" % (destination, data)
        self.send_data(message)

    def get_user(self, data):
        """
        get_user attemptes to parse the supplied input 'data' for a username 'user'.
        """
        user = ''
        for char in data:
            if char == "!":
                break
            elif char != ":":
                user += str(char)
        return user

    def is_trusted(self, destination, user):
        """
        is_trusted checks Bottly.trusted for the ocurrence of 'user'.
        """
        return user in self.trusted

    def is_admin(self, destination, user):
        """
        is_admin attemptes to check Bottly.admins for the occurrence of 'user'.
        """
        return user in self.admins

    def deny_command(self, destination):
        """
        deny_command submits a 'deny' message using Bottly.send_message.
        """
        self.send_message(destination, response["deny"])

    def trigger_check(self, data):
        """
        trigger_check checks 'data' for the presence of the configured trigger character.
        """
        state = False
        if self.trigger in data:
            state = True
            data = data.lstrip(self.trigger)
        return state, data

    def checkmail(self, destination, user):
        """
        checkmail performs a database lookup using the supplied 'destination' and 'user'
        input in order to find 'tells'. Returns string messages appropriate to whether or
        not the user has 'tells' waiting for them in the database.
        """
        db = self.db
        all_rows = database.get_tells(db, user)
        x = 0
        for row in all_rows:
            if x < 4:
                x += 1
                self.send_message(destination, "%s, %s -%s" % (row[0], row[1], row[2]))
        if len(all_rows) > 4:
            return self.response["more_mail"]
        return self.response["no_mail"]

    def isup(self, url):
        """
        isup uses www.isup.me in an attempt to determine whether or not the supplied 'url'
        'is up' or if it really is just you.
        """
        resp = requests.get("http://www.isup.me/%s" % url)
        if re.search("It's just you.", resp.text, re.DOTALL):
            return self.response["isup_up"]
        return self.response["isup_down"]

    def mail(self, destination, message, user):
        """
        mail stores a 'message' (tell) in the database so that 'user'
        can read it later via the 'checkmail' command (Bottly.checkmail).
        """
        database.save_tell(self.db, destination, message, user)

    def auto_tiny_controller(self, on):
        """
        auto_tiny_controller enables/disables 'autotiny' url creation based on the passed in
        boolean 'on'.
        """
        if on:
            return True, self.response["autotiny_off"]
        return False, self.response["autotiny_on"]

    def hush_controller(self, on):
        """
        hush_controller enables/disables bot output based on the supplied boolean 'on' param.
        """
        if on:
            return True, self.response["hush_on"]
        return False, self.response["hush_off"]

    def tinyurl(self, destination, url):
        """
        tinyurl attempts to generate a short url using the service provided by tinyurl.com.
        """
        payload = {'url': url}
        resp = requests.get("http://tinyurl.com/api-create.php", params=payload)
        if resp.status_code == 200:
            short_url = resp.text
            if len(short_url) < len(url):
                return self.response["tiny_success"] + ' ' + short_url
            elif len(url) < len(short_url):
                return self.response["tiny_short"]
        return self.response["tiny_failure"]

    def uptime(self, start_time):
        """
        uptime returns the difference between 'start_time' and end_time (now).
        """
        end_time = time.time()
        uptime = end_time - start_time
        uptime = str(datetime.timedelta(seconds=int(uptime)))
        return "Uptime: %s" % uptime

    def usage(self, command):
        """
        usage returns help information based on the passed in 'command' string.
        """
        # trusted command usage and descriptions
        autotiny = "USAGE: '~tiny{on,off}' - {enables,disables} %s's auto URL shorten feature" % self.nick
        hush = "USAGE: '~{hush,unhush' - {anables,disables} output fromm %s" % self.nick

        # user command usage and descriptions
        checkmail = "USAGE: '~checkmail' - check your mailbox"
        isup = "USAGE: '~isup <url>' -  check network status of your favorite websites"
        mail = "USAGE: '~mail <recipient> <message>' - send a message to someone's mailbox"
        tiny = "USAGE: '~tiny  <url>' - shorten long URLs with TinyURL"

        if command == "checkmail":
            return checkmail
        elif command == "isup":
            return isup
        elif command == "mail":
            return mail
        elif command == "tiny":
            return tiny

        if command == "user":
            return checkmail, isup, mail, tiny
        elif command == "trusted":
            return autotiny, hush

    def admin_only_commands(self, command, destination, user, arg):
        """
        admin_only_commands executes commands deemed too powerful for mere mortals.
        """
        if "join" == command:
            if len(arg) == 1:
                self.join_channel(arg[0])
        elif "leave" == command:
            if len(arg) == 1:
                self.leave_channel(arg[0])
            else:
                self.leave_channel(destination)
        elif "quit" == command:
            self.disconnect_server()

    def trusted_commands(self, command, destination, user):
        """
        trusted_commands executes commands deemed trivial by the gawds, but too
        powerful for the plebs.
        """
        message = ""
        if "hush" == command:
            self.hushed, message = self.hush_controller(True)
        elif "unhush" == command:
            self.hushed, message = self.hush_controller(False)
        elif "tinyoff" == command:
            self.autotiny, message = self.auto_tiny_controller(False)
        elif "tinyon" == command:
            self.autotiny, message = self.auto_tiny_controller(True)
        return self.autotiny, self.hushed, message

    def user_commands(self, command, destination, user, arg):
        """
        user_commands executes commands for which plebs are worthy.
        """
        message = ""
        if "foo" == command:
            message = "bar"
        elif "author" == command:
            message = "kekler - http://github.com/kekler"
        elif "checkmail" == command:
            message = self.checkmail(destination, user)
        elif command == "contributors":
            message = "Dragonkeeper - Hosts on #nixheeads & bug fixes | darthlukan - bug fixes & db.py"
        elif "help" == command:
            if len(arg) == 1:
                message = self.usage(arg[0])
            else:
                message = self.usage("user")
        elif "isup" == command:
            if len(arg) == 1:
                message = self.isup(arg[0])
            else:
                message = self.usage("isup")
        elif "mail" == command:
            if len(arg) >= 2:
                destination = arg[0]
                mail = " ".join(arg[1:])
                self.mail(destination, mail, user)
            else:
                message = self.usage("mail")
        elif "tiny" == command:
            message = self.tinyurl(destination, arg[0])
        elif "uptime" == command:
            message = self.uptime(self.start_time)
        else:
            message = response["commandNotFound"]

        return message

    def auto_commands(self, command, destination, usr, arg):
        """
        auto_commands executes commands that do not require explicit user
        requests, such as automatic shortening of urls.
        """
        message = ""
        if not command and isinstance(arg, list):
            for item in arg:
                if "http" in item:
                    url = item
                    message = self.tinyurl(destination, url)
        return message

    def command_filter(self, user, msg_type, destination, command, arg):
        """
        command_filter attempts to determine the appropriate action(s) based on
        the supplied input and then execute it/them.
        """
        message = None
        if command is not None:
            trig_pass, command = self.trigger_check(command)
        else:
            trig_pass = False
            message = self.auto_commands(command, destination, user, arg)

        if trig_pass:
            log(self.logger, user, msg_type, destination, command, arg)
            if self.is_admin(destination, user):
                self.admin_only_commands(command, destination, user, arg)

            if self.is_trusted(destination, user):
                self.autotiny, self.hushed, message = self.trusted_commands(command, destination, user)

            if not self.hushed:
                message = self.user_commands(command, destination, user, arg)

        if len(message) > 0:
            utils.pretty_print(self.nick, msg_type, destination, message)
            if isinstance(message, tuple):
                for line in message:
                    self.send_message(destination, line)
            else:
                self.send_message(destination, message)


if __name__ == "__main__":
    bot = Bottly(server, port, nick, trusted, admins, trigger, response)
    bot.connect_server()
    bot.register_nick()

    for channel in channels:
        bot.join_channel(channel)

    while 1:
        data = bot.get_data()

    bot.disconnect_server()
