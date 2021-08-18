import time, os, subprocess
from subprocess import run, PIPE
import sqlite3, math
import collections


while True:
	db  = sqlite3.connect('/home/adetiba/central_customer.db')
	c_db = sqlite3.connect('channels.db')
	cursor = db.cursor()
	
	os.system('sudo asterisk -rx "core show channels verbose" | grep "active channel" > channels.txt')
	#cmd = ['/bin/bash', '-c', 'sudo asterisk -rx "core show channels verbose" | grep "active channel" > channels.txt']
	#act_chan = subprocess.Popen([cmd], stdout =  subprocess.PIPE)
	#r = run(cmd, stdout=PIPE)

	chan = open('channels.txt')
	for j in chan:
		space = j.split(' ')
		print("[INFO] Number of active channels:", space[0])
		chan_num = int(space[0])
		if chan_num == 0:
			print ("[INFO] No active channels")
		elif chan_num >= 1:
			#cmd = 'sudo asterisk -rx "core show channels concise" > watch.txt | head -n {} watch.txt > line.txt'
			#cmd = cmd.format(chan_num)
			cdm = ['/bin/bash', '-c', 'sudo asterisk -rx "core show channels concise" > watch.txt']
			#print(cmd)
			#os.system(cmd)	
			r = run(cdm, stdout = PIPE)
			print ("[INFO] Reading Channel ID")
			
			head  = 'head -n {} watch.txt > line.txt'
			head = head.format(chan_num)
			chmd = ['/bin/bash', '-c', head]
			w = run(chmd, stdout = PIPE)

			file = open("line.txt", "r")
			print ("[INFO] Opening channel list")
			chan_id = []
			origins = []
			dests = []
			imsis = []
			balances = []
			times = []
			chan_db = []

			for n in range(chan_num):
				x = n + 1
				i = file.readlines(x)
				i = str(i)
				m = i.split('!')
				channel_id = str(m[0])
				channel_id = channel_id.replace('[\'', '')
				print ("[INFO] Active Channel ID:", channel_id)
				print ("[INFO] Call Origin:", m[7])
				print ("[INFO] Call Destination:", m[2])
				time.sleep(1)
				db_cmd = 'SELECT IMSI, BALANCE, RATE FROM CUSTOMER WHERE PHONE_NUMBER = {};'
				origin = m[7]
				origin = int(origin)
				dest = int(m[2])
				db_cmd = db_cmd.format(origin)
				cursor.execute(db_cmd)
				info = cursor.fetchone()
				imsi = info[0]
				balance = info[1]
				rate = info[2]
				operator = '131'
				seconds_remaining = math.floor((balance * 100) / rate)
				chan_id.append(channel_id)
				origins.append(origin)
				dests.append(dest)
				imsis.append(imsi)
				balances.append(balance)
				times.append(seconds_remaining)
			
			cur = c_db.execute("SELECT CHANNELID FROM CHANNELS ")
			
			for channel in cur:
				chan_db.append(channel)
			
			new_chan = list(set(chan_id) - set(chan_db))
			#existing_chan = collections.Counter(chan_id) == collections.Counter(chan_db)
			deleted_chan = list(set(chan_db) - set(chan_id))
			
			if not new_chan:
				print("[INFO] No New Channels to Report")
			
			else:
				for i in new_chan:
					st = "INSERT INTO CHANNELS (CHANNELID, TIMELIMIT) VALUES ('{}', {})"
					k = new_chan.index(i)
					sec = times[k]
					
					ch = str(i)
					cmd = st.format(i, sec)
					
					c_db.execute(cmd);
					print("[INFO] Adding active channels to Database")
					
			
			if not chan_db:
				print("[INFO] No existing channels to report")
			else:
				print("[INFO] Updating existing Channels")
				for i in chan_db:
					m = str(i)
					m = m.replace('(', '')
					m = m.replace(')', '')
					m = m.replace(',', '')
					db_cmd = "SELECT TIMELIMIT FROM CHANNELS WHERE CHANNELID = {}"
					db_cmd = db_cmd.format(m)
					cursor = c_db.cursor()
					cursor.execute(db_cmd);
					info = cursor.fetchone()
					time_limit = info[0]
					time_limit = time_limit - 1
					st = "UPDATE CHANNELS set TIMELIMIT = {} where CHANNELID = {}"
					cmd = st.format(time_limit, m)
					c_db.execute(cmd);
					print("[INFO] Updating active channels in Database")
					if time_limit == 0:
						end  = 'sudo asterisk -rx "channel request hangup {}"'
						end = end.format(i)
						end_call = ['/bin/bash', '-c', end]
						EC = run(end_call, stdout = PIPE)
						print("[INFO] Call ended")
			
			if not deleted_chan:
				print ("[INFO] No channels to delete")
			
			else:
				for i in deleted_chan:
					m = str(i)
					m = m.replace('(', '')
					m = m.replace(')', '')
					m = m.replace(',', '')
					db_cmd = "DELETE from CHANNELS WHERE CHANNELID = {};"
					db_cmd = db_cmd.format(m)
					c_db.execute(db_cmd)
					print("[INFO] Deleting closed channels from database")
	c_db.commit()
	c_db.close()
	print("===================================================")
	print("===================================================")
	print("                                                   ")