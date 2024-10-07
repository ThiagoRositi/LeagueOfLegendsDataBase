
#proyecto para utilizar la api de league of legends y analizar mi perfil subiendolo a una base de datos.

import requests  # type: ignore
import numpy as np # type: ignore
import pandas as pd # type: ignore
import json


#la api key se actualiza cada nose cuanto fijarse eso si no anda.

API_KEY = "RGAPI-e5fb717a-2347-4a11-b5ee-b8d2f9f9fc6e"
TAG = "LAS" #Ondarza#LAS
SUMMONER_NAME = "ElPerritoLoco"

API_REST = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{SUMMONER_NAME}/{TAG}?api_key={API_KEY}"

# recuperamos de la API la puuid, es un dict parecido al siguiente 
# {'puuid': 's6IMn66Ob-1OjC-J5ZYjt8jUv0XeqnzSLyHONgThnwI7vdyc3LVGLYxEE-rdUtghyrIy5pFB0D3gzQ', 'gameName': 'Bracamante', 'tagLine': '8478'}
# puuid herdegen: 'Uv8IBC93J6w5oWIJXay2W7seUkTCo3BPwmtoSmMNITjzjMLfX8Z61kf6USDQV3oamiwSe4piq01_Ow'

resp = requests.get(API_REST)
data = resp.json()

# tomo del diccionario la puuid

PUUID = data.get("puuid")

#devuelve una lista con el top 50 personajes y su nivel (representa la maestria o cantidad de uso)

def dicTopMaestry(puuid, api_key):


	API_MAESTRIAS = f"https://la2.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}?api_key={api_key}"
	resp = requests.get(API_MAESTRIAS)
	data = resp.json()

	dict_campeones = {}

	#primeros 20 campeones del diccionario (los de mas maestria)
	for campeon in range(0, 50):
		#recupero la id del campeon
		campeon_id = data[campeon].get("championId")
		championLevel = data[campeon].get("championLevel")
		championPoints = data[campeon].get("championPoints")
		dict_campeones.update({campeon_id:{'championLevel': championLevel, 'championPoints': championPoints}})
	return dict_campeones


#le das un diccionario de campeones, una puuid, la apikey y busca en los ultimos 1000 match tipo rankeds y guarda datos especificos en ese diccionario

def collectMatches(puuid, api_key):
	matches = []
	for i in range (10):
		API_MATCHES = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start={i*100}&count=100&api_key={api_key}"

		respMatches = requests.get(API_MATCHES)

		#devuelve una lista con la id de los matches lista = ['match1', 'match2', 'match3']
		actualMatches = respMatches.json()
		for i in actualMatches:
			matches.append(i)
		
	
	return matches
	 

def CollectInfoLast100Matches(dict_campeones, puuid, api_key): 
	#api de partidas el parametro start= 0 dice desde cuanto, count=100 en este caso 1000 partidas (corregir)

				#devuelve una lista con la id de los matches lista = ['match1', 'match2', 'match3']
				matches = collectMatches(puuid, api_key)
				# herdegenDf = pd.DataFrame.from_dict(dict_campeonIdToCampeon, orient='index', columns=['puuid','championLevel','championPoints'])
				# herdegenDf con indice campeon id y columnas puntos de maestria nivel del campeon y nose.
				for match in matches:
					API_MATCH_INFO = f'https://americas.api.riotgames.com/lol/match/v5/matches/{match}?api_key={api_key}'
					resp = requests.get(API_MATCH_INFO)
					if resp.status_code == 200:
						resp.encoding='utf-8'
						dataMatch = resp.json()
						summoners = dataMatch.get('metadata').get('participants')

					#si el modo de juego es clasico guardo la info de herdegen
					if dataMatch != None:
							summonerNum = 0
							#buscamos al usuario que necesitamos por la puuid.
							
							for i in range(len(summoners)):
								if summoners[i] == puuid:
									summonerNum = i

								
							
							#si esta el campeon en el diccionario de los 20 mas jugados guardamos datos
							infoSummonerGame = dataMatch.get('info').get('participants')[summonerNum]
							champPlayedId = infoSummonerGame.get('championId')
							
							if dict_campeones.get(champPlayedId) != None:

								
								#creo un diccionario con lo que voy a updatear, en este caso me interesan los valores de:
								#kills(int), deaths(int), assists(int), goldEarned(int), pentakills(int), visionScore(int) y win(boolean)
								#

								dictDataChampPlayed = {'wins': infoSummonerGame.get('win'), 'kills': infoSummonerGame.get('kills'), 'deaths':infoSummonerGame.get('deaths'),
														'assists': infoSummonerGame.get('assists'), 'goldEarned':infoSummonerGame.get('goldEarned'),
															'visionScore': infoSummonerGame.get('visionScore'), 'pentakills': infoSummonerGame.get('pentakills'), 
															'championName': infoSummonerGame.get('championName') }
									
									
									#para todos los parametros
								for parameter in dictDataChampPlayed.keys():
									if dict_campeones.get(champPlayedId).get(parameter) == None :
										#si no existe la lista le apendeo los valores para esta partida
										dict_campeones.get(champPlayedId).update({parameter: [dictDataChampPlayed.get(parameter)]})

										#appendeo la nueva lista, con el valor agregado al diccionario de campeones, al campeon correspondiente.
									else :
										listParameter = dict_campeones.get(champPlayedId).get(parameter)
										listParameter.append(dictDataChampPlayed.get(parameter))
										#piso el valor con el nuevo
										dict_campeones.get(champPlayedId).update({parameter: listParameter})

								#apendeamos al diccionario de campeones, el nombre del campeon en su id, luego lo cambiaremos por el indice.
								if dict_campeones.get(champPlayedId).get('championName') == None:
									dict_campeones.get(champPlayedId).update({'championName':dictDataChampPlayed.get('championName')})


				return dict_campeones
				

#funciona solo en este caso de diccionario de diccionarios.
#lo utilizo para cambiar el indice del diccionario en vez del champId al champName
#crea otro diccionario
def changeIndex(dictionary):
	finalDict = {}
	for key, value in dictionary.items():
		if value.get('championName') != None:
			finalIndex = value.pop('championName')
	
			value.update({'championId': key})
			finalDict.update({finalIndex[0] : value})

	return finalDict


maestrias = dicTopMaestry(PUUID, API_KEY)
maestrias = CollectInfoLast100Matches(maestrias, PUUID, API_KEY)
maestrias = changeIndex(maestrias)

#poner ruta donde quiere que se guarde el diccionario.

ruta = f"C:\\Users\\thiago\\OneDrive\\Escritorio\\Facu\\TrabajoApi\\diccionario{SUMMONER_NAME}.json"

with open(ruta, 'w') as archivo:
	json.dump(maestrias, archivo, indent=4)



#--------------------------------------- prueba formato apimatchs--------------------------------------------

#a = {}
#data = pruebaCollect(a, PUUID, API_KEY)
#info = data[0].get('info')
#participants = info.get('participants')

#------------------------------------------ prueba for en api de matches -----------------------------------

#matches = collectMatches(PUUID,API_KEY)
#setDeMatches = set(matches)
#if len(setDeMatches) == len(matches):
#	print(True)
#	print(len(setDeMatches))
