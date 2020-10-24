import matplotlib.pyplot as plt
import numpy
from PM33xx import PM33xx

configuration={}

configuration['trace'] = {
					'resolution':8, #valid values: 8|16
					'samples':8192
				}		

configuration['trigger']  = {
					'channel':1,
					'level':0.025,	# Volt
					'slope':'NEG'	#valid values: POS[itive]|NEG[ative]|EITH[er]					
				}

configuration['timebase']  = {
					'horDiv':0.0002		#time in seconds	
				}

configuration['channels'] = {
				 '1':{	
						'on':True,
						'alias':'Sinewave',
					  	'coupling':'DC',    #valid values: AC|DC|GROund
					  	'vertDiv':0.02, 	#Volt per division
					  	'impedance':50,		#valid values: 50| 1E6
					  	'probe':'1:1'		#valid values: 1:1 | 10:1 | 20:1 | 50:1 | 100:1
					 },
				 '2':{	
				 		'on':True,
				 		'alias':'Probe calibration',
				 		'coupling':'AC',
				 		'vertDiv':0.25,
				 		'impedance':1E6,
				 		'probe':'1:1'
				 	 },
				 '3':{
				 		'on':True,
				 		'alias':'Floating',
				 		'coupling':'DC',
				 		'vertDiv':0.02,
				 		'impedance':1E6,
				 		'probe':'1:1'
				 	 },
				 '4':{
				 		'on':True,				 		
				 		'coupling':'DC',
				 		'vertDiv':0.125,
				 		'impedance':1E6,
				 		'probe':'1:1'
				 	},
				}


scope1 = PM33xx.PM33xx(30)

print("Configuring oscilloscope")
scope1.configure(configuration)

print("Starting measurement")
scope1.initiate()

print("Waiting for trigger")
scope1.waitForTrigger()

print("Reading traces")
traceList, timeScale = scope1.readTraces()

fig, ax = plt.subplots(figsize=(14,7))
ax.set_ylabel('Amplitude [V]')
ax.set_xlabel('Time [s]')

for channel in range(0,len(traceList)):
	if traceList[channel] != []:
		if 'alias' in configuration['channels'][str(channel+1)]:
			alias = configuration['channels'][str(channel+1)]['alias']
		else:
			alias = 'Channel ' + str(channel+1)

		ax.plot(timeScale,traceList[channel],label=alias)

legend = ax.legend()
plt.savefig('trace.png', bbox_inches='tight')









