# nile-mab-email-approval
This set of scripts implements a MAB approval workflow leveraging email.  The process is as follows:

1.  Build and periodically update a DB with available segments, sites, buildings, etc
2.  Check for new unauthorized clients every 5 minutes
3.  If any new clients found, send an email with the device details and available segments
4.  If admin wants to approve a device, they respond to the email
5.  If an approval email is received (check every minute) an API call is sent to approve the device in MAB
6.  Email address of user is used for description in MAB table so there is an audit trail

Install Instructions:
- Download file (git or tarball) to local machine
- Run install script
- Enter parameters (for Nile Prod, API URL = https://u1.nile-global.cloud/api)
- Enjoy!

You will need the following to complete the script:
- API URL (see above)
- Tenant ID
- API Key
- Email address for receipient of new device notifications (typically an IT admin or group)
- Email address where approvals will be sent (this will be the inbox the script will check, essentially, assign an account/inbox to the alerting script)
- Email address new device notifications will be send from (should be the same as above)
- Password for inbox where approvals will be sent.

If doing repeated tests, you can reset the test by:

1. Delete your wired devices from MAB, they will show up as unauthenticated again
2. Run 'python reset-test.py' from /opt/mab-approval

Notes:

- Some additional work should be done to productize this:
  - Specifically the timers should be adjusted
  - Pagesize on API requests
  - Supporting multiple approvals in same email
  - Making the syntax simplier for the approval email
  - Error handling in syntax in reply email
  - Send a single email per new unauthorized client
  - Add some security to control who can send in approval requests
 
- Some ideas that could be built off of this:
  - This script assumes that there is now "Allow All" MAB rule and that all new unauthenticated clients will not have any initial access until approved.  Another version of this script could be built with the assumption that an "Allow All" MAB rule is in place and that devices will get INternet Only initially, will fingerprint, and then you could send more robust information in the email, i.e., what type of device it is, then move it to a more appropriate segment.
  - Have the email notification have buttons that send an API call direct to Nile (instead of replying to email)
  - Provide a revoke/disconnect option
  - Move away from email and build it to interact with other solutions (send/receive flow)
  - Use Shortcuts in iOS to detect the incoming email notifications of new clients and turn it into a different approval workflow.
  
