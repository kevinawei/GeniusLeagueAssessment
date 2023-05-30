# Genius League SWE Assessment 
# By Kevin Wei
# All source code can be found in ProcessGameState.py and GeniusLeague.ipynb. All sample output and graphs/figures will be included here but can be tested in GeniusLeague.ipynb
# Answers to each individual question with code snippets and explanations can be found below

## Dependencies
1. Pandas
2. Numpy
3. matplotlib (for heatmap and coordinate plotting)
4. pyarrow (for read_parquet)

# 1. 
## a. 
### When initializing a ProcessGameState object, it takes in a parquet file and using pandas read_parquet function loads the data into a pandas dataframe

``` python
import pandas as pd
class ProcessGameState():
    def __init__(self, filename):
        self.df = pd.read_parquet(filename, engine='pyarrow')

```

``` python
p1 = ProcessGameState('game_state_frame_data.parquet')
```


## b. 
### Now we set the boundary from the coordinates provided and call the GetBoundaryRows method with said boundary
```python
boundary = [((-1735, 250),(-2024,398)), ((-2024,398), (-2806, 742)),((-2806,742), (-2472, 1233)), ((-2472, 1233),(-1565, 580)), ((-1565, 580), (-1735,250))] #edges of boundary defined here
rows = p1.getBoundaryRows(boundary)
```

### The getBoundaryRows method iterates through all rows of our pandas dataframe and calls the checkBoundary method to check the coordinates extracted from each individual row. If the given row is found to be inside the boundary we add the row number to a list which contains all rows that are within the boundary. That list is what is returned from this method

```python
    def getBoundaryRows(self, boundary):
        withinBoundary = []
        for row in self.df.iterrows():
            c = (row[1].x, row[1].y, row[1].z) # create list to hold singular xyz coordinate for each row
            if self.checkBoundary(c, boundary):
                 withinBoundary.append(row[0])
        return withinBoundary
```
### The checkBoundary method first checks that given coordinate's z bound is within a certain range before implementing the raycast algorithm. This algorithm determines if a given point is inside of a given polygon by first checking that the point is within the y range of the current edge. The second statement checks that a raycasted horizontal line would pass through one of the edges of the polygon given that the first condition holds true. The function keeps track of how many times a horizontal raycast line from the point crosses edges from the polygon. If the number is an odd number then the point is inside the polygon. If the number of times it crosses the edges is even then the point is outside of the polygon.
```python
    def checkBoundary(self,c, boundary): # uses the raycast odd number rule to detect if a point is within the boundaries of a polygon
        x,y,z = c #x, y and z coordinates for current row we are checking
        if z>421 or z<285: # first check z bound
            return False
        else: # then implement raycast algorithm
            count = 0
            
            for edge in boundary:
                (x1, y1), (x2, y2) = edge
                if (y < y1) != (y<y2) and x < x1 + ((y-y1)/(y2-y1))*(x2-x1): # first part of expression checks that the point is in the y range of the current edge
                    count +=1

            return count%2 == 1
```
## c.

### Method to extract weapon types from a row

![](/screenshots/weapons.png)


# 2
## a. 

## We can see from the output below that Team 2 was in the specified boundary during only a singular round and only with 2 of their players, thus it was not a common strategy for them to enter via this boundary

![](/screenshots/2a.png)

## We can plot the data to see all the individual coordinates compared to the boundary lines to confirm the above

![](/screenshots/2a2.png)


## b. 
## The methodology for retrieving the average timer that Team 2 on T side enters BombsiteB with at least 2 rifles or SMGs is as follows. 
## First the getRows() method is called to return rows given the filters specified. 
```python
    def getRows(self, area, team, side): # get rows filtered by area, team, and side
        rows = []
        for row in self.df.iterrows():
            row = row[1]
            if ((area == row['area_name']) and (team == row['team']) and (side == row['side']) and (row['is_alive'])):
                rows.append(row)
        return rows
```
## Once those rows have been retrieved, we traverse the rows and store the first instance per player per round into a 2d array (the index of the array should matchup with the round number - 1, if the team in question is team 2 then the index will matchup with the round number -16). This marks the first time that a player has entered BombsiteB in a given round. 
``` python
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
```
## We can then traverse our 2d array and extract the weapon classes from the inventory of these rows and check if they contain SMG or Rifle. If they do then we append them to a new 1d array which we then pass to another function if the number of rows in the array exceeds the number of requested weapons (in this case it's 2 weapons so if it has a length >= 2). This getTimer() function sorts the array by the attribute['seconds'] and returns the earliest instance where >= 2 players entered the area. Since the array is sorted the value in question is at index [weaponCount-1]. We then take the average of the seconds for each round that meets the criteria and return that value.



```python
def getTimer(rows, weaponCount):  
    sorted_rows = sorted(rows, key=lambda x: x['seconds'], reverse=False)
    print("Requirements met at: "+ str(sorted_rows[weaponCount-1]['seconds'])+" seconds")
    return sorted_rows[weaponCount-1]['seconds']
```
## Here is the code for the outer most method which can be reused to search for the earliest instance of a team entering a given area on a given side with a specific gun count
```python

def getAvgTime(p, area, team, side, gunCount): # function to get average time entering a certain area by a team on a specific side with a specified number of SMGs or Rifles. p is a ProcessGameState object
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


time = getAvgTime(p1, "BombsiteB", "Team2", "T", 2) # Retrieving average timer for Team 2 on T side to enter BombsiteB with atleast 2 rifles or SMGs
print(str(time))
```
## Example output shows that average time for Team 2 on T side to enter BombsiteB with at least 2 rifles or SMGs is 33.5 seconds
![](/screenshots/getTime.JPG)


## c.

## Based on the below heatmap we can see that Team 2 likes to position themselves most commonly around (-700,-100), relatively frequently at roughly between -800 and -700 x and between -100 and -200 y, and around (100,-950) and (250,900).

![](/screenshots/2c.png)



# 3
## I would propose the idea of hosting the script as a webapp using a python framework like Streamlit. The application could be hosted on a number of hosting sites such as through github or google app engine. The benefit of using a webapp is we can implement a UI to make utilizing the script easier for the coaching staff and they will be able to access the web application from any device with internet connectivity. The UI will be simple and straightforward enough for the coaching staff to use and will include options for coaches to upload their own parquet/pickle files or potentially select from a database of files from certain matches. Initially there will be 2 different data request options to choose from (this could easily be expanded upon later if further functionality is requested). The first would be to request info with certain filters available. For example they can request the average time it took for Team 1 to leave their spawn on T side with 3 or more rifles. The second option would be to generate a heatmap for positional data. For example they could generate a heatmap for Team 2 on T side after they have planted the bomb to see where they like to hide post plant. This heatmap could be overlayed with the actual in game map to further improve visual clarity. Below is a mockup of what the UI could look like for the first data request function
![](/screenshots/UI.JPG)

## This application wouldn't require much additional coding beyond creating a simple UI and hooking up the already existing script to the UI. Additional work would include designing the UI and deploying the application which should take less than a week's worth of time in total to get the app deployed.