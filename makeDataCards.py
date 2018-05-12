from Framework.Core import *
import argparse,os

textFilePath = "/afs/cern.ch/user/y/yduh/public/lucien/qua.txt"

process = [
		"vjets",
		"qcd",
		"ttsig",
		"st",
		]

systematics = [
		lnNSystematic("btag"	,["ttsig"]	,[1.03]),
		lnNSystematic("ltag"	,["ttsig"]	,[1.005]),
		lnNSystematic("jer"		,["ttsig"]	,[1.004]),
		lnNSystematic("met"		,["ttsig"]	,[1.005]),
		lnNSystematic("pu"		,["ttsig"]	,[1.008]),
		lnNSystematic("tune"	,["ttsig"]	,[1.01]),
		lnNSystematic("bdecay"	,["ttsig"]	,[1.03]),
		lnNSystematic("isr"		,["ttsig"]	,[1.015]),
		lnNSystematic("hvj"		,["vjets"]	,[1.30]),
		lnNSystematic("hvqcd"	,["qcd"]	,[1.30]),
		ShapeSystematic("jes"	,["ttsig"]),
		ShapeSystematic("fs"	,["ttsig"]),
		ShapeSystematic("rs"	,["ttsig"]),
		ShapeSystematic("hdamp"	,["ttsig"]),
		ShapeSystematic("mt"	,["ttsig"]),
		ShapeSystematic("bfrag"	,["ttsig"]),
		#"pdf",
		#"fsr",
		#"hadro",
		#"NLO",
		]

parser = argparse.ArgumentParser()
parser.add_argument('--inputPath',action='store')
parser.add_argument('--outputDir',action='store')

option = parser.parse_args()

rootFileReader = RootFileReader()
rootFileReader.readFile(option.inputPath)
binCollection = rootFileReader.createBinCollection(process,systematics)
textFileReader = TextFileReader()
textFileReader.readTextFile(textFilePath,binCollection)

if not os.path.exists(option.outputDir):
	os.makedirs(option.outputDir)

for ibin,anaBin in binCollection.iteritems():
	dataCard = DataCard(anaBin)
	dataCard.makeCard(option.outputDir)
	dataCard.makeRootFile(option.outputDir)

rootFileReader.cleanUp()
