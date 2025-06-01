
/* 
PSEUDO CODE - OPC UA Client with Login

1. SETUP CONFIGURATION
   - Set application name = "Your App Name"
   - Set security = auto-accept certificates
   - Set timeouts

2. CONNECT TO SERVER
   - Set server address = "opc.tcp://your-server-ip:port"
   - Find available endpoints
   - Create login credentials = username + password
   - Establish secure session with server

3. BROWSE STRUCTURE
   - Start at root folder
   - Get list of all available nodes
   - For each node found:
     - Print node name
     - IF node is a variable (tag):
       - Read current value
       - Print value + timestamp + status
     - ELSE IF node is a folder:
       - Go deeper into that folder (repeat process)

4. CLEANUP
   - Close session
   - End program

ERROR HANDLING:
- IF connection fails → show error message
- IF certificate rejected → user must approve on server
- IF login fails → check username/password
- IF reading fails → show which tag failed
*/ 