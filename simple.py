
import httplib
import urllib
import ssl
import json

# simple script -- https fail party

#basic params
user="mrsilly"
password="changeme"

# 52.235.40.173:443
# serverUrl="https://cipgis.canadaeast.cloudapp.azure.com"
serverUrl="52.235.40.173"
port=443

tokenURL = "/arcgis/admin/generateToken"
params = urllib.urlencode({'username': user, 'password': password, 'client': 'requestip', 'f': 'json', 'expiration': 20 })
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

# Connect to server, ignore self-signed
httpConn = httplib.HTTPSConnection(serverUrl, port, context=ssl._create_unverified_context())

# attempt to post and get magic token. this usually fails with:
#     socket.gaierror: [Errno 11004] getaddrinfo failed
httpConn.request("POST", tokenURL, params, headers)

# Read response
response = httpConn.getresponse()
if (response.status != 200):
    httpConn.close()
    print "Error while fetching tokens from admin URL. Please check the URL and try again."
    
else:
    data = response.read()
    httpConn.close()

    #Extract the token from it
    token = json.loads(data)
    print token['token']