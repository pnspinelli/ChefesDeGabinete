#!/usr/bin/python
#coding: utf-8
from Prodam import *
from Suspensas import *
from DiarioTools.GMailer import *
import datetime
import sys
import os

def HandleProdam(configInstance):
    searcher = SearchProdam(configInstance, True)
    parser = ParseProdam()
    processor = ProcessorProdam(configInstance, searcher, parser, configInstance.logName, "Prodam")    
    return processor.Process()

def HandleSuspensas(configInstance):
    searcher = SearchSuspensas(configInstance, True)
    parser = ParseSuspensas()
    processor = ProcessorSuspensas(configInstance, searcher, parser, configInstance.logName, "Suspensas")    
    return processor.Process()

def Run():

	config = Configuration(os.path.join("Config", "config.xml"), sys.argv)
	config.AppendConfigurationFile(os.path.join("Config","prodam.xml"))

	htmlFiles = []

	mail = "\tRelatório de " + datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S") + "\r\n\r\n" 

	Log.Log("Searching Prodam")
	messages = HandleProdam(config)
	if messages is not None:
	    fileName = "Prodam.html"
	    mail += "\tFavor conferir o documento " + fileName + " anexado para informações relativas ao período.\r\n\r\n"
	    htmlFiles.append(fileName)
	    with open(fileName, "w") as fd:
		fd.write(messages)
	else:
	    mail += "\tNenhuma ocorrência relativa à Prodam encontrada no período.\r\n\r\n"

	Log.Log("Searching Suspensas")
	messages = HandleSuspensas(config)
	if messages is not None:
	    fileName = "EmpresasSuspensas.html"
	    mail += "\tFavor conferir o documento " + fileName + " anexado para informações relativas ao período.\r\n"
	    htmlFiles.append(fileName)
	    with open(fileName, "w") as fd:
		fd.write(messages)
	else:
	    mail += "\tNenhuma ocorrência relativa a empresas suspensas encontrada no período.\r\n"
	
	if (config.mode == "alert mode"):
	   
	    
	    Log.Log("Enviando E-Mail")
	    mailer = GMailerWrappper(config)
	    for file in htmlFiles:
		mailer.AttachFile(file)	
	    mailer.Send(mail)



