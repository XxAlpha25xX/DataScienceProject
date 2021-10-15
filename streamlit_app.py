import streamlit as st
import json
import numpy as np
import pandas as pd

from datetime import datetime as dt

# Supress Warnings
import warnings
warnings.filterwarnings('ignore')


st.title('[Data-Science] Sorare')
#Load file in to pd
with open('sorare_data_light.json', 'r', encoding='utf-8') as file:
  json_data = json.load(file)
df = pd.json_normalize(json_data)

#Drop playerId
df.drop('PlayerId', axis=1, inplace=True)

#Delete footbal player played less than 4 match
to_del = []
for i in range(0, len(df)):
  row = df.iloc[i]
  if len([m for m in row.Matchs if m['mins_played']]) <= 3:
    to_del.append(i)
df.drop(to_del, axis=0, inplace=True)

listTeam = df["TeamId"].unique()
listTeam = list(listTeam)
listTeam.insert(0,"")
arrayOfScarcity = ["", "LIMITED", "RARE", "SUPER RARE", "UNIQUE"]
position = df["Position"].unique()
position = list(position)
position.insert(0, "")

def setListScarcity(index):
  return "Valuations." + index + ".EurAverage"

def get_predictions(x1, x2, x3, x4, x5, x6):
    try:
        team = x1 if x1 != "" else None
        price = float(x3)
        scarcity = setListScarcity(x2)
        scarcityFinal = scarcity if scarcity != "" else None
        min_matchs = int(x4) if x4 != "" else None
        pos = x5 if x5 != "" else None
        score = float(x6) if x6 != "" else None

        print(f"Team = {team}")
        print(f"Price =  {price}")
        print(f"Scarcity = {scarcityFinal}")
        print(f"Min matchs = {min_matchs}")
        print(f"Position = {pos}")
        print(f"SO5Score = {score}")
        print("----------")
        dataset = pd.DataFrame(df)

        print(f'Before: {dataset.shape}')
        # Drop sockers whom average € value is not set for the given scarcity
        dataset = dataset.drop(dataset[(dataset[scarcityFinal] == 0) | (dataset[scarcityFinal] > price)].index)
        # If a team is specified, drop all players that don't belong to it
        if team:
            dataset = dataset.drop(dataset[dataset["TeamId"] != team].index)
        # Select only the players that played the minimum matchs required
        if min_matchs:
            dataset = dataset.drop(dataset[dataset['Played matchs'] < min_matchs].index)
        # Select only the players that match the required position
        if pos:
            dataset = dataset.drop(dataset[dataset['Position'] != pos].index)
        if score:
            dataset = dataset.drop(dataset[dataset['SO5Score Average'] < score].index)
        print(f'After: {dataset.shape}')

        print("-------")
        dataset = dataset.sort_values(by=['SO5Score Average'])
        if dataset.shape[0] != 0:
            tmp = dataset.groupby(["FullName", "SO5Score Average", "TeamId"]).first().sort_values('SO5Score Average', ascending=False)
            christofer = tmp.head()[0:1]
            print(f"We recommend that you buy: \t\n{christofer.index[0][0]}, \n player of {christofer.index[0][2]},\n score => {christofer.index[0][1]} \n and  the price is {christofer[scarcityFinal][0]}€\n in {scarcity}")
            st.write(f"We recommend that you buy: \t\n{christofer.index[0][0]}, \n player of {christofer.index[0][2]},\n score => {christofer.index[0][1]} \n and  the price is {christofer[scarcityFinal][0]}€\n in {scarcity}")
        else:
            print(f"We didnt find the best fit for the parameters:\n\tTeam:\t{team}\n\tMaxPrice:\t{price}\n\tScarcity:\t{scarcityFinal}\n\tMinimumPlayedMatchs:\t{min_matchs}\n\tPosition:\t{pos}")
            st.write(f"We didnt find the best fit for the parameters:\n\tTeam:\t{team}\n\tMaxPrice:\t{price}\n\tScarcity:\t{scarcityFinal}\n\tMinimumPlayedMatchs:\t{min_matchs}\n\tPosition:\t{pos}")
    except Exception as e:
        st.write(e)
        
        
    
priceW = st.text_input('Price (Mandatory)(€)', '0')
teamW = st.selectbox( 'Pick a team (Optional)',listTeam)
scarcityW = st.selectbox( 'Pick a rarity (Mandatory)',arrayOfScarcity)
min_matchs = st.text_input('Min played match (Optional)')
score = st.text_input('Min Score (Optional)', '')
position = st.selectbox( 'Pick a team (Optional)',position)



if st.button('Determine the best fit'):
    get_predictions(x1=teamW, x2=scarcityW, x3=priceW, x4=min_matchs, x5=position, x6=score)
