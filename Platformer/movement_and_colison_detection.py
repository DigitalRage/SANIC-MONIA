#movement and colison detection
import time
import sys
import os
import termios
import tty
import select
import atexit
import signal
import random
import math
import threading
import queue
import readchar
import copy
from gun_function import board_val
from the_board import board
# movment
def get_char():
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)
	#clear extra input
	ch = ''
	while True:
		[i, o, e] = select.select([sys.stdin.fileno()], [], [], 0.1)
		if i:
			ch = sys.stdin.read(1)
		else:
			break
	#the main stuff
	try:
		tty.setraw(sys.stdin.fileno())
		[i, o, e] = select.select([sys.stdin.fileno()], [], [], 0.1)
		if i:
			ch = sys.stdin.read(1)
		else:
			ch = ''
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	return ch
def start_input_thread(input_queue):
	def input_thread(input_queue):
		while True:
			ch = get_char()
			if ch:
				input_queue.put(ch)
	input_thread_instance = threading.Thread(target=input_thread, args=(input_queue,), daemon=True)
	input_thread_instance.start()
#collision detection
def is_solid(x, y):
	return board_val[x][y] in ["g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", "g9","g10","g11","g12","g13","g14","g15","g16","g17","g18","g19","g20","g21","g22","g23","g24","g25","g26","g27","g28","g29","g30","g31","g32","g33","g34","g35","g36","g37","g38","g39","g40","g41","g42","g43","g44","g45","g46","g47","g48","g49","g50","b1","b2","b3","b4","b5","b6","b7","b8","b9","b10","b11","b12","b13","b14","b15","b16","b17","b18","b19","b20"]
def is_on_ground(x, y):
	return is_solid(x, y + 1)
def is_damager(x, y):
	return board_val[x][y] in ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "d11", "d12", "d13", "d14", "d15", "d16", "d17", "d18", "d19", "d20"]
def is_goal(x, y):
	return board_val[x][y] in ["G1"]
def is_checkpoint(x, y):
	return board_val[x][y] in ["C1"]
def is_ammo(x, y):
	return board_val[x][y] in ["A1"]
def is_health(x, y):
	return board_val[x][y] in ["H1"]
def is_bullet(x, y):
	return board_val[x][y] in ["o1"]
#work on more