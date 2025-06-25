import pandas as pd
from collections import defaultdict
from colorama import Fore, Style

# Load CSV
csv_path = "TTOC_Results.csv"
df = pd.read_csv(csv_path)

# Remove rows where a player is both on the podium (1st, 2nd, or 3rd) and is listed as a participant in the same gamemode in the same season
def remove_duplicate_participants(df):
    # Create a set of (season, gamemode, player_name) tuples for podium finishers
    podium_players = set()
    for _, row in df[df['placement'].isin(['1st', '2nd', '3rd'])].iterrows():
        podium_players.add((row['season'], row['gamemode'], row['player_name']))
    
    # Filter out participant rows for players who are already on the podium
    filtered_df = df[~(
        (df['placement'] == 'participant') & 
        df.apply(lambda row: (row['season'], row['gamemode'], row['player_name']) in podium_players, axis=1)
    )]
    
    return filtered_df

# Apply the filtering
df = remove_duplicate_participants(df)

# Normalize column values
df['placement'] = df['placement'].str.lower().str.strip()
df['gamemode'] = df['gamemode'].str.strip()
df['season'] = df['season'].astype(str).str.strip()
df['player_name'] = df['player_name'].str.strip()

# Podium Appearances
podium_df = df[df['placement'].isin(['1st', '2nd', '3rd'])]
podium_appearances = podium_df['player_name'].value_counts()

# Most wins by placement
most_1st = df[df['placement'] == '1st']['player_name'].value_counts()
most_2nd = df[df['placement'] == '2nd']['player_name'].value_counts()
most_3rd = df[df['placement'] == '3rd']['player_name'].value_counts()

# Most wins by gamemode
gamemode_wins = (
    df[df['placement'] == '1st']
    .groupby(['gamemode', 'player_name'])
    .size()
    .reset_index(name='wins')
    .sort_values(['gamemode', 'wins'], ascending=[True, False])
)

# Streaks
# A player's streak will only reset if a player participated in a bracket, but did not retain their achievement.

# Longest Podium Streak
podium_streaks = {}
podium_streak_gamemodes = {}
for player in podium_appearances.index:
        player_df = df[df['player_name'] == player]
        streak = 0
        longest_streak = 0
        current_gamemodes = []
        longest_gamemodes = []

        for _, row in player_df.iterrows():
            if row['placement'] in ['1st', '2nd', '3rd']:
                streak += 1
                current_gamemodes.append(row['gamemode'] + " " + row['season'])
            else:
                if streak > longest_streak:
                    longest_streak = streak
                    longest_gamemodes = current_gamemodes.copy()
                streak = 0
                current_gamemodes = []
        if streak > longest_streak:
            longest_streak = streak
            longest_gamemodes = current_gamemodes.copy()

        podium_streaks[player] = longest_streak
        podium_streak_gamemodes[player] = longest_gamemodes

# Longest Win Streak
win_streaks = {}
win_streak_gamemodes = {}
for player in most_1st.index:
    player_df = df[df['player_name'] == player]
    streak = 0
    longest_streak = 0
    current_gamemodes = []
    longest_gamemodes = []

    for _, row in player_df.iterrows():
        if row['placement'] == '1st':
            streak += 1
            current_gamemodes.append(row['gamemode'] + " " + row['season'])
        else:
            if streak > longest_streak:
                longest_streak = streak
                longest_gamemodes = current_gamemodes.copy()
            streak = 0
            current_gamemodes = []
    if streak > longest_streak:
        longest_streak = streak
        longest_gamemodes = current_gamemodes.copy()

    win_streaks[player] = longest_streak
    win_streak_gamemodes[player] = longest_gamemodes

# Uncomment the following lines to sort and export the CSV data
'''
# Sort csv data by season, gamemode, and placement and export to CSV
# Sort by custom order for gamemode - Classic, Weapons, Golf, Gold Rush, Target, Laser, Candy Tanks
gamemode_order = {
    'Classic': 1,
    'Weapons': 2,
    'Golf': 3,
    'Gold Rush': 4,
    'Target': 5,
    'Laser': 6,
    'Candy Tanks': 7
}
df['gamemode_order'] = df['gamemode'].map(gamemode_order)
df_sorted = df.sort_values(by=['season', 'gamemode_order', 'placement'], ascending=[True, True, True])
df_sorted.drop(columns=['gamemode_order'], inplace=True)
# Export sorted data to CSV
sorted_csv_path = "TTOC_Results_Sorted.csv"
df_sorted.to_csv(sorted_csv_path, index=False)
'''

# Display all insights
def display_insights():
    print(Fore.CYAN + "Podium Appearances" + Fore.RESET)
    print(podium_appearances.to_string(header=False))
    print(Fore.CYAN + "\nMost Wins by Placement" + Fore.RESET)
    print(Fore.YELLOW + "Most 1st Place:" + Fore.RESET)
    print(most_1st.to_string(header=False))
    print(Fore.YELLOW + "\nMost 2nd Place:" + Fore.RESET)
    print(most_2nd.to_string(header=False))
    print(Fore.YELLOW + "\nMost 3rd Place:" + Fore.RESET)
    print(most_3rd.to_string(header=False))

    print(Fore.CYAN + "\nMost Wins by Gamemode" + Fore.RESET)
    for gamemode, group in gamemode_wins.groupby('gamemode'):
        print(Fore.YELLOW + f"\n{gamemode}:" + Fore.RESET)
        for _, row in group.iterrows():
            print(f"{row['player_name']:<15} {row['wins']}")

    print(Fore.CYAN + "\nLongest Podium Streaks" + Fore.RESET)
    for player, streak in sorted(podium_streaks.items(), key=lambda x: x[1], reverse=True):
        gamemodes_str = ', '.join(podium_streak_gamemodes[player])
        print(f"{player:<20} {streak}  [{gamemodes_str}]")
    
    print(Fore.CYAN + "\nLongest Win Streaks" + Fore.RESET)
    for player, streak in sorted(win_streaks.items(), key=lambda x: x[1], reverse=True):
        gamemodes_str = ', '.join(win_streak_gamemodes[player])
        print(f"{player:<20} {streak}  [{gamemodes_str}]")

if __name__ == "__main__":
    display_insights()
