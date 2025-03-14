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
  - Have the email notification have buttons that send an API call direct to Nile (instead of replying to email)
  - Provide a revoke/disconnect option
  - Move away from email and build it to interact with other solutions (send/receive flow)
