import streamlit as st
import json
import pandas as pd

# Supress Warnings
import warnings
warnings.filterwarnings('ignore')

# Load file in to pd
with open('sorare_data_light.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)
df = pd.json_normalize(json_data)

# Drop playerId
df.drop('PlayerId', axis=1, inplace=True)
# Drop Slug
df.drop('Slug', axis=1, inplace=True)
# Drop DisplayName
df.drop('DisplayName', axis=1, inplace=True)
# Drop BirthDate
df.drop('BirthDate', axis=1, inplace=True)
# Drop Licensed
df.drop('Licensed', axis=1, inplace=True)
# Drop SubscriptionsCount
df.drop('SubscriptionsCount', axis=1, inplace=True)
# Drop NationalTeam
df.drop('NationalTeam', axis=1, inplace=True)
# Drop MatchName
df.drop('MatchName', axis=1, inplace=True)
# Drop Matchs
df.drop('Matchs', axis=1, inplace=True)
# Drop SO5Scores
df.drop('SO5Scores', axis=1, inplace=True)
# Drop AllAroundScores
df.drop('AllAroundScores', axis=1, inplace=True)
# Drop Price info.eur
df.drop('Price info.eur', axis=1, inplace=True)
# Drop Price info.usd
df.drop('Price info.usd', axis=1, inplace=True)
# Drop Price info.gbp
df.drop('Price info.gbp', axis=1, inplace=True)
# Drop Price info.eth
df.drop('Price info.eth', axis=1, inplace=True)

# # Delete footbal player that played less than 4 match
# to_del = []
# for i in range(0, len(df)):
#     row = df.iloc[i]
#     if len([m for m in row.Matchs if m['mins_played']]) <= 3:
#         to_del.append(i)
# df.drop(to_del, axis=0, inplace=True)

def setListScarcity(index):
    return 'Valuations.' + index + '.EurAverage'

def get_predictions(x1, x2, x3, x4, x5, x6):
    # Get all parameters and check if some values are null
    price = float(x3)
    scarcityFinal = setListScarcity(x2)
    min_matchs = int(x4) if x4 != '' else None
    score = float(x6) if x6 != '' else None
    team = x1 if x1 != '' else None
    pos = x5 if x5 != '' else None

    # Create a copy of the dataset
    dataset = pd.DataFrame(df)

    ############### MANDATORY PARAMETERS ###############
    # Drop sockers whose average € value is not set for the given scarcity
    dataset = dataset.drop(dataset[(dataset[scarcityFinal] == 0) | (dataset[scarcityFinal] > price)].index)
    # Drop all valuation columns that doesn't match the scarcity
    for column in dataset.columns:
        if 'Valuations' in column and column != scarcityFinal:
            dataset.drop(column, axis=1, inplace=True)
    ####################################################

    ############### OPTIONAL PARAMETERS ###############
    # If a team is specified, drop all players that don't belong to it
    if team:
        dataset = dataset.drop(dataset[dataset['TeamId'] != team].index)
    # Select only the players that played the minimum matchs required
    if min_matchs:
        dataset = dataset.drop(dataset[dataset['Played matchs'] < min_matchs].index)
    # Select only the players that match the required position
    if pos:
        dataset = dataset.drop(dataset[dataset['Position'] != pos].index)
    # Select only the players that match the required SO5Score average
    if score:
        dataset = dataset.drop(dataset[dataset['SO5Score Average'] < score].index)
    ###################################################

    christofer = dataset.sort_values(by=['SO5Score Average'], ascending=False)

    if dataset.shape[0] != 0:
        # christofer = dataset.groupby(['FullName', 'SO5Score Average', 'TeamId']).sort_values('SO5Score Average', ascending=False)
        st.dataframe(data=christofer, width=None, height=None)
        # st.write(f"We recommend that you buy: \t\n{christofer.index[0][0]}, \n player of {christofer.index[0][2]},\n score => {christofer.index[0][1]} \n and  the price is {christofer[scarcityFinal][0]}€\n in {scarcity}")
    else:
        st.write('We didn\'t find any match for the parameters:')
        st.write(f'MaxPrice:              {price}')
        st.write(f'Scarcity:              {x2}')
        st.write(f'MinimumPlayedMatchs:   {min_matchs}')
        st.write(f'MinimumScore:          {score}')
        st.write(f'Team:                  {team}')
        st.write(f'Position:              {pos}')

# Set Web-App title
st.title('[Data-Science] Sorare')

# Extracted lists from the dataset, used for the selection
listTeam = df['TeamId'].unique().tolist()
listTeam.insert(0, '')
arrayOfScarcity = ['LIMITED', 'RARE', 'SUPER RARE', 'UNIQUE']
position = df['Position'].unique().tolist()
position.insert(0, '')

# Widgets creation
priceW = st.text_input('*Price (€):', '0')
scarcityW = st.selectbox('*Select a rarity:', arrayOfScarcity)
min_matchs = st.text_input('Minimum played matchs:', '')
score = st.text_input('Minimum score average:', '', help='SO5Score must be <=100')
teamW = st.selectbox('Select a team:', listTeam)
position = st.selectbox('Select a position:', position)

# Add a button that triggers the algorithm used to find players that match the selected parameters
if st.button('Determine the best fit'):
    get_predictions(x1=teamW, x2=scarcityW, x3=priceW, x4=min_matchs, x5=position, x6=score)