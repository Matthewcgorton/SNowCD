#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3

import sys, getopt
import requests
import re
import time
import json
import datetime


from SNowclassv2 import SNowCD


def main(argv):

	debug = 0
	username = ''
	password = ''
	env = '-'
	sysId = ''
	chg = ''
	filename = ''
	

	try:
			opts, args = getopt.getopt(argv,"h:u:p:d:g:",["username=","password=","debug=", "group=", "file=", "sys=", "chg=", "env="])
	except getopt.GetoptError:
		print('test.py ')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print ('Snowv2.py --e=[dev|test] [--chg==CHG00????? | --sysid=<sysid>]--file=<testresultsfile>--d=[1-9]' )
			sys.exit()
		elif opt in ("-d", "--debug"):
			if   arg == '1' : debug = 1
			elif arg == '2' : debug = 2
			elif arg == '3' : debug = 3
		elif opt in ("-e", "--env"):
			if   arg == 'dev' : 		env = 'dev'
			elif arg == 'test' : 		env = 'test'
		elif opt in ("--sys"):				sysId = arg
		elif opt in ("--file"):				filename = arg
		elif opt in ("--chg"):				chg = arg
		elif opt in ("-u", "--username"):	username = arg
		elif opt in ("-p", "--password"):	password = arg



	if   env == 'test' :	baseurl = 'https://gaptechtest.service-now.com/api/now'
	elif env == 'dev'  :	baseurl = 'https://gaptechdev.service-now.com/api/now'
	else :
		print("Unknown environment (--env=%s)" % env)
		exit(1)
	
	
	s = SNowCD(chg)
	
	s.baseurl = baseurl
	s.debug = debug
	
	
	with open('creds.txt', 'rb') as f:
		read_data = f.read()
	f.closed

	s.username = json.loads(read_data.decode("utf-8"))['username']
	s.password = json.loads(read_data.decode("utf-8"))['password']
	


#	if username == '' :
#		print ("Username : ")
#		username = input()

#	if password == '' :
#		print ("Password : ")
#		password = input()


	ct = datetime.datetime.now()
	st = ct + datetime.timedelta(seconds=30)
	et = ct + datetime.timedelta(hours=1, seconds=30)


	s.payload = {"type":"continuous_delivery",
                 "u_elevated_approval_required":"continuous_delivery",
                 "u_change_classification":"Delivery",
                 "u_ci_app_delivery":"Application",
                 "u_app_infra":"App",
                 "change_plan":"Automated deployment by RDP",
                 "backout_plan":"Standard recovery plan for pipeline changes",
                 "test_plan":"See attached pdf",
                 "justification":"N/A",
                 "u_customer_impact":"N/A",

                 "requested_by":"Matthew Gorton (Ma8u333)",
                 "u_release":"Continuous Delivery",
                 "short_description":"POET deployment build 15123",
                 "description":"Deployment of POET V2. This is a test after standiup meeting, \n\n  mgorton, clarcina",

                 "start_date":st.strftime('%Y/%m/%d %H:%M:%S'),
                 "end_date":et.strftime('%Y/%m/%d %H:%M:%S'),


                 "cmdb_ci":"Pyramid (POET)"
                 }


# create new change unless sysid or change number given as an arg
	if sysId == '' and s.chg == '' :
		if(debug >= 1) : print("Create Change")
		
		s.createChangeRequest()
	else : 
		if(debug >= 1) : print( "Updating existing change ", s.chg)

		if s.chg == '' :
			s.sysId = sysId
		else :
			s.sysId = s.loopkupChangeRequest(chg)

	s.display()
	



#attach test evidence
	if(debug >= 1) : print("\n\nattaching file")
	if(filename == '' ) : filename = 'test_results.pdf'

	s.attachFile(filename)	



# Check for approval 		
	if(debug >= 1) : print("Checking for approval (1=Open, 7=rejected, 10=Approved, 20=Pending approvals)")
	

	while s.approvedState() == 1 :	
		time.sleep(1)

	if(	s.approvedState() == 7 ): 
		print("Change Rejected")
		exit(1)
			
	if(debug >= 1) : print("\n\nChange is approved:")	



# Waiting for start of change window
	if(debug >= 1) : print("Waiting for start of change:")
	while s.isChangeWindowOpen() != 1 :
		time.sleep(1)

	if(debug >= 1) : print("\n\nChange window is open:")	



# simulating deployment
	if(debug >= 1) : print(" Begin deployment: changing status to WIP")
	s.updateWorkInProgress()
	
	if(debug >= 1) : print(" Adding progress notes")
	
	s.addWorkNotes('Build 15 deployed to host px231\nserver started\nhealth check clean')
	time.sleep(1)
	s.addWorkNotes('Build 15 deployed to host px456\nserver started\nhealth check clean')
	time.sleep(1)
	s.addWorkNotes('Build 15 deployed to host px568\nserver started\nhealth check clean')
	time.sleep(1)
	s.addWorkNotes('Build 15 deployed to host px890\nserver started\nhealth check clean')
	time.sleep(1)

#closed change
	if(debug >= 1) : print("End of deploy: Changing status to Closed->Successful")
	s.updateClosed()

	  

	
if __name__ == "__main__":
   main(sys.argv[1:])	








