
import time
import threading
from pylogix import PLC

# Set to True after configuring "configureKeyboardInput" to shim/simulate specific
# tag changes without needing to run the PLC system.
# useKeyboardInputForScans = True
useKeyboardInputForScans = False

# IP address for the PLC to poll
PLCIP = "192.168.1.1"

# Sleep delay used in the polling daemon thread; float, so can be less than 1.0 wanted.
pollingDelaySeconds = 2

# Set requestAll to True to have the script initially request and print all tags - 
# useful for learning about the system configuration and discovering what tags exist.
# requestAll = True
requestAll = False

PLCPollDaemon = None

# Tags to monitor every pollingDelay seconds - this is the master list of tags to
#  poll the PLC about:
PLCTagsToMonitor = ['Weight_Right_Kg',
					'Weight_Left_Kg',
					'ToRlyPC_QR_Left_timestamp',]

# Tags to specifically act on.
PLCTagsToActOn = ['Weight_Right_Kg',
					'Weight_Left_Kg',]

# Tags that will not be printed to terminal for changes - timestamps, etc.
PLCTagsToNotAlertOn = []





# Tags to populate initially - not currently used.
PLCTagsToPopulate = ['LEFT_RAMP_CAR_NUMBER',
					'Right_Ramp_Car_Number',
					'Left_Ramp_Step_Pointer',]
# Tags that will always be acted on, even with no change - not currently used.
PLCTagsToAlwaysActOn = ['New_QR_Code_Left',
					'New_QR_Code_Right',]


# Empty list and object for storing tags:
changedTags = []
lastMonitorVals = {"PLC": {}}

for tag in PLCTagsToMonitor:
	lastMonitorVals["PLC"][tag] = None

def daemonizer():
	while True:
		# print("Daemonizer looped!")
		time.sleep(5)


def PLCTagPoller():
	while True:
		updatePLCTags()
		time.sleep(pollingDelaySeconds)


def updatePLCTags():
	"""A function that queries the PLC for the current values of all tags
	in PLCTagsToMonitor then, filters them to a minor extent, then passes
	all changed tags to actOnChangedTags"""

	changedTags = []

	with PLC(PLCIP) as PLCComm:
		for tag in PLCTagsToMonitor:
			tempTestVal = PLCComm.Read(tag).Value
			lastVal = lastMonitorVals["PLC"][tag]
			if lastVal == None:
				lastMonitorVals["PLC"][tag] = tempTestVal
			if (lastVal != None) and (tempTestVal != None) and (lastVal != tempTestVal):
				if tag not in PLCTagsToNotAlertOn:
					print("PLC tag changed! Tag: {}; old value: {}; new value: {}".format(tag, lastVal, tempTestVal))
				else:
					# print("Tag not alerted due to being in assemTagsToNotAlertOn.")
					pass
				if tag == "ToRlyPC_Fault":
					# assemComm.Write()
					pass
				lastMonitorVals["PLC"][tag] = tempTestVal
				changedTags.append({"tag": tag, "newVal": tempTestVal})
			if (lastVal != None) and (tempTestVal != None) and (lastVal == tempTestVal):
				# print("Tag did not change! : {}".format(tag))
				pass


	if changedTags:
		actOnChangedTags(changedTags)

def actOnChangedTags(newTags):
	"""A function that takes in a list of newTags, pops them out one by one,
	then processes them - checks if they need to be acted on, and if so,
	performs whatever actions are defined."""

	while newTags:
		# print(newTags)
		tempTag = newTags.pop()
		# print(tempTag)
		if tempTag["tag"] in PLCTagsToActOn:
			if tempTag["tag"] == "Controller_Date_Time_Str":
				# print(tempTag["newVal"])
				pass

			# if tempTag["tag"] == "ToRlyPC_QRcode":
			# 	print(tempTag["newVal"])
			# 	assemValues["qrCode"] = tempTag["newVal"]

			# if tempTag["tag"] == "ToRlyPC_Fault":
			# 	print(tempTag["newVal"])
			# 	assemValues["proctor"] = tempTag["newVal"]

			# if tempTag["tag"] == "ToRlyPC_NewCycleStarted":
			# 	print(tempTag["newVal"])
			# 	if tempTag["newVal"] == True:
			# 		assemValues["assembling"] = True

			# if tempTag["tag"] == "ToRlyPC_CarComplete":
			# 	print(tempTag["newVal"])
			# 	if tempTag["newVal"] == True:
			# 		assemValues["assembling"] = False

			# match tempTag["tag"]:

			# 	case 'LEFT_RAMP_CAR_NUMBER':
			# 		trackValues["left"]["carNumber"] = tempTag["newVal"]

			# 	case 'Right_Ramp_Car_Number':
			# 		trackValues["right"]["carNumber"] = tempTag["newVal"]

			# 	case 'Left_Ramp_Step_Pointer':
			# 		trackValues["left"]["step"] = tempTag["newVal"]

			# 	case 'Right_Ramp_Step_Pointer':
			# 		trackValues["right"]["step"] = tempTag["newVal"]

			# 	case 'At_Right_Lowd_Latch':
			# 		if tempTag["newVal"] is True:
			# 			trackValues["right"]["ramp-position"] = "low"

			# 	case 'At_Right_Mid_Latch':
			# 		if tempTag["newVal"] is True:
			# 			trackValues["right"]["ramp-position"] = "mid"

			# 	case 'At_Right_Raised_Latch,':
			# 		if tempTag["newVal"] is True:
			# 			trackValues["right"]["ramp-position"] = "high"

			# 	case 'At_Left_Mid_Latch':
			# 		if tempTag["newVal"] is True:
			# 			trackValues["left"]["ramp-position"] = "mid"

			# 	case 'At_Left_Lowd_Latch':
			# 		if tempTag["newVal"] is True:
			# 			trackValues["left"]["ramp-position"] = "low"

			# 	case 'At_Left_Raised_Latch':
			# 		if tempTag["newVal"] is True:
			# 			trackValues["left"]["ramp-position"] = "high"



def convertKeyboardInput(inputValue):
	keyChart = ["axle",
				"wheel-smooth",
				"wheel-toothed",
				"wheel-knurled",
				"wheel-o-ring",
				"gearbox-high",
				"gearbox-low",
				"belts-1",
				"battery-pack",
				"cart-clear",
				"cart-finish",
				"belts-2",
				"belts-3",
				"belts-4",
				"chassis",
				"weight-box"]

	if len(inputValue) == 0:
		return

	if inputValue in "0123456789":
		if int(inputValue) < len(keyChart):
			qrCodeScannerHandler(keyChart[int(inputValue)])
	else:
		charVal = 10
		if inputValue == "a":
			charVal = 10
		elif inputValue == "b":
			charVal = 11
		elif inputValue == "c":
			charVal = 12
		elif inputValue == "d":
			charVal = 13
		elif inputValue == "e":
			charVal = 14
		elif inputValue == "f":
			charVal = 14
		elif inputValue == "g":
			charVal = 14
		elif inputValue == "h":
			charVal = 15

	print(str(charVal))



def main():
	print("start")

	PLCPollDaemon = threading.Thread(target=PLCTagPoller, daemon=False)
	PLCPollDaemon.start()

	if requestAll:
		with PLC(PLCIP) as PLCComm:
			allPLCTags = PLCComm.GetTagList()


		for tagName in allPLCTags.Value:
			print(tagName.TagName)




	if useKeyboardInputForScans:
		while True:
			inputKey = input("Type a character from [0-9,a-h] followed by Enter to fake a QR code scan:")
			convertKeyboardInput(inputKey)



if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\nExiting\n")
		# Doesn't seem to exit, probably from the threads running...
		exit()
