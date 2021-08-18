import pandas as pd 
import sqlite3
import subprocess, os
from subprocess import run, PIPE

	
while True:
	conn = sqlite3.connect('cdr_lines.db') #Open CDR memory
	df = pd.read_csv('/var/log/asterisk/cdr-custom/Master.csv') #Open CDR
	conn1 = sqlite3.connect('/home/adetiba/central_customer.db') # Open Central customer DB
	cursor = conn.cursor()
	cursor1 = conn1.cursor()
	

	last = len(df.index) - 1 #Check Current number of lines in the CDR
	cursor.execute('SELECT LAST FROM LINES WHERE ID = 1;') 
	info = cursor.fetchone()
	db_last = int(info[0]) #retrieve from memory the last number of lines


	# Conditional statements begin
	if last == db_last:
		print("No new CDR Entry found")
	
	elif last > db_last:
		diff = last - db_last
		l_diff = diff - 1
		#print(diff, l_diff)
		print("[INFO] Found {} New Entry(ies) in CDR".format(diff))
		for i in range(diff):
			n = last - i
			#print(n)
			#print (len(df.index))
			df1  = df.iloc[n]
			dest = df1['2602']
			if dest == 'h-18':
				dest == str(dest)
			else:
				dest = int(dest)
			
			#print("destination type:", type(dest))
			origin = df1['IMSI621208460154609']
			origin  = str(origin)
			origin  = origin.replace('IMSI', '')
			origin = int(origin)
			#print (type(origin), origin)
			if dest == 2602 or dest == 2600 or dest == 'h-18':
				print("[INFO] System Call found... No charge for service")
			elif dest != 2602 or dest != 2600 or dest != 'h-18':
				duration = df1['7.1']
				duration = int(duration)
				
				print ("[INFO] User: ", origin)
				print ("[INFO] Destination: ", dest)
				print ("[INFO] Call duration: ", duration, "(s)")
				db_cmd = "SELECT BALANCE, RATE FROM CUSTOMER WHERE IMSI = {};"
				db_cmd = db_cmd.format(origin)
				cursor1.execute(db_cmd)
				operator = '113'
				info = cursor1.fetchone()
				balance = info[0]
				balance = int(balance)
				rate = int(info[1])
				cost = int((duration * rate) / 100)
				print ("[INFO] Call Cost: ", cost, "Naira")
				print ("[INFO] Current Balance: ",balance, "Naira")
				if cost <= balance:
					new_balance = balance - cost
					print("[INFO] New Balance: ", new_balance)
					up_cmd = "UPDATE CUSTOMER set BALANCE = {} where IMSI = {}"

					up_cmd = up_cmd.format(new_balance, origin)
					conn1.execute(up_cmd)
					body = "last call was {}Naira. Balance is {}Naira"
					body = body.format(cost, new_balance)
					cdm = 'target_term -run 4 "sendsms {target} {msisdn} {body}"'
					cdm = cdm.format(target = origin, msisdn = operator, body = body)
					cmd = cdm
					sms = [ '/bin/bash', '-c', cmd]
					r = run(sms, stdout = PIPE)
					print("[INFO] Database successfully updated")
				elif cost >= balance:
					new_balance = 0
					up_cmd = "UPDATE CUSTOMER set BALANCE = {} where IMSI = {}"

					up_cmd = up_cmd.format(new_balance, origin)
					conn1.execute(up_cmd)
					
					

					print("[INFO] Database successfully updated")
				
			if i == l_diff:
				line_updt = "UPDATE LINES set LAST = {} where ID = 1"

				line_updt = line_updt.format(last)
	
				conn.execute(line_updt)
				

				print("[INFO] Database successfully updated")


	elif last < db_last:
		print("[WARNING] Exception with Line DB found ")
		print("[DEBUG] Applying Fix")
		line_updt = "UPDATE LINES set LAST = {} where ID = 1"

		line_updt = line_updt.format(last)
		conn = sqlite3.connect('cdr_lines.db')
		conn.execute(line_updt)
		conn.commit()
		
		print("[INFO] Fix Successful")
		print("[INFO] Database successfully updated")
	
	conn.commit()
	conn1.commit()
	conn.close()
	print("===================================================")
	print("===================================================")
	print("                                                   ")


'''cmd  = "UPDATE LINES set LAST = {} where ID = 1"
cmd  = cmd.format(last)

conn.execute(cmd)

print ("Table updated successfully")

conn.close()

'''