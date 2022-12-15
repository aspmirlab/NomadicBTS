import sqlite3
from random import randint
import subprocess
from subprocess import run, PIPE
import time
while True:

	asterisk_db = sqlite3.connect('/var/lib/asterisk/sqlite3dir/sqlite3.db')
	tmsi_db = sqlite3.connect('/var/run/TMSITable.db')

	asterisk_db_cursor = asterisk_db.cursor()
	tmsi_db_cursor = tmsi_db.cursor()

	usernames = [username[0].replace('IMSI', '') for username in asterisk_db_cursor.execute('''select username 
															from SIP_BUDDIES''')]
	
	imsis = [imsi[0] for imsi in tmsi_db_cursor.execute('''select IMSI
															from TMSI_TABLE''')]


	compare_lists = list(set(imsis) - set(usernames))
	print ("[output]: ", compare_lists)
	
	asterisk_db.close()
	tmsi_db.close()


	def generator(n):
		r_start = 10**(n-1)
		r_end = (10**n)-1
		return randint(r_start, r_end)

	if not compare_lists:
		print ("[INFO] No new subscriber")
	else:
		for i in range(len(compare_lists)):
			operator_number = '130'
			new_subscriber_number = generator(7)
			new_subscriber_pin = generator(6)
			new_subscriber_name = str(generator(4))
			imsis = 'IMSI' + compare_lists[i]

			create_subscriber_command = 'target_term -run 6 "./nmcli.py sipauthserve subscribers create "{name}" {isdn} {msisdn}"'
			create_subscriber_command = create_subscriber_command.format(name=new_subscriber_name, isdn=imsis, msisdn=new_subscriber_number)
			create_subscriber_command = ['/bin/bash', '-c', create_subscriber_command]
			create_subscriber_process = subprocess.run(create_subscriber_command, stdout = PIPE)

			success_message = 'Registration success! number:{} pin{}'
			success_message = success_message.format(new_subscriber_number, new_subscriber_pin)
			send_subscriber_sms_command = 'target_term -run 4 sendsms {imsi} {operator_number} {message}'
			send_subscriber_sms_command = send_subscriber_sms_command.format(imsi=imsi, operator_number=operator_number, message=success_message)
			send_subscriber_sms_command = [ '/bin/bash', '-c', send_subscriber_sms_command]

			send_subscriber_sms_process = subprocess.run(send_subscriber_sms_command, stdout = PIPE)
	print("===================================================")
	print("===================================================")
	print("                                                   ")
	time.sleep(5)