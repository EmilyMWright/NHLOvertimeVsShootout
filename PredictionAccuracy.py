
################################################################################
# ShootoutValidity.py - Sports statistics project                              #
#                                                                              #
# Explore the prediction accuracy of betting odds                              #
# for NHL games. Compare accuracy for different endings                        #
# (i.e. regular time, over time, and shootout).                                #
#                                                                              #
# Author: Emily M. Wright                                                      #
# Date: January 2021                                                           #
#                                                                              #
################################################################################

import numpy as np 
import pandas as pd
import difflib
import yaml
import matplotlib.pyplot as plt

# Read in dictionary with NHL team names and their acronyms
with open('team_names.yml') as f:
    team_names = yaml.safe_load(f)
team_dict = team_names['team_dict']

################################################################################
# Function: win_probability                                                    #
#                                                                              #
# Purpose: Calculate win probability from American odds                        #
#                                                                              #
# Arguments:                                                                   #
#   home_close      integer     odds for home team                             #
#   vis_close       integer     odds for visiting team                         #
#                                                                              #
# Returns: home team win probability                                           #
#                                                                              #
################################################################################

def win_probability(home_close, vis_close):
        if home_close > 0:
            home_prob = (100/(1+home_close/100))
        else:
            home_prob = (100/(1-100/home_close))

        if vis_close > 0:
            vis_prob = (100/(1+vis_close/100))
        else:
            vis_prob = (100/(1-100/vis_close))

        weight = 100/(home_prob+vis_prob)
        return home_prob*weight

################################################################################
# Function: season_data                                                        #
#                                                                              #
# Purpose: Read in data on game results and betting odds for an NHL season.    #
#          Combine into one data frame with data on each game:                 #
#               Game ID                                                        #
#               Home Team                                                      #
#               Visiting Team                                                  #
#               Home Win Probability                                           #
#               Victor                                                         #
#               Ending Type (Regular Time (RT), Overtime (OT), Shootout (SO))  #
#               Season                                                         #
#                                                                              #
# Arguments:                                                                   #
#   season          string     NHL season of format "yyyy-yy"                  #
#                                                                              #
# Returns: data frame with entries specified above                             #
#                                                                              #
################################################################################

def season_data(season):
    # Read in odds and game results data from Excel file
    home_odds = pd.read_excel('NHL Data/nhl odds ' + season + '.xlsx', 
                            skiprows=lambda x: x % 2 != 0,
                            usecols=['Date','Team','Final','Close'],
                            engine='openpyxl')
    vis_odds = pd.read_excel('NHL Data/nhl odds ' + season + '.xlsx', 
                            skiprows=lambda x: x % 2 == 0 and x != 0,
                            usecols=['Team','Final','Close'],
                            engine='openpyxl')
    results = pd.read_excel('NHL Data/nhl results ' + season + '.xlsx', 
                            usecols=['Date','Home','RTOTSO'],
                            engine='openpyxl')
    results = results.fillna('RT')

    # Replace team names with accronyms
    home_odds['Team'].replace(team_dict, inplace=True)
    vis_odds['Team'].replace(team_dict, inplace=True)
    results['Home'].replace(team_dict, inplace=True)
    odds = pd.concat([home_odds, vis_odds], axis=1, ignore_index=True)
    odds = odds.rename(columns={0:'Date',1:'Home',2:'Home Goals',3:'Home Odds',\
                                4:'Visitor',5:'Visitor Goals',6:'Visitor Odds'}) 

    # Determine victor using goals
    odds['Victor'] = odds['Home'].where(odds['Home Goals'] > \
                    odds['Visitor Goals'], odds['Visitor'])
    
    # Calculate win probability from American odds
    odds['Home Win Prob'] = \
        odds.apply(lambda x: win_probability(x['Home Odds'], x['Visitor Odds']), \
                    axis=1)

    # Create unique game id
    odds['Game ID'] = odds['Date'].astype(str)+odds['Home']
    results['Game ID'] = results['Date'].astype(str)+results['Home']

    # Keep only games in both data sets
    results = results[results['Game ID'].isin(odds['Game ID'])]
    odds = odds[odds['Game ID'].isin(results['Game ID'])]

    # Align data frames
    odds = odds.sort_values('Game ID')
    results = results.sort_values('Game ID')
    
    
    # Set up final, combined data frame
    data = [odds['Game ID'], odds['Home'], odds['Visitor'], odds['Home Win Prob'],\
             odds['Victor'], results['RTOTSO']]
    headers = ['Game ID', 'Home', 'Visitor', 'Home Win Prob', 'Victor', 'RTOTSO']
    overall = pd.concat(data, axis=1, keys=headers)
    overall['Season'] = season
    return overall

################################################################################
# Function: prediction_accuracy                                                #
#                                                                              #
# Purpose: Calculate percent of time victor predicted by odds actually wins.   #
#          Calculate prediction accuracy for each type of ending (RT, OT, SO). #
#                                                                              #
# Arguments:                                                                   #
#   season          string     NHL season of format "yyyy-yy"                  #
#                                                                              #
# Returns: list of prediction accuracies (overall, RT, OT, SO)                 #
#                                                                              #
################################################################################

def prediction_accuracy(season):
    # Get season data
    season_result = season_data(season)

    # Split by ending type (RT, OT, or SO)
    season_RT_result = season_result[season_result['RTOTSO'] == 'RT']
    season_OT_result = season_result[season_result['RTOTSO'] == 'OT']
    season_SO_result = season_result[season_result['RTOTSO'] == 'SO']
    
    # Find when victor predicted by odds wins
    correct = (np.where(season_result['Home Win Prob']>=50, True, False) \
            & np.where(season_result['Home'] == season_result['Victor'], True, False)) \
            | (np.where(season_result['Home Win Prob']<=50, True, False) \
            & np.where(season_result['Visitor'] == season_result['Victor'], True, False))

    # Find when victor predicted by odds wins for games ending in regular time
    correct_RT = (np.where(season_RT_result['Home Win Prob']>=50, True, False) \
            & np.where(season_RT_result['Home'] == season_RT_result['Victor'], True, False)) \
            | (np.where(season_RT_result['Home Win Prob']<=50, True, False) \
            & np.where(season_RT_result['Visitor'] == season_RT_result['Victor'], True, False))
    
    # Find when victor predicted by odds wins for games ending in overtime
    correct_OT = (np.where(season_OT_result['Home Win Prob']>=50, True, False) \
            & np.where(season_OT_result['Home'] == season_OT_result['Victor'], True, False)) \
            | (np.where(season_OT_result['Home Win Prob']<=50, True, False) \
            & np.where(season_OT_result['Visitor'] == season_OT_result['Victor'], True, False))
    
    # Find when victor predicted by odds wins for games ending in shootout
    correct_SO = (np.where(season_SO_result['Home Win Prob']>=50, True, False) \
            & np.where(season_SO_result['Home'] == season_SO_result['Victor'], True, False)) \
            | (np.where(season_SO_result['Home Win Prob']<=50, True, False) \
            & np.where(season_SO_result['Visitor'] == season_SO_result['Victor'], True, False))

    # total = (np.where(season_result['Home Win Prob']>=60, True, False)) \
    #         | (np.where(season_result['Home Win Prob']<=40, True, False))

    # total_RT = (np.where(season_RT_result['Home Win Prob']>=60, True, False)) \
    #         | (np.where(season_RT_result['Home Win Prob']<=40, True, False))
    
    # total_OT = (np.where(season_OT_result['Home Win Prob']>=60, True, False)) \
    #         | (np.where(season_OT_result['Home Win Prob']<=40, True, False))

    # total_SO = (np.where(season_SO_result['Home Win Prob']>=60, True, False)) \
    #         | (np.where(season_SO_result['Home Win Prob']<=40, True, False))

    # Calculate percent of time prediction was correct
    accuracy = [season, np.count_nonzero(correct)*100/len(correct), 
                np.count_nonzero(correct_RT)*100/len(correct_RT), 
                np.count_nonzero(correct_OT)*100/len(correct_OT), 
                np.count_nonzero(correct_SO)*100/len(correct_SO)]

    # accuracy = [season, np.count_nonzero(correct)*100/np.count_nonzero(total), 
    #             np.count_nonzero(correct_RT)*100/np.count_nonzero(total_RT), 
    #             np.count_nonzero(correct_OT)*100/np.count_nonzero(total_OT), 
    #             np.count_nonzero(correct_SO)*100/np.count_nonzero(total_SO)]
    
    return accuracy

# Seasons for which I have data
seasons = ['2007-08','2008-09','2009-10','2010-11','2011-12','2012-13','2013-14',
            '2014-15','2015-16','2016-17','2017-18','2018-19','2019-20']
        
accuracy_list = []

# Calculate prediction accuracy for each season
for season in seasons:
    accuracy_list.append(prediction_accuracy(season))

# Store prediction accuracy in data frame
accuracy_df = pd.DataFrame(columns= 
            ['Season', 'Accuracy', 'RT Accuracy', 'OT Accuracy', 'SO Accuracy'],
            data=accuracy_list)

# Output
print(accuracy_df)

plt.plot(seasons, accuracy_df['Accuracy'], label='Overall')
plt.plot(seasons, accuracy_df['RT Accuracy'], label='Regulation')
plt.plot(seasons, accuracy_df['OT Accuracy'], label='Overtime')
plt.plot(seasons, accuracy_df['SO Accuracy'], label='Shootout')
plt.legend()
plt.grid()
plt.ylabel('Prediction Accuracy (%)')
plt.xlabel('Season')
plt.ylim([40, 80])
plt.show()