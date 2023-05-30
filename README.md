# Genius League SWE Assessment 
# By Kevin Wei
# All source code can be found in ProcessGameState.py and GeniusLeague.ipynb. 
# Answers to each individual question with code snippets and explanations can be found below

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

## We can see from the below code snippet that Team 2 was in the specified boundary during only a singular round and only with 2 of their players, thus it was not a common strategy for them to enter via this boundary

![](/screenshots/2a.png)

## We can plot the data to see all the individual coordinates compared to the boundary lines to confirm the above

![](/screenshots/2a2.png)


## b. 


## c.

## Based on the below heatmap we can see that Team 2 likes to position themselves most commonly around (-700,-100), relatively frequently at roughly between -800 and -700 x at between -100 and -200 y, and around (100,-950)

![](/screenshots/2c.png)



# 3
## I would propose the idea of hosting the script as a webapp using a python framework like Streamlit. The application could be hosted on a number of free hosting sites such as through github or google app engine. The benefit of using a webapp is we can implement a UI to make utilizing the script easier for the coaching staff and they will be able to access the web application from any device with internet connectivity. The UI will be simple and straightforward for the coaching staff to use and will include options for coaches to upload their own parquet/pickle files or potentially select from a database of files from certain matches. Initially there will be 2 different data request options to choose from (this could easily be expanded upon later if further functionality is requested). The first would be to request info with certain filters available. For example they can request the average time it took for Team 1 to leave their spawn on T side with 3 or more rifles. The second option would be to generate a heatmap for positional data. For example they could generate a heatmap for Team 2 on T side after they have planted the bomb to see where they like to hide post plant. This heatmap could be overlayed with the actual in game map to further improve visual clarity. Below is a mockup of what the UI could look like for the first data request function
![](/screenshots/UI.PNG)

## This application wouldn't require much additional coding beyond creating a simple UI and hooking up the already existing script to the UI. Additional work would include designing the UI and deploying the application which should take less than a week's worth of time in total to get the app deployed.