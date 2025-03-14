import mysql.connector
import sqlite3
from kivy.app import App
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivy.logger import Logger
from datetime import datetime
from datetime import timedelta
from plyer import gps
from math import radians, sin, cos, sqrt, atan2


currentUser = ''
currentCompany = ''
currentCar = ''
currentDest = ''
currentPass = ''
currentCargo = ''
currentlat = 0
currentlon = 0
currentTripID = ''
mpg = 25 # the average miles per gallon of taxi cars
checkFrequency = 10 #seconds
minMph = 2



def DBConnect():
    mydb = mysql.connector.connect(
			host = "localhost", ##going to be an IP
			user = "root",		
			password = "password123",
			database = "second_db",
			)
    cursor = mydb.cursor()
    return [cursor,mydb]

def DBCreate():
    [cursor,mydb] = DBConnect()
    # Create an actual database
    cursor.execute("CREATE DATABASE IF NOT EXISTS second_db")
	# Create A Table for User Data
    cursor.execute("""CREATE TABLE if not exists UserData(
	username VARCHAR(20),
    password VARCHAR(20),
    name VARCHAR(20),
    phone VARCHAR(15),
    company1 VARCHAR(20),
    comp1num VARCHAR(5),
    company2 VARCHAR(20),
    comp2num VARCHAR(5)
   	)""")
    # Create a Table for Tracking Data
    cursor.execute("""CREATE TABLE if not exists TrackingData(
	tripID VARCHAR(40),
    company VARCHAR(20),
    carnum VARCHAR(5),
    destinationXstatus VARCHAR(20),
    passengersXtotalTime VARCHAR(20),
    cargoXtotalDist VARCHAR(20),
   	gpslonXworkingFuel VARCHAR(20),
    gpslat VARCHAR(20),
    time VARCHAR(30)
    )""")
    # Save Changes
    mydb.commit()
	# Close our connection
    mydb.close()

def DBClearUsers():
    [cursor, mydb] = DBConnect()
    # Clear Data
    query = "truncate UserData"
    cursor.execute(query)
    # Save Changes
    mydb.commit()
	# Close our connection
    mydb.close() 

def DBClearTracking():
    [cursor, mydb] = DBConnect()
    # Clear Data
    query = "truncate TrackingData"
    cursor.execute(query)
    # Save Changes
    mydb.commit()
	# Close our connection
    mydb.close() 

def DBDelete():
    [cursor, mydb] = DBConnect()
    #cursor.execute("DROP TABLE UserData")
    cursor.execute("DROP TABLE TrackingData")

def DBShowAll():
    [cursor,mydb] = DBConnect()
    # Grab records from database
    cursor.execute("SELECT * FROM UserData")
    records = cursor.fetchall()
    print("\nUser Data Data Base")
    for row in records:
        print(row)
    cursor.execute("SELECT * FROM TrackingData")
    records = cursor.fetchall()
    print("\n")
    print("\nTracking Data Data Base")
    for row in records:
        print(row)
    print("\n")
    # Save Changes
    mydb.commit()
	# Close our connection
    mydb.close()
 
def DBCheckUsernameExists(username):
    if(username == ''):
        return "Username Invalid"
    else:
        [cursor, mydb] = DBConnect()
        query = "SELECT * FROM UserData WHERE username = '{}'".format(username)
        cursor.execute(query)
        test = cursor.fetchone()
        mydb.commit()
	    # Close our connection
        mydb.close()
        try: 
            test[0]
        except: # If this phone is unused
            return "Valid"
        else: # If this phone is already in the database
            return "This username is already in use. Please choose another username."

def DBCheckPhoneExists(phone):
    try:
        int(phone)
    except: 
        return "Phone Number Invalid"
    else:
        [cursor, mydb] = DBConnect()
        query = "SELECT * FROM UserData WHERE phone = '{}'".format(phone)
        cursor.execute(query)
        test = cursor.fetchone()
        mydb.commit()
	    # Close our connection
        mydb.close()
        try: 
            test[0]
        except: # If this phone is unused
            return "Valid"
        else: # If this phone is already in the database
            return "This phone number is already in use"
    
def DBRegister(username, password, name, phone, company1, comp1num, company2, comp2num):
    [cursor, mydb] = DBConnect()
    query = "INSERT INTO UserData (username, password, name, phone, company1, comp1num, company2, comp2num) values ('{}','{}','{}','{}','{}','{}','{}','{}')".format(username, password, name, phone, company1, comp1num, company2, comp2num)
    cursor.execute(query)
    # Save Changes
    mydb.commit()
	# Close our connection
    mydb.close()

def DBLogin(username,password):
    [cursor, mydb] = DBConnect()
    query = "SELECT * FROM UserData WHERE username = %s AND password = %s"
    cursor.execute(query, (username,password))
    # Checks for a line where the username and password match those input
    try:
        test = cursor.fetchone()
        username = test[0]
    except: # If no line matching is found
        return(False)
    else: # If a matching line is found
        account = test
        localDBLogin(account[0], account[1], account[2], account[3], account[4], account[5], account[6], account[7])
        return(True)

def DBPullUserData():
    [cursor, mydb] = DBConnect()
    query = "SELECT * FROM UserData WHERE username = '{}'".format(currentUser)
    cursor.execute(query)
    records = cursor.fetchone()
    # Save Changes
    mydb.commit()
	# Close our connection
    mydb.close()
    return records

def DBUploadDataPoint(tripID, company, carnum, destination, passengers, cargo, gpslon, gpslat, time):
    [cursor, mydb] = DBConnect()
    query = "INSERT INTO TrackingData (tripID, company, carnum, destinationXstatus, passengersXtotalTime, cargoXtotalDist, gpslonXworkingFuel, gpslat, time) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(tripID, company, carnum, destination, passengers, cargo, gpslon, gpslat, time)
    cursor.execute(query)
    # Save Changes
    mydb.commit()
	# Close our connection
    mydb.close()

def DBCheckConnection():
    try:
        [cursor, mydb] = DBConnect()
        query = "SELECT * FROM UserData WHERE username = '{}'".format(currentUser)
        cursor.execute(query)
        records = cursor.fetchone()
        mydb.commit()
        mydb.close()
    except:
        return False
    else:
        return True

def DBGetDayStats(username, date):
    dayID = "%{}{}%".format(username, date)
    [cursor, mydb] = DBConnect()
    query = "SELECT passengersXtotalTime,cargoXtotalDist,gpslonXworkingFuel,time FROM TrackingData WHERE destinationXstatus = 'End Trip' AND tripID LIKE '{}'".format(dayID)
    cursor.execute(query)
    trips = cursor.fetchall()
    numTrips = 0
    totalDist = 0
    totalTime = timedelta()
    totalFuel = 0
    for row in trips:
        numTrips += 1
        totalDist += float(row[1])
        t = datetime.strptime(str(row[0]),'%H:%M:%S.%f')
        totalTime = totalTime + timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
        totalFuel += float(row[2])
        endTime = datetime.strptime(str(row[3]),'%Y-%m-%d %H:%M:%S.%f')
    query = "SELECT time FROM TrackingData WHERE destinationXstatus = 'Start Trip' AND tripID LIKE '{}'".format(dayID)
    cursor.execute(query)
    dayStart = datetime.strptime(str(cursor.fetchone()[0]),'%Y-%m-%d %H:%M:%S.%f')
    idleTime = endTime - dayStart - totalTime
    return [numTrips, totalDist, totalFuel, totalTime, idleTime]
        
    

def localDBConnect():
    localdb = sqlite3.connect('local_db.db')
    cursor = localdb.cursor()
    return [cursor, localdb]

def localDBCreate():
    [cursor, localdb] = localDBConnect()
    cursor.execute("""CREATE TABLE if not exists accountData(
	username VARCHAR(20),
    password VARCHAR(20),
    name VARCHAR(20),
    phone VARCHAR(15),
    company1 VARCHAR(20),
    comp1num VARCHAR(5),
    company2 VARCHAR(20),
    comp2num VARCHAR(5)
   	)""")
    cursor.execute("""CREATE TABLE if not exists tripData(
	tripID VARCHAR(40),
    company VARCHAR(20),
    carnum VARCHAR(5),
    destinationXstatus VARCHAR(20),
    passengersXtotalTime VARCHAR(20),
    cargoXtotalDist VARCHAR(20),
   	gpslonXworkingFuel VARCHAR(20),
    gpslat VARCHAR(20),
    time VARCHAR(30)
   	)""")
    localdb.commit()
    localdb.close()

def localDBDelete():
    [cursor, localdb] = localDBConnect()
    #cursor.execute("DROP TABLE accountData")
    cursor.execute("DROP TABLE tripData")

def localDBShowAll():
    [cursor,localdb] = localDBConnect()
    # Grab records from database
    cursor.execute("SELECT * FROM accountData")
    records = cursor.fetchall()
    print("\nAccount Data Data Base")
    for row in records:
        print(row)
    cursor.execute("SELECT * FROM tripData")
    records = cursor.fetchall()
    print("\n")
    print("\nTrip Data Data Base")
    for row in records:
        print(row)
    print("\n")
    # Save Changes
    localdb.commit()
	# Close our connection
    localdb.close() 
 
def localDBLogin(username, password, name, phone, company1, comp1num, company2, comp2num):
    [cursor, localdb] = localDBConnect()
    localDBLogOut()
    query = "INSERT INTO accountData (username, password, name, phone, company1, comp1num, company2, comp2num) values ('{}','{}','{}','{}','{}','{}','{}','{}')".format(username, password, name, phone, company1, comp1num, company2, comp2num)
    cursor.execute(query)
    # Save Changes
    localdb.commit()
	# Close our connection
    localdb.close()
 
def localDBPullAccountData():
    [cursor, localdb] = localDBConnect()
    query = "SELECT * FROM accountData"
    cursor.execute(query)
    records = cursor.fetchone()
    # Save Changes
    localdb.commit()
	# Close our connection
    localdb.close()
    return records
         
def localDBLogOut():
    [cursor, localdb] = localDBConnect()
    # Clear Data
    query = "DELETE FROM accountData"
    cursor.execute(query)
    # Save Changes
    localdb.commit()
	# Close our connection
    localdb.close()  

def localDBClearTrip():
    [cursor, localdb] = localDBConnect()
    # Clear Data
    query = "DELETE FROM tripData"
    cursor.execute(query)
    # Save Changes
    localdb.commit()
	# Close our connection
    localdb.close() 

def localDBRecord(username, company, carnum, destination, passengers, cargo, gpslon, gpslat, time):
    [cursor, localdb] = localDBConnect()
    query = "INSERT INTO tripData (tripID, company, carnum, destinationXstatus, passengersXtotalTime, cargoXtotalDist, gpslonXworkingFuel, gpslat, time) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(username, company, carnum, destination, passengers, cargo, gpslon, gpslat, time)
    cursor.execute(query)
    # Save Changes
    localdb.commit()
	# Close our connection
    localdb.close()
    localDBShowAll()

def localDBDumptoServer():
    [cursor, localdb] = localDBConnect()
    cursor.execute("SELECT * FROM tripData")
    records = cursor.fetchall()
    for row in records:
        DBUploadDataPoint(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
    # Save Changes
    localdb.commit()
	# Close our connection
    localdb.close()
    # Clear local data
    localDBClearTrip()

def localDBPullTripCoords(tripID):
    [cursor, localdb] = localDBConnect()
    query = "SELECT gpslonXworkingFuel, gpslat FROM tripData WHERE tripID = '{}' AND destinationXstatus != 'Start Trip' AND destinationXstatus != 'End Trip'".format(tripID)
    cursor.execute(query)
    coords = cursor.fetchall()
    # Save Changes
    localdb.commit()
	# Close our connection
    localdb.close()
    return coords

def localDBGetTripStart(tripID): 
    [cursor, localdb] = localDBConnect()
    query = "SELECT time FROM tripData WHERE tripID = '{}' AND destinationXstatus = 'Start Trip'".format(tripID)
    cursor.execute(query)
    time = datetime.strptime(str(cursor.fetchone()[0]),'%Y-%m-%d %H:%M:%S.%f')
    return time

def localDBGetTripStats(tripID):
    [cursor, localdb] = localDBConnect()
    query = "SELECT passengersXtotalTime,cargoXtotalDist,destinationXstatus FROM tripData WHERE destinationXstatus != 'End Trip' AND destinationXstatus != 'Start Trip' AND tripID = '{}'".format(tripID)
    cursor.execute(query)
    tripData = cursor.fetchone()
    query = "SELECT passengersXtotalTime,cargoXtotalDist,gpslonXworkingFuel FROM tripData WHERE destinationXstatus = 'End Trip' AND tripID = '{}'".format(tripID)
    cursor.execute(query)
    endData = cursor.fetchone()
    totalDist = endData[1]
    t = datetime.strptime(str(endData[0]),'%H:%M:%S.%f')
    totalTime = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
    totalFuel = endData[2]
    try:
        passengers = "{} with {}".format(tripData[0], tripData[1])
        destination = tripData[2]
    except:
        passengers = "Trip Too Short"
        destination = "Trip Too Short"
    return [destination, passengers, totalDist, totalTime, totalFuel]



def onLaunch():
    global currentUser
    global currentCompany
    global currentCar
    global currentDest
    global currentPass
    global currentCargo
    global currentTripID
    try:
        currentUser = localDBPullAccountData()[0]
    except:
        currentUser = ''
    currentCompany = ''
    currentCar = ''
    currentDest = ''
    currentPass = ''
    currentCargo = ''
    currentTripID = ''

def startTrip():
    now = datetime.now()
    global currentTripID
    currentTripID = '{}{}{}{}{}{}{}'.format(currentUser, now.year, now.month, now.day, now.hour, now.minute, now.second)
    localDBRecord(currentTripID, currentCompany, currentCar, 'Start Trip', 0, 0, 0, 0, now)

def getTripDistance(tripID):
    coords = localDBPullTripCoords(tripID)
    totalDist = 0
    rowNum = 0
    global lon1, lat1, lon2, lat2
    for row in coords:
        if(rowNum < 1):
            lon1 = radians(float(row[0]))
            lat1 = radians(float(row[1]))
        else:
            lon2 = radians(float(row[0]))
            lat2 = radians(float(row[1]))
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            R = 3958.8 # radius of earth in miles
            d = R * c
            if(d >= (minMph*checkFrequency/3600)): # prevents movements smaller than minMph average speed to not be recorded 
                totalDist += d
            lon1 = lon2
            lat1 = lat2
        rowNum += 1
    return totalDist



class Welcome(Screen):            
    def logIn(self, username, password):
        if(DBCheckConnection()):
            if DBLogin(username, password):
                self.ids.Incorrect.text = ''
                self.ids.Username.text = ''
                self.ids.Password.text = ''
                self.manager.current = "Home" # sets the window to the window with the name given
                self.manager.transition.direction = "up"  # sets transition direction
                global currentUser
                currentUser = str(username)
            else:
                self.ids.Incorrect.text = 'Invalid Username or Password'
        else:
            self.ids.Incorrect.text = 'Connection Required to Log In'
       
class Home(Screen):
    def logOut(self):
        global currentUser
        global currentCompany
        global currentCar
        global currentDest
        global currentPass
        global currentCargo
        global currentTripID
        currentUser = ''
        currentCompany = ''
        currentCar = ''
        currentDest = ''
        currentPass = ''
        currentCargo = ''
        currentTripID = ''
        localDBLogOut()

class HomeStatsPage(Screen):
    def on_pre_enter(self):
        if(DBCheckConnection()):
            try:
                statistics = DBGetDayStats(currentUser, datetime.today().strftime("%Y%m%d"))
                self.ids.NumberOfTrips.text = "{} Trips".format(statistics[0])
                self.ids.MilesDriven.text = "{} Miles".format(statistics[1])
                self.ids.EstimatedGas.text = "{} Gallons".format(statistics[2])
                hours = int(statistics[3].seconds/3600)
                minutes = int((statistics[3].seconds-hours*3600)/60)
                seconds = int(statistics[3].seconds - hours*3600 - minutes*60)
                self.ids.TotalTime.text = '{} Hours, {} Minutes, {} Seconds'.format(hours, minutes, seconds)
                hours = int(statistics[4].seconds/3600)
                minutes = int((statistics[4].seconds-hours*3600)/60)
                seconds = int(statistics[4].seconds - hours*3600 - minutes*60)
                self.ids.TimeBetween.text = '{} Hours, {} Minutes, {} Seconds'.format(hours, minutes, seconds)
            except:
                self.ids.NumberOfTrips.text = "No Data Available"
                self.ids.MilesDriven.text = "No Data Available"
                self.ids.EstimatedGas.text = "No Data Available"
                self.ids.TotalTime.text = "No Data Available"
                self.ids.TimeBetween.text = "No Data Available"
        else:
            self.ids.NumberOfTrips.text = "Connection Required"
            self.ids.MilesDriven.text = "Connection Required"
            self.ids.EstimatedGas.text = "Connection Required"
            self.ids.TotalTime.text = "Connection Required"
            self.ids.TimeBetween.text = "Connection Required"

class Register1(Screen):        
    def checkRegPg1(self, username, phone):
        if(DBCheckConnection()):
            if(DBCheckUsernameExists(username) != "Valid"):
                self.ids.Incorrect.text = DBCheckUsernameExists(username)
            elif(DBCheckPhoneExists(phone) != "Valid"):
                self.ids.Incorrect.text = DBCheckPhoneExists(phone)
            else:
                self.manager.current = "Register2" # sets the window to the window with the name given
                self.manager.transition.direction = "up" # sets transition direction    
        else:
            self.ids.Incorrect.text = "Connection Required to Register New Account"
   
class Register2(Screen):
    def register(self, username, password, name, phone, comp1, car1, comp2, car2):
        if(DBCheckConnection()):
            DBRegister(username, password, name, phone, comp1, car1, comp2, car2)
            self.manager.get_screen('Register1').ids.UsernameReg.text = ''
            self.manager.get_screen('Register1').ids.PasswordReg.text = ''
            self.manager.get_screen('Register1').ids.NameReg.text = ''
            self.manager.get_screen('Register1').ids.PhoneReg.text = ''
            self.ids.Company1Reg.text = ''
            self.ids.Car1NumReg.text = ''
            self.ids.Company2Reg.text = ''
            self.ids.Car2NumReg.text = ''
            self.manager.current = "Welcome"# sets the window to the window with the name given
            self.manager.transition.direction = "up" # sets transition direction
        else:
            self.ids.Incorrect.text = "Connection Required to Register New Account"

class StartTrip(Screen):
    def on_pre_enter(self):
        userData = localDBPullAccountData()
        self.ids.car1.text = "{} {}".format(userData[4], userData[5])
        self.ids.car2.text = "{} {}".format(userData[6], userData[7])
        if(userData[6] != ''):
            self.ids.car2.disabled = False
            self.ids.car2.opacity = 100
        else:
            self.ids.car2.disabled = True
            self.ids.car2.opacity = 0
        
    
    def selectCar(self, companyNum):
        global currentCompany
        global currentCar
        userData = localDBPullAccountData()
        currentCompany = userData[2*companyNum+2]
        currentCar = userData[2*companyNum+3]
        
    def getCarLabel(self, companyNum):
        userData = localDBPullAccountData()       
        try:
            return("{} {}".format(userData[2*companyNum+2], userData[2*companyNum+1+3]))
        except:
            return "None"
        
    def clearCar(self):
        global currentCompany
        currentCompany = ''

class Destination(Screen):
    def setDest(self, destination):
        global currentDest
        currentDest = destination
        
    def clearCar(self):
        global currentCompany
        currentCompany = ''
    
class People(Screen):
    def setPass(self, people):
        global currentPass
        currentPass = people
        
    def clearDest(self):
        global currentDest
        currentDest = ''

class Cargo(Screen):
    def setCargo(self, cargo):
        global currentCargo
        currentCargo = cargo
        
    def clearPeople(self):
        global currentPass
        currentPass = ''

class FinishTrip(Screen):
    def on_enter(self):
        try:
            MainApp().startGPS(checkFrequency)
        except:
            Logger.critical("GPS Not Enabled on This Device")
        startTrip()
    
    def endTrip(self):
        try:
            MainApp().stopGPS()
        except:
            Logger.critical("GPS Not Set Up on This Device")
        now = datetime.now()
        dist = round(getTripDistance(currentTripID),3) # rounds to the nearest 5ft
        tripTime = now - localDBGetTripStart(currentTripID)
        tripFuel = round(dist/mpg, 3)
        localDBRecord(currentTripID, currentCompany, currentCar, 'End Trip', tripTime, dist, tripFuel, '', now)
    
    def clearCargo(self):
        global currentCargo
        global currentTripID
        self.endTrip()
        currentCargo = ''
        currentTripID = ''
        
class TripStats(Screen):
    def on_enter(self):
        statistics = localDBGetTripStats(currentTripID)
        self.ids.Destination.text = str(statistics[0])
        self.ids.PassengersCargo.text = str(statistics[1])
        self.ids.tripDist.text = "{} Miles".format(statistics[2])
        hours = int(statistics[3].seconds/3600)
        minutes = int((statistics[3].seconds-hours*3600)/60)
        seconds = int(statistics[3].seconds - hours*3600 - minutes*60)
        self.ids.tripTime.text = '{} Hours, {} Minutes, {} Seconds'.format(hours, minutes, seconds)
        self.ids.tripFuel.text = "{} Gallons".format(statistics[4])
    
    def on_pre_leave(self):
        if(DBCheckConnection()):
            localDBDumptoServer()
        
    def clearCurrent(self):
        global currentTripID
        global currentCompany
        global currentCar
        global currentDest
        global currentPass
        global currentCargo
        currentCompany = ''
        currentCar = ''
        currentDest = ''
        currentPass = ''
        currentCargo = ''
        currentTripID = ''
        
class Loading(Screen):
    pass
        
class WindowManager(ScreenManager):
    pass

class MainApp(App):
    def build(self):
        return kv
    
    def on_start(self):
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.INTERNET, Permission.ACCESS_BACKGROUND_LOCATION, Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])
        localDBCreate()
        localDBLogin('testUser', 'testPassword', 'Test User', '1234567890', 'Company1', '1', 'Company2', '2') # DELETE ONCE LOGIN IS POSSIBLE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        onLaunch()  
        kv.transition = NoTransition()
        try:
            username = localDBPullAccountData()[0]
            if(username != ''):
                kv.current = "Home"
            else:
                kv.current = "Welcome"
        except:
            kv.current = "Welcome"
        kv.transition = SlideTransition()    

        
    def on_gps_location(self, **kwargs):
        global currentlat
        global currentlon
        currentlat = kwargs['lat']
        currentlon = kwargs['lon']
        now = datetime.now()
        localDBRecord(currentTripID, currentCompany, currentCar, currentDest, currentPass, currentCargo, currentlon, currentlat, now)

        
    def on_request_close(self):
        self.root.get_screen("FinishTrip").root.endTrip()
        return True
        
    def startGPS(self, seconds):
        try:
            gps.configure(on_location=self.on_gps_location,on_status=None)
            gps.start(seconds*1000,0) # gathers location every 'seconds' seconds minimum and 0 meters minimum
        except:
            Logger.critical("GPS Not On This Device")
            
    def stopGPS(self):
        gps.stop()
        global currentlat
        global currentlon
        currentlat = 0
        currentlon = 0
    
    def handle_checkbox_active(self, is_checked):
        if is_checked:
            # The CheckBox is checked, show the additional questions or elements
            self.root.get_screen('Register2').ids.CarCompanyTwo.opacity = 1
            self.root.get_screen('Register2').ids.Company2Reg.opacity = 1
            self.root.get_screen('Register2').ids.CarNumberTwo.opacity = 1
            self.root.get_screen('Register2').ids.Car2NumReg.opacity = 1
        else:
            # The CheckBox is unchecked, hide the additional questions or elements
            self.root.get_screen('Register2').ids.CarCompanyTwo.opacity = 0
            self.root.get_screen('Register2').ids.Company2Reg.opacity = 0
            self.root.get_screen('Register2').ids.CarNumberTwo.opacity = 0
            self.root.get_screen('Register2').ids.Car2NumReg.opacity = 0   


# load the kivy file
kv = Builder.load_file('GalapagosCarTracking.kv')
# run the application
if __name__=='__main__':
    MainApp().run()