from Gpib import *
import time
import numpy

class PM33xx:

	probeIndexList={'1:1':0,'10:1':1,'20:1':2,'50:1':3,'100:1':4}

	def __init__(self, address):
		self.PRIMARY_ADDR = 30
		self.SECONDARY_ADDR = 0

		self.conn = Gpib(0,self.PRIMARY_ADDR,self.SECONDARY_ADDR+96)

	def sign_extend(self, value, bits):
		sign_bit = 1 << (bits - 1)
		return (value & (sign_bit - 1)) - (value & sign_bit)		

	def configure(self, configuration):
		self.configuration=configuration
		self.SAMPLE_BITS = self.configuration['trace']['resolution']
		self.NUM_SAMPLES = self.configuration['trace']['samples']

		#reset scope to a known state
		self.conn.write("*RST")

		channelsSkipped = 0

		#set up timebase
		self.conn.write("*WAI;SENSe:SWEep:TIME "+str(self.configuration['timebase']['horDiv']*10))		

		#TODO: check wether to set for every channel or not, should be the same right?
		self.conn.write("*WAI;FORMat INTeger,"+str(self.SAMPLE_BITS))
		self.conn.write("*WAI;TRACe:POINts CH1,"+str(self.NUM_SAMPLES))
		self.conn.write("*WAI;TRACe:POINts CH2,"+str(self.NUM_SAMPLES))
		self.conn.write("*WAI;TRACe:POINts CH3,"+str(self.NUM_SAMPLES))
		self.conn.write("*WAI;TRACe:POINts CH4,"+str(self.NUM_SAMPLES))

		for channelConfig in sorted(self.configuration['channels']):
			#print("Configuring channel " + channelConfig)
			config = self.configuration['channels'][channelConfig]
			
			if config['on']:		
				self.conn.write("*WAI;SENSe:FUNCtion:ON \"XTIMe:VOLTage"+channelConfig+"\"")
				self.conn.write("*WAI;INPut"+channelConfig+":COUPling " + config['coupling'])
				self.conn.write("*WAI;SENSe:VOLTage"+channelConfig+":RANGe:PTPeak "+str(config['vertDiv']*8.0))
				self.conn.write("*WAI;INPut"+channelConfig+":IMPedance "+str(config['impedance']))
				
				if config['probe']!="1:1":
					#unfortunately probes can only be set via the menu, so keypressing stuff here		
					self.conn.write("*WAI;DISPlay:MENU UTIL")
					command = "*WAI;SYSTem:KEY 2;KEY 5"
					
					if int(channelConfig) != 1:
						command+=(channelsSkipped)*";KEY 2"

					probeIndex = self.probeIndexList[config['probe']]
					
					command += (probeIndex)*";KEY 4"

					#print(command)
					self.conn.write(command)
					self.conn.write("*WAI;DISPlay:MENU:STATe OFF")
					channelsSkipped=1
				else:
					channelsSkipped+=1			

				#end of setting probes
			else:
				self.conn.write("*WAI;SENSe:FUNCtion:OFF \"XTIMe:VOLTage"+channelConfig+"\"")
				channelsSkipped+=1

		#make sure channel1 is again selected in menu and switch off menu		
		if channelsSkipped != 4:
			self.conn.write("*WAI;DISPlay:MENU UTIL")
			command = "*WAI;SYSTem:KEY 2;KEY 5"
			command+=(channelsSkipped)*";KEY 2"	
			self.conn.write(command)	
			self.conn.write("*WAI;DISPlay:MENU:STATe OFF")

		#set up trigger
		self.conn.write("*WAI;TRIGger:SOURce INTernal"+str(self.configuration['trigger']['channel']))
		self.conn.write("*WAI;TRIGger:LEVel "+str(self.configuration['trigger']['level']))
		self.conn.write("*WAI;TRIGger:SLOPe "+str(self.configuration['trigger']['slope']))

	def initiate(self):
		self.conn.write("*WAI;INITiate")
		self.conn.write("*OPC")

	def checkForTrigger(self):
		self.conn.write("*ESR?")
		eventStatusRegister = (int(conn.read()) == 1)
		return eventStatusRegister

	def waitForTrigger(self):
		eventStatusRegister=False

		while(not eventStatusRegister):
			self.conn.write("*ESR?")
			eventStatusRegister = int(self.conn.read())
			#print("Waiting for trigger")
			time.sleep(0.001)

	def readTraces(self):
		traceList=[]

		for channelConfig in sorted(self.configuration['channels']):		

			if self.configuration['channels'][channelConfig]['on']:

				self.conn.write("TRACe? CH"+str(channelConfig))		
				raw_result = self.conn.read(2**(16+1))

				self.conn.write("SENSe:VOLTage"+str(channelConfig)+":RANGe:PTPeak?")
				Vpp = float(self.conn.read())
				self.conn.write("SENSe:VOLTage"+str(channelConfig)+":RANGe:OFFSet?")
				Voffset = float(self.conn.read())				

				length_indicator = int(raw_result[1])

				data = raw_result[3+length_indicator:3+length_indicator+(self.NUM_SAMPLES*(self.SAMPLE_BITS/8))]
				#print(len(data), raw_result[3], raw_result[4], raw_result[5])

				if self.SAMPLE_BITS == 16:
					numericData = []
					it = iter(data)
					for x in it:
						newData = ord(x)*256+ord(next(it))
						numericData.append(newData)		
				else:
					numericData = [ord(elem) for elem in data]

				trace = [-1*(float(self.sign_extend((elem ^ (2**self.SAMPLE_BITS-1)) + 1,self.SAMPLE_BITS)) / (200 * (256 if self.SAMPLE_BITS==16 else 1)) * Vpp - Voffset)  for elem in numericData]

			else:
				trace=[]

			traceList.append(trace)

		self.conn.write("SENSe:SWEep:TIME?")
		Tsweep = float(self.conn.read())
		Tsample = Tsweep / float(self.NUM_SAMPLES)
		print(Tsweep, Tsample)					

		timeScale = numpy.arange(0,Tsweep,Tsample)	

		return traceList,timeScale	
