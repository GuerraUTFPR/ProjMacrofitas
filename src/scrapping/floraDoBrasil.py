import requests
import json
import csv

def getData(searchTerm='', allDataset=False, inputFile='../data/ListaMacrofitasResult.csv', outputPath='../data/floraDoBrasil.csv', notFoundPath='../data/notFoundFDB.csv'):
	urlRequestTemplate = "http://servicos.jbrj.gov.br/flora/taxon/{}"

	if allDataset:
		getManyEntries(urlRequestTemplate, inputFile, outputPath, notFoundPath)

	else:
		getOneEntry(urlRequestTemplate, searchTerm, outputPath, notFoundPath)


def getOneEntry(urlRequestTemplate, searchTerm, outputPath, notFoundPath):
	if(searchTerm == ''):
		raise BaseException

	urlRequest = urlRequestTemplate.format(searchTerm)
	response = requests.get(urlRequest.strip())

	try:
		unicode_queryResult = response.json()[u'result']
	except:
		parseAndWriteJSON(line, notFoundPath, isNone=True)
		return 0

	queryResult = json.dumps(unicode_queryResult,indent=4, ensure_ascii=False)
	parseAndWriteJSON(queryResult, outputPath)

def getManyEntries(urlRequestTemplate, inputFile,outputPath, notFoundPath):
	results = []

	with open(inputFile) as inputFile:
		lines = inputFile.readlines()

		for line in lines:
			urlRequest = urlRequestTemplate.format(line)
			response = requests.get(urlRequest.strip())

			unicode_queryResult = response.json()[u'result']

			if(unicode_queryResult == None):
				parseAndWriteJSON(line, notFoundPath, isNone=True)
				continue

			queryResult = json.dumps(unicode_queryResult,indent=4, ensure_ascii=False)
			parseAndWriteJSON(queryResult, outputPath)

def parseAndWriteJSON(json_data, outputPath, isNone=False):
	outputFile = open(outputPath,'a')
	output = csv.writer(outputFile)

	if isNone:
		output.writerow((json_data.split()[0], json_data.split()[1], 'Not Found'))
		return 0

	json_data = json.loads(json_data)[0]
	status = json_data["taxonomicstatus"]

	name, accepted_name = '', ''


	if status == 'SINONIMO':
		try:
			name = json_data["scientificname"].split()[0] + ' ' + json_data["scientificname"].split()[1]
		except:
			family = 'Not specified'
			name = 'Not Specified'
		try:
			accepted_name = json_data["NOME ACEITO"][0]["scientificname"].split()[0] + ' ' + json_data["NOME ACEITO"][0]["scientificname"].split()[1]
		except:
			accepted_name = "Not Specified"
			pass

	else:
		name = json_data["scientificname"].split()[0] + ' ' + json_data["scientificname"].split()[1]
		status = json_data["taxonomicstatus"]

	output.writerow((name, status, accepted_name))

def main():
	getData(allDataset=True)

if __name__ == '__main__':
	main()