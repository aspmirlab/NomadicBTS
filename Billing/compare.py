import sqlite3
from random import randint
import subprocess
from subprocess import run, PIPE
import time
while True:

	db0 = sqlite3.connect('/var/lib/asterisk/sqlite3dir/sqlite3.db')
	db1 = sqlite3.connect('/var/run/TMSITable.db')

	cursor0 = db0.cursor()
	cursor1 = db1.cursor()

	buddies = [buddies[0] for buddies in cursor0.execute('''select username 
															from SIP_BUDDIES''')]
	bud = [x.replace('IMSI', '') for x in buddies]
	tmsi = [tmsi[0] for tmsi in cursor1.execute('''select IMSI
															from TMSI_TABLE''')]


	compare = list(set(tmsi) - set(bud))
	print ("[output]: ", compare)
	db0.close()
	db1.close()


	def generator(n):
		r_start = 10**(n-1)
		r_end = (10**n)-1
		return randint(r_start, r_end)

	if not compare:
		print ("[INFO] No new subscriber")
	else:
		for i in range(len(compare)):
			num = '130'
			number = generator(7)
			pin = generator(6)
			name = generator(4)
			name = str(name)
			imsi = compare[i]
			imsis = 'IMSI' + imsi

			cdm = 'target_term -run 6 "./nmcli.py sipauthserve subscribers create "{name}" {isdn} {msisdn}"'
			cdm = cdm.format(name = name, isdn = imsisc, msisdn = number)
			cdm = ['/bin/bash', '-c', cdm]
			o = subprocess.run(cdm, stdout = PIPE)

			message = 'Registration success! number:{} pin{}'
			message = message.format(number, pin)
			dsn = 'target_term -run 4 sendsms {imsi} {num} {message}'
			dsn = dsn.format(imsi=imsi, num=num, message=message)
			cmd = [ '/bin/bash', '-c', dsn]

			band9 = subprocess.run(cmd, stdout = PIPE)
	print("===================================================")
	print("===================================================")
	print("                                                   ")
	time.sleep(5)