import parser
import struct
from threading import Thread


def cmd(cmd, game, server):
	print("Executing Command: {}".format(cmd))

	msg_type = b'\x65\x00'
	msg_src = b'\x1e\x56\x6d\x10'
	msg_tgt = b'\x1e\x56\x6d\x10'
	srv_id = b'\x24\x04'
	magic = bytearray(b'\xaf\x4b\x01\x00\x03\x00\x22\x00')
	text = bytearray('hiya everyone, lalas r da best', 'utf-8')
	print(text)
	print(len(text))
	while len(text) < 1024:
		text.append(0)
	
	data = magic + text
	packet = parser.encode(msg_type, msg_src, msg_tgt, srv_id, data)
	server.sendall(packet)
	return