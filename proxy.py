import socket
import parser, cmdhandler
from time import sleep
from importlib import reload
from threading import Thread

class Server2Proxy(Thread):

	def __init__(self, host, port, sport):
		super(Server2Proxy, self).__init__()
		self.game = None #tobe game client socket
		self.port = port
		self.host = host
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.connect((host, port))
		self.sport = sport

	def run(self):
		while True:
			data = self.server.recv(4096)
			if data:
				#Forward to client
				self.game.sendall(data)
				try:
					parser.parse(data, self.sport, self.port, "server",  self.game, self.server)
				except Exception as e:
					print("Parse Error(s): %s" % e)
				
		
class Game2Proxy(Thread):

	def __init__(self, connection, port, sport):
		super(Game2Proxy, self).__init__()
		self.server = None
		self.game = connection
		self.port = port
		self.sport = sport

	def run(self):
		while True:
			data = self.game.recv(4096)
			if data:
				#Parse Packet
				try:
					cmd = parser.parse(data, self.sport, self.port, "game", self.game, self.server)
					if cmd == 'pass':
						pass
					if cmd == 'reload':
						reload(parser)
						pass
					if cmd == None:
						self.server.sendall(data)
				except Exception as e:
					try:
						self.server.sendall(data)
					except Exception as e:
						print("Server Packet Error: {}".format(e))
						print("Parse Error(c): %s" % e)
						reload(parser)
					

class Proxy(Thread):

	def __init__(self, from_host, to_host, port):
		super(Proxy, self).__init__()
		print("[Proxy(%i)] setting up" % port)
		self.from_host = from_host
		self.to_host = to_host
		self.port = port
		self.connections = []
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.from_host, port))
		self.sock.listen(1)
		print("[Proxy(%i)] listening" % port)

	def run(self):
		while True:
			self.game, addr = self.sock.accept()
			print("New Connection at %s:%s" % addr)

			g2p = Game2Proxy(self.game, self.port, addr[1])
			s2p = Server2Proxy(self.to_host, self.port, addr[1])
			g2p.server = s2p.server
			s2p.game = g2p.game

			self.connections.append((g2p, s2p))
			self.connections[-1][0].start()
			self.connections[-1][1].start()


masterserver = Proxy('0.0.0.0', '204.2.229.11', 54994)
masterserver.start()

brynhilder = Proxy('0.0.0.0', '204.2.229.112', 55007)
brynhilder.start()