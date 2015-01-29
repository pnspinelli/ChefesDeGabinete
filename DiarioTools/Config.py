#!/usr/bin/python
#coding: utf-8
from Log import *
from xml.etree.ElementTree import *
import os
import re
import getopt

validConfig = False
def IfValidConfig(func):
    def decorated(*args, **kwargs):	
	if validConfig:
	    return func(*args, **kwargs)
    return decorated

class Configuration(object):
    """ Basic configuration. Read from xml and make available in config instance"""
    def __init__(self,configFileName, args):
	self.destination = []
	self._ProcessConfigFile(configFileName)
	self._ProcessArgs(args)
	
    def _ProcessArgs(self, args):
	self.startDate = None
	self.endDate = None
	opts = getopt.getopt(args[1:], "s:e:h")
	for opt, value in opts[0]:
	    if opt == "-s":
		date = self._ParseDate(value)
		if date is not None:
		    self.startDate = date
	    if opt == "-e":
		date = self._ParseDate(value)
		if date is not None:
		    self.endDate = date
	    if opt == "-h":
		Log.Log("""Uso: """ + args[0] + """ [-s data -e data]

Argumentos:
-s	Data inicial
-e	Data final""")
		exit(0)

	if self.startDate == None and self.endDate != None:
	    Log.Warning("Data final especificada sem data initial")
	    exit(1)

	if self.startDate != None and self.endDate == None:
	    Log.Warning("Data inicial especificada sem data final")
	    exit(1)

	if self.startDate is not None:
	    self.mode = "local search"
	else:
	    self.mode = "alert mode"

    def _ParseDate(self, date):
	retDate = None
	dateRe = re.search("(\d{2})/(\d{2})/(\d{4})", date)
	if dateRe is not None:
	    retDate = dateRe.group(3) + "-" + dateRe.group(2) + "-" + dateRe.group(1) + "T00:00:00.000Z"
	return retDate

    def _ProcessConfigFile(self, configFileName):
	global validConfig 
	if os.path.exists(configFileName):
	    try:
		tree = parse(configFileName)
		self.username = tree.find("./User").text
		self.password = tree.find("./Password").text
		self.frommail = tree.find("./From").text		
		self.subject = tree.find("./Subject").text
		self.header = tree.find("./Header").text
		self.footer = tree.find("./Footer").text
		self.baseDate = tree.find("./BaseDate").text
		self.proxy = tree.find("./Proxy").text
		self.logName = tree.find("./LogName").text
		self.timeout = float(tree.find("./Timeout").text)
		self.retries = int(tree.find("./Retries").text)
		self.timeBetweenRetries = float(tree.find("./TimeBetweenRetries").text)
		self._ProcessCleanLogs(tree.find("./LogMode").text, self.logName)		
		
		emails = tree.findall("./To/Email")
		for email in emails:
		    self.AddDestination(email.text)
		
		validConfig = True
	    except Exception as ex:
		Log.Warning("Erro de processamento do arquivo de configuração: " + str(ex))
		exit(1)
	else:
	    Log.Warning("Arquivo de configuração não encontrado")
	    exit(1)

    def _ProcessCleanLogs(self, logMode, logName):
	if re.search("Overwrite", logMode, re.I) is not None:
	    if os.path.exists(logName):
		os.remove(logName)

    def AddDestination(self, email):
	self.destination.append(email)
