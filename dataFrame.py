import json
import pandas as pd # type: ignore
import numpy as np   # type: ignore


ruta = "C:\\Users\\thiago\\OneDrive\\Escritorio\\Facu\\TrabajoApi\\diccionarioElPerritoLoco.json"

def champJsonToDataFrame(ruta):
    
    dataframe = pd.DataFrame()
    #abro el arhivo
    with open (ruta, 'r') as archivo:
        dataframe = pd.read_json(archivo, orient='index')
    
    return dataframe

def modifyDataframe(df):
    df['winrate'] = None
    df['kda'] = None
    df['totalGames'] = None
    for index, row in df.iterrows():
        trueWins = 0
        
        df.at[index,'totalGames'] = len(row['wins'])
        
        for win in row['wins']:
            #lista booleana de victorias. si es true suma una victoria "real"
            if win:
                trueWins +=1
                
        winrate = trueWins / len(row['wins'])
        df.at[index, 'winrate'] = round (winrate * 100, 1)
        df.at[index, 'wins'] = trueWins
        
        #calculamos el kda, kills+assists / deaths
        kda = (sum(df.at[index, 'kills']) + sum(df.at[index, 'assists']))
        if sum(df.at[index,'deaths']) != 0:
            kda = kda / sum(df.at[index,'deaths'])
        
        
        #lo establecemos en el indice actual (campeon) redondeado 2 decimales.
        df.at[index, 'kda'] = round(kda, 2)
        
        #reemplazo la lista de visionScore por su promedio.
        visionScore = sum(df.at[index, 'visionScore']) / len(df.at[index, 'visionScore'])
        df.at[index, 'visionScore'] = round(visionScore , 2)
        
        #reemplazo la lista de oro obtenido por su promedio.
        goldEarned = sum(df.at[index, 'goldEarned']) / len(df.at[index, 'goldEarned'])
        df.at[index, 'goldEarned'] = round(goldEarned, 2)
        
        
        
        #reemplazo la lista de pentakills por el total de pentakills sumandolos (como hay tipo None y tipo int hago un for)
        totalPentakills = 0
        for pentakill in  df.at[index, 'pentakills']:
            if pentakill != None:
                totalPentakills += pentakill
        df.at[index, 'pentakills'] = totalPentakills
        
    df = df.drop(columns=['kills','deaths','assists'])    
    return df      
        
                



df = champJsonToDataFrame(ruta)
df = modifyDataframe(df)
print(df[['totalGames','pentakills','winrate','kda','visionScore','goldEarned']])


