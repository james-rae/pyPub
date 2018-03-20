import arcpy

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

"""Publish the service.

    Args:
        inFolder: Absolute path of workspace folder.
        sd: SD file to publish.
        connPath: Path to connection file that is used to connect to a GIS Server.
        serviceName: Name of the service.
        folder: Name of the folder to publish in.
        logs: log list holds all log items for current publication
        summary (optional): A string that represents the Item Description Summary (default=None).
        tags (optional): A string that represents the Item Description Tags (default=None).
"""


# ############################################

def publishSD(inFolder, sd, connPath, serviceName, folder, logs, summary=None, tags=None):

    checkError.printLog(logs,"Publishing SD in: " + inFolder)

    sdPath = inFolder + "/" + sd
    folderName = folder

    # Execute UploadServiceDefinition.  This uploads the service definition
    # and publishes the service.
    arcpy.UploadServiceDefinition_server(sd, connPath)
    checkError.printLog(logs, "Service successfully published")

def main():
    folder = arcpy.GetParameterAsText(0)
    sd = arcpy.GetParameterAsText(1)

    # Connection files lurk at
    # C:\Users\<userid>\AppData\Roaming\ESRI\Desktop10.4\ArcCatalog\
    # TODO change to param?
    conn = "C:\\Users\\jamesr\\AppData\\Roaming\\Esri\\Desktop10.4\\ArcCatalog\\arcgis on cipgis.canadaeast.cloudapp.azure.com (publisher)"

    # step 1. check if service exists, delete it.

    # step 2. publish service

    # step 3. turn service into tiles