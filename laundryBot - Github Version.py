# This is a bot that will create a dataset of laundry machine openings#imports
# ___

# Imports

import sqlite3  # SQLite database
import time
from datetime import datetime  # library used for getting time #why - ___

import requests  # scraping library
import schedule  # scheduling libraries

# Config
#If you are using this for some reason, update these two variables with the url to the washing machine tracker and your # of machines
#Also you can change the frequency that the bot checks the washers and dryers -- in minutes between checks
washAlertURL = "https://washalert.washlaundry.com/washalertweb/calpoly/WASHALERtweb.aspx?location=36524c01-9ec3-42ca-9f20-4b9b1fd0445a"
numberOFWashers = 3
numberOfDryers = 4
numberOfMachines = numberOFWashers + numberOfDryers
checkFrequency = 15 #Minutes

# Create & open database
sqliteConnection = sqlite3.connect('data.db')
cursor = sqliteConnection.cursor()

# execute the statement
# TODO: Run if table missing
def createTables():
    # SQL command to create a table in the database
    sql_command = """CREATE TABLE data (
    timestamp TIMESTAMP PRIMARY KEY,
    dayOfWeek TINYTEXT,
    hours TINYINT(24),
    minutes TINYINT(60),
    freeWashers TINYINT(%d),
    freeDryers TINYINT(%d),
    freeMachines TINYINT(%d)
    );""" % (numberOFWashers, numberOfDryers, numberOfMachines)

    cursor.execute(sql_command)

# Detect if table is present
    createTables()

#sets up days of the week for later use
#weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
typeList = []
startIndx = 0
#sets up dryer and washer statuses -- true is washer and false is dryer
content = requests.get(washAlertURL, verify=False).text
for i in range(numberOfMachines) :
    num = int(content.find("class=\"type\"", startIndx, len(content)))
    if content[num + 13] == "W" : #jank
        typeList.append(True)
    else :
        typeList.append(False)

#freeMachines is the amount of machines that are open at that time
#content is the entire html page
#the num and startIndx variables are probably stupid but they work
def laundryScraper() :
    content = requests.get(washAlertURL, verify=False).text
    startIndx = 0
    freeMachines = 0
    freeWashers = 0
    freeDryers = 0
    for i in range(numberOfMachines) :
        num = int(content.find("class=\"status\"", startIndx, len(content)))

        #if data is jank then I can exclude more cases, but for now I am only excluding the "In Use" state, leaving the others
        if content[num + 15] != "I" :
            freeMachines += 1
            if typeList[i] :
                freeWashers += 1
            else :
                freeDryers += 1
        startIndx = num + 1
    print(freeMachines)
    minu = str(datetime.today().minute)
    if len(str(datetime.today().minute)) == 1 :
        minu = "0" + minu
    # Add to database
    # SQL command to insert the data in the table # #dayOfWeek
    sql_command = "INSERT INTO data (timestamp, dayOfWeek, hours, minutes, freeWashers, freeDryers, freeMachines) VALUES ( " + str(datetime.today().timestamp()) + ", \"" + str(datetime.today().strftime("%A")) + "\", " + str(datetime.today().hour) + ", " + str(minu) + ", "+ str(freeWashers) + ", " + str(freeDryers) + ", " + str(freeMachines) +  "); "
    cursor.execute(sql_command)
    sqliteConnection.commit()

    #timestamp, dayOfWeek, hours, minutes, freeWashers, freeDryers, freeMachines

schedule.every(checkFrequency).minutes.do(laundryScraper) #TODO: Change to minutes

#while True:
for i in range(60):
    schedule.run_pending()
    time.sleep(1)

# close the connection
sqliteConnection.close()

