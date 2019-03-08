import sys
import time
import os
import threading


bytes_to_remote = 0
bytes_from_remote = 0

_relay_port = 0
_remote_address = ''
_remote_port = 0


def report_bandwidth():
	global bytes_to_remote
	global bytes_from_remote
	step = 0
	while True:
		time.sleep(1)
		if sys.platform == 'win32':
			os.system('cls')
		else:
			os.system('clear')
		print('Relaying on port {0} to {1}:{2}'.format(_relay_port, _remote_address, _remote_port))
		print('From remote: {0:.6f}MB/s | To remote: {1:.6f}MB/s'.format(
			float(bytes_from_remote) / 1000000, float(bytes_to_remote) / 1000000))
		if step == 0:
			print('\\')
			step += 1
		elif step == 1:
			print('|')
			step += 1
		elif step == 2:
			print('/')
			step += 1
		elif step == 3:
			print('-')
			step = 0
		bytes_from_remote = 0
		bytes_to_remote = 0


def start(relay_port, remote_address, remote_port):
	global _relay_port
	global _remote_address
	global _remote_port
	
	report_bandwidth_thread = threading.Thread(target=report_bandwidth)
	report_bandwidth_thread.daemon = True
	report_bandwidth_thread.start()

	_relay_port = relay_port
	_remote_address = remote_address
	_remote_port = remote_port
