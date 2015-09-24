import json, re, socket, string, sys

with open('config.json') as json_data:
	data = json.load(json_data)

SERVER = data['Server']
PORT = data['Port']
CHANNEL = data['Channel']

NICK = data['BotNick']
TRIGGER = data['Trigger']
ADMINS = data['Admins']


class Bottly(object):

	def __init__(self, server, port, nick, admins, trigger):
		self.server = server
		self.port = int(port)
		self.nick = nick
		self.admins = admins
		self.trigger = trigger

	def connect_server(self):
		self.irc = socket.socket()
		self.irc.connect((self.server, self.port))

	def pong(self, target=':Pong'):
		message = 'PONG %s' % target
		self.send_data(message)

	def join_channel(self, channel, password=''):
		self.send_data('JOIN %s' % channel)

	def leave_channel(self, channel, message):
		self.send_data('PART %s :%s' % (channel, message))
		print(message)


	def register_nick(self):
		self.send_data('USER {0} {0} {1} {0}'.format(self.nick, self.server))
		self.send_data('NICK ' + self.nick)

	def send_data(self, data):
		if data is not None:
			self.irc.send(str.encode(data + '\r\n'))

	def send_message(self, reciever, message):
		self.send_data('PRIVMSG ' + reciever + ' :' + message)

	def get_data(self):
		data = self.irc.recv(4096)
		decoded_data = []
		for item in data.split():
			decoded_data.append(item.decode('UTF-8'))
		print(decoded_data)
		print(data)
		return decoded_data

	def check_input(self, data):
		if 'ERROR' in data:
			print('Error, disconnecting')
		elif data[1] in ['PRIVMSG', 'JOIN', 'PART']:
			self.command_filter(data)
		elif data[0] == 'PING':
			self.pong(data[0])

	def command_filter(self, data):
		sender = self.get_sender(data[0])
		channel = data[2]
		try:
			command = data[3].lstrip(':')
		except:
			command = None

		if self.trigger + 'foo' == command:
			self.send_message(channel, 'bar')
		elif self.trigger + 'leave' == command:
			if sender in self.admins:
				try:
					channel = data[4]
				except IndexError:
					pass
				message = '...not that anyone cares'
				self.leave_channel(channel,message)
			else:
				self.deny_command(channel, sender)
		elif self.trigger + 'join' == command:
			if sender in self.admins:
				try:
					channel = data[4]
				except IndexError:
					pass
				self.join_channel(channel)
			else:
				self.deny_command(channel, sender)

	def get_sender(self, line):
		sender = ''
		for char in line:
			if char == '!':
				break
			if char != ':':
				sender += str(char)
		return sender

	def is_admin(self, user_nick):
		return user_nick in self.admins

    def deny_command(self, channel, sender):
        self.send_message(channel, 'Not authed')

if __name__ == '__main__':
	bot = Bottly(SERVER, PORT, NICK, ADMINS, TRIGGER)
	bot.connect_server()
	bot.register_nick()

	for channel in CHANNEL:
		bot.join_channel(channel)

	while 1:
		data = bot.get_data()
		bot.check_input(data)
