import pandas as pd
import numpy as np

class ProcessGameState():
    def __init__(self, filename):
        self.df = pd.read_parquet(filename, engine='pyarrow')

    def checkBoundary(self,c, boundary): # uses the raycast odd number rule to detect if a point is within the boundaries of a polygon
        x,y,z = c
        if z>421 or z<285: # first check z bound
            return False
        else: # then implement raycast algorithm
            count = 0
            
            for edge in boundary:
                (x1, y1), (x2, y2) = edge
                if (y < y1) != (y<y2) and x < x1 + ((y-y1)/(y2-y1))*(x2-x1):
                    count +=1

            return count%2 == 1

    def getBoundaryRows(self, boundary):
        withinBoundary = []
        for row in self.df.iterrows():
            c = (row[1].x, row[1].y, row[1].z) # create list to hold singular xyz coordinate for each row
            if self.checkBoundary(c, boundary):
                 withinBoundary.append(row[0])
        return withinBoundary
    
    def getRows(self, area, team, side): # get rows filtered by area, team, and side
        rows = []
        for row in self.df.iterrows():
            row = row[1]
            if ((area == row['area_name']) and (team == row['team']) and (side == row['side']) and (row['is_alive'])):
                rows.append(row)
        return rows
    
def extractWeaponClass( row):
    weapons = []
    for item in row['inventory']:
        weapons.append(item['weapon_class'])
    return weapons


def enterArea(rows):# function which returns a 2d array indexed by round number, within each round contains rows of data for first instance of player data for that round
    playerIndex = -1
    rows_by_round = np.empty(shape=(15, 5), dtype=object)
    tRound = 0
    tPlayer = ''
    for row in rows: # rows are already sorted by player and by timer in round so we just need to find the first instance per player per round
        player = row['player']
        if player != tPlayer:
            playerIndex+=1
        round_num = row['round_num']
        if round_num != tRound: # change in round means we can input new row
            rows_by_round[round_num-16][playerIndex] = row
        tRound = round_num
        tPlayer = player
    return rows_by_round
    
def getTimer(rows, weaponCount):  
    sorted_rows = sorted(rows, key=lambda x: x['seconds'], reverse=False)
    print("Requirements met at: "+ str(sorted_rows[weaponCount-1]['seconds'])+" seconds")
    return sorted_rows[weaponCount-1]['seconds']

def getAvgTime(p, area, team, side, weaponCount): # function to get average time entering a certain area by a team on a specific side with a specified number of SMGs or Rifles
    rows = p.getRows(area, team, side)
    rows_by_round = enterArea(rows)
    
    roundCount = 0
    timer = 0
    rifleRows=[]
    
    for i in range(15): #traverse the 2d array to find rows with rifle or SMG in inventory
        if len(rifleRows) >=2:
            roundCount+=1
            timer += getTimer(rifleRows, weaponCount)
        rifleRows=[]
        for j in range(5):
            row = rows_by_round[i][j]
            if (row is not None):
                if "Rifle" or "SMG" in extractWeaponClass(row):
                    print("RIFLE or SMG at: " + str(row['seconds'])+" seconds in round: "+str(row['round_num']))
                    rifleRows.append(row)
    if len(rifleRows) >=2: # edge case to add final time added for last round
            roundCount+=1
            timer += getTimer(rifleRows, weaponCount)
            
    return (timer/roundCount)  


def main():
    p1 = ProcessGameState('game_state_frame_data.parquet')
    boundary = [((-1735, 250),(-2024,398)), ((-2024,398), (-2806, 742)),((-2806,742), (-2472, 1233)), ((-2472, 1233),(-1565, 580)), ((-1565, 580), (-1735,250))] #edges of boundary defined here
    rows = p1.getBoundaryRows(boundary)
    for i in rows:
        row = p1.df.iloc[i]
        team = row['team']
        side = row['side']
        round = row['round_num']

        if team == "Team2" and side == 'T':
            print(round)

    time = getAvgTime(p1, "BombsiteB", "Team2", "T", 2) # Retrieving average timer for Team 2 on T side to enter BombsiteB with atleast 2 rifles or SMGs
    print("Average timer for Team 2 on T side to enter BombsiteB with atleast 2 rifles or SMGs is :" + str(time)+ " seconds")
main()

