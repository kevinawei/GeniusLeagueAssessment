import pandas as pd


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
    
    def extractWeaponClass(self, row):
        weapons = []
        for item in row['inventory']:
            weapons.append(item['weapon_class'])
        return weapons





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

main()