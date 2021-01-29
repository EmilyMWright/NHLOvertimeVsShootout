# Overtime vs Shootout Analysis
# Author: Emily Wright
# Date: January 2021

import numpy as np 
import pandas as pd
import difflib

full_res = ['Edmonton Oilers', 'St. Louis Blues',
    'Vegas Golden Knights', 'Anaheim Ducks', 'Carolina Hurricanes',
    'Colorado Avalanche', 'Dallas Stars', 'Nashville Predators',
    'New York Rangers', 'Pittsburgh Penguins', 'Tampa Bay Lightning',
    'Columbus Blue Jackets', 'New Jersey Devils', 'New York Islanders',
    'Philadelphia Flyers', 'San Jose Sharks', 'Arizona Coyotes',
    'Buffalo Sabres', 'Calgary Flames', 'Florida Panthers', 'Ottawa Senators',
    'Washington Capitals', 'Detroit Red Wings', 'Vancouver Canucks',
    'Chicago Blackhawks', 'Montreal Canadiens', 'Winnipeg Jets', 'Boston Bruins',
    'Los Angeles Kings', 'Minnesota Wild', 'Atlanta Thrashers', 'Phoenix Coyotes']

abr_res = ['EDM', 'STL', 'TOR','VEG', 'ANA', 'CAR','COL', 'DAL', 'NSH', 'NYR', 'PIT', 
    'TBL', 'CBJ', 'NJD', 'NYI', 'PHI', 'SJS', 'ARI', 'BUF', 'CGY', 'FLA','OTT', 'WSH', 
    'DET', 'VAN', 'CHI', 'MTL', 'WPG', 'BOS', 'LAK', 'MIN', 'ATL', 'PHX']

full_odds = ['Dallas', 'Arizona', 'Boston', 'Buffalo', 'Calgary', 'Colorado', 'Montreal', 
    'NYIslanders', 'Ottawa', 'Pittsburgh', 'Vancouver', 'Vegas', 'Winnipeg', 'Carolina', 
    'Columbus', 'LosAngeles', 'Minnesota', 'NewJersey', 'Toronto', 'Anaheim', 'Chicago',
    'Washington', 'Detroit', 'Florida', 'NYRangers', 'Nashville', 'St.Louis', 'TampaBay', 
    'Philadelphia', 'SanJose', 'Edmonton', 'Arizonas', 'Los Angeles', 'St. Louis', 
    'New Jersey', 'Atlanta', 'Phoenix']

abr_odds = ['DAL', 'ARI', 'BOS','BUF', 'CGY', 'COL', 'MTL', 'NYI', 'OTT', 'PIT', 'VAN',
    'VEG', 'WPG', 'CAR', 'CBJ', 'LAK', 'MIN', 'NJD', 'TOR', 'ANA', 'CHI', 'WSH', 'DET',
    'FLA', 'NYR', 'NSH', 'STL', 'TBL', 'PHI', 'SJS', 'EDM', 'ARI', 'LAK', 'STL', 'NJD', 
    'ATL', 'PHX']

team_dict = {'Dallas':'DAL', 'Arizona':'ARI', 'Boston':'BOS', 'Buffalo':'BUF', 'Calgary':'CGY', 'Colorado':'COL',
    'Montreal':'MTL', 'NYIslanders':'NYI', 'Ottawa':'OTT', 'Pittsburgh':'PIT', 'Vancouver':'VAN', 
    'Vegas':'VEG', 'Winnipeg':'WPG', 'Carolina':'CAR', 'Columbus':'CBJ', 'LosAngeles':'LAK', 
    'Minnesota':'MIN', 'NewJersey':'NJD', 'Toronto':'TOR', 'Anaheim':'ANA', 'Chicago':'CHI', 'Washington':'WSH',
    'Detroit':'DET', 'Florida':'FLA', 'NYRangers':'NYR', 'Nashville':'NSH', 'St.Louis':'STL', 'TampaBay':'TBL', 
    'Philadelphia':'PHI', 'SanJose':'SJS', 'Edmonton':'EDM', 'Atlanta':'ATL', 'Phoenix':'PHX'}

#print(difflib.get_close_matches("Toronto Maple Leafs", list(team_dict.keys()), n=1)[0])

for name in full_res:
    print(name)
    print(team_dict[difflib.get_close_matches(name, list(team_dict.keys()), n=1)[0]])

# /Users/emilywright/OneDrive/Documents/Sport Stats/NHL Data
def SeasonData(season):
    OddsData = pd.read_excel('NHL Data/nhl odds ' + season + '.xlsx')
    ResultsData = pd.read_excel('NHL Data/nhl results ' + season + '.xlsx')
    



    ########
    ResultsDf = pd.DataFrame({'Date': ResultsData.Date,'Home': ResultsData.Home, 'RTOTSO': ResultsData.RTOTSO})
    ResultsDf = ResultsDf.fillna('RT')
    
     # Changes full team name to acronym
    home = [] 
    for team in ResultsDf['Home']:
        i = full.index(difflib.get_close_matches(team, full, n=1)[0])
        home.append(acc[i])
    
    ResultsDf['Home'] = home
    
    ResultsDf = ResultsDf.sort_values(['Date', 'Home'])
    
    headers = ['Date', 'Home', 'Visitor', 'Home Win Probability', 
               'Visitor Win Probability', 'Predicted Victor', 'Victor']
    SeasonData = {header:[] for header in headers}
    
    # CSV file has two rows for each game
    SeasonData['Home'] = OddsData.Team.groupby(OddsData.Team.index // 2).last().to_numpy()
    SeasonData['Visitor'] = OddsData.Team.groupby(OddsData.Team.index // 2).first().to_numpy()
    SeasonData['Date'] = OddsData.Date.groupby(OddsData.Date.index // 2).first().to_numpy()
    HOdds = OddsData.Close.groupby(OddsData.Close.index // 2).last().to_numpy()
    VOdds = OddsData.Close.groupby(OddsData.Close.index // 2).first().to_numpy()
    HGoals = OddsData.Final.groupby(OddsData.Final.index // 2).last().to_numpy()
    VGoals = OddsData.Final.groupby(OddsData.Final.index // 2).first().to_numpy()
    
    # Changes full team name to acronym
    home_acc = []
    for team in SeasonData['Home']:
        i = full2.index(difflib.get_close_matches(team, full2, n=1)[0])
        home_acc.append(acc2[i])
    
    SeasonData['Home'] = home_acc
    
    vis_acc = []
        
    for team in SeasonData['Visitor']:
        i = full2.index(difflib.get_close_matches(team, full2, n=1)[0])
        vis_acc.append(acc2[i])
    
    SeasonData['Visitor'] = vis_acc
    
    hProb, vProb = 0, 0

    # Calcualtes win probability from American odds using re-weighting to account for betting margins
    for i in range(len(HOdds)):

        if HOdds[i] > 0:
            hProb = (100/(1+HOdds[i]/100))
        else:
            hProb = (100/(1-100/HOdds[i]))

        if VOdds[i] > 0:
            vProb = (100/(1+VOdds[i]/100))
        else:
            vProb = (100/(1-100/VOdds[i]))

        weight = 100/(hProb+vProb)

        SeasonData['Home Win Probability'].append(weight*hProb)
        SeasonData['Visitor Win Probability'].append(weight*vProb)

        if SeasonData['Home Win Probability'] > SeasonData['Visitor Win Probability']:
            SeasonData['Predicted Victor'].append(SeasonData['Home'][i])
        else:
            SeasonData['Predicted Victor'].append(SeasonData['Visitor'][i])

    SeasonData['Home Win Probability'] = np.array(SeasonData['Home Win Probability']).round(2)
    SeasonData['Visitor Win Probability'] = np.array(SeasonData['Visitor Win Probability']).round(2)

    # Determines victor from score
    for i in range(len(HGoals)):
        if HGoals[i] > VGoals[i]:
            SeasonData['Victor'].append(SeasonData['Home'][i])
        else:
            SeasonData['Victor'].append(SeasonData['Visitor'][i])

    OddsDf = pd.DataFrame(SeasonData)

    OddsDf = OddsDf.sort_values(['Date', 'Home'])

    # Both dataframes are sorted by date and then home team so that entries are in the same order
    OddsDf['RTOTSO'] = ResultsDf['RTOTSO']
    
    correct = np.where(OddsDf['Predicted Victor'] == OddsDf['Victor'], True, False)
    lopsided = np.where((OddsDf['Home Win Probability'] <= 40) | (OddsDf['Home Win Probability'] >= 60)
                        | (OddsDf['Visitor Win Probability'] <= 40) | (OddsDf['Visitor Win Probability'] >= 60), True, False)

    OddsDf['Correct Prediction'] = correct
    OddsDf['Lopsided Odds'] = lopsided
    OddsDf = OddsDf.sort_index()
    print('Odds collected for ' + season)
    return OddsDf



#print(SeasonData("2018-19"))