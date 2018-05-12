class Systematic(object):
	def __init__(self,name,process):
		self.name = name
		self.process = process 
	
class lnNSystematic(Systematic):
	def __init__(self,name,process,magnitude):
		self.systType = "lnN"
		self.name = name
		self.process = process
		self.magnitude = magnitude
		self.systDict = {}
		for i,eachProcess in enumerate(process):
			self.systDict[eachProcess] = magnitude[i]

class ShapeSystematic(Systematic):
	def __init__(self,name,process):
		super(ShapeSystematic,self).__init__(name,process)
		self.systType = "shape"

	def getSystName(self):
		return self.name.replace("Up","").replace("Down","")





