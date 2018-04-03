import arcpy
import httplib
import urllib
import ssl
import json

# ############################################
#
#  printLog(logs, msg)
#
# Appends message to the log collection and prints it
#
# ############################################


def printLog(logs, msg):
    print msg
    logs.append("")  #have to add an empty line, otherwise no line break in email content
    logs.append(msg)


# ############################################
#
#  ASSER JSON SUCCESS FUNCTION
#  Returns True in case of success,
#  False otherwise
"""Checks that the input JSON object is not an error object.
    Args:
        data: JSON string.
    Returns:
        True if successful, False otherwise.
"""
# ############################################

def assertJsonSuccess(data):

    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print "Error: JSON object returns an error. " + str(obj)
        return False
    else:
        return True

# ############################################
#
#  GET SERVICE RESPONCE FUNCTION
"""Connects to the service to get its current JSON definition.

    Args:
        serverName: Domain of server to connect to.
        serverPort: Port of server to connect to.
        service: URL of service.
        params: URL parameters.
        headers: URL headers.

    Returns:
        The service's current JSON definition.
"""
#
# ############################################

def getServiceResponse(serverName, serverPort, service, params, headers):

    #Connect to service
    httpConn = httplib.HTTPSConnection(serverName, serverPort, context=ssl._create_unverified_context())
    httpConn.request("POST", service, params, headers)

    #Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print "Could not read service information."
        return
    else:
        data = response.read()

        #Check that data returned is not an error object
        if not assertJsonSuccess(data):
            print "Error when reading service information. " + str(data)
        else:
            if "edit" in service:
                print "Service edited successfully."
            else:
                print
                print service + " responded successfully."

            httpConn.close()
            return data

# ############################################
#
#  GET TOKEN FUNCTION
"""Generate an access token for ArcGIS Admin API.

    Reference:
        http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000m5000000

    Args:
        username: Username of user who wants to get a token.
        password: Password of user who wants to get a token.
        serverName: Domain of server to connect to.
        serverPort: Port of server to connect to.

    Returns:
        The generated token.
"""
# ############################################

def getToken(username, password, serverName, serverPort):

    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    tokenURL = "/arcgis/admin/generateToken"

    # todo figure out how long our average session is, adjust expiration
    params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json', 'expiration': 20 })

    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    # TODO i think we can use getServiceResponse here.  same code, no?
    # Connect to URL and post parameters
    print serverName
    print params
    httpConn = httplib.HTTPSConnection(serverName, serverPort, context=ssl._create_unverified_context())
    httpConn.request("POST", tokenURL, params, headers)

    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print "Error while fetching tokens from admin URL. Please check the URL and try again."
        return
    else:
        data = response.read()
        httpConn.close()

        #Check that data returned is not an error object
        if not assertJsonSuccess(data):
            return

        #Extract the token from it
        token = json.loads(data)
        return token['token']

# ############################################

"""Publish the service.

    Args:
        sdFolder: Absolute path of workspace folder.
        sd: SD file to publish.
        connPath: Path to connection file that is used to connect to a GIS Server.
        serviceName: Name of the service.
        serverFolder: Name of the folder to publish in.
        logs: log list holds all log items for current publication

"""

# ############################################

def enhanceTile(serverName, serviceName, serverFolder, username, password, logs):

    serverPort = 443

    # Get a token to access ArcGIS REST API
    # todo chance so token is passed in, so we can re-use tokens
    token = getToken(username, password, serverName, serverPort)
    if token == "":
        print "Could not generate a token with the username and password provided."
        return

    # This request only needs the token and the response formatting parameter
    params = urllib.urlencode({'token': token, 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    folderPath = "/arcgis/admin/services/" + serverFolder

    serviceUrl = folderPath + "/" + serviceName + ".MapServer"

    # get the admin json object for the service
    serviceJson = getServiceResponse(serverName, serverPort, serviceUrl, params, headers)
    serviceObj = json.loads(serviceJson)

    # appears the values are encoded as text. attempt bools/ints if errors happen.
    serviceObj["properties"]["cacheOnDemand"] = "true"
    # serviceObj["properties"]["maxScale"] = "2000000"
    # serviceObj["properties"]["minScale"] = "145000000"

    # Serialize back into JSON
    updatedServiceJson = json.dumps(serviceObj)

    # Call the edit operation on the service.  Pass in modified JSON.
    editServiceUrl = serviceUrl + "/edit"
    params = urllib.urlencode({'token': token, 'f': 'json', 'service': updatedServiceJson})
    getServiceResponse(serverName, serverPort, editServiceUrl, params, headers)


# ############################################
# Main Party

# ############################################

print sys.version

user = arcpy.GetParameterAsText(0)
password = arcpy.GetParameterAsText(1)
logs = []

# update this to be real parameter
serverFolder = "PythonParty"

# Connection files lurk at
# C:\Users\<userid>\AppData\Roaming\ESRI\Desktop10.4\ArcCatalog\
# TODO change to param?

printLog(logs, "Start the party")

# step 1. check if service exists, delete it.

# step 2. publish service
# note: url seems to need to be a dns. python is freaking if we use normal web address
# "https://cipgis.canadaeast.cloudapp.azure.com"

enhanceTile("52.235.40.173", "Enhance", serverFolder, user, password, logs)

# step 3. turn service into tiles