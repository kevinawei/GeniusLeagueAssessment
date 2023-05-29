# Genius League SWE Assessment 
# By Kevin Wei
# All source code can be found in ProcessGameState.py and GeniusLeague.ipynb

# 1. 
## a. 
### When initializing a ProcessGameState object, it takes in a parquet file and using pandas read_parquet function loads the data into a pandas datafram
``` python
p1 = ProcessGameState('game_state_frame_data.parquet')
```

``` python
class ProcessGameState():
    def __init__(self, filename):
        self.df = pd.read_parquet(filename, engine='pyarrow')

```
## b. 
### Now we set the boundary from the coordinates provided and call the GetBoundaryRows method with said boundary
```python
boundary = [((-1735, 250),(-2024,398)), ((-2024,398), (-2806, 742)),((-2806,742), (-2472, 1233)), ((-2472, 1233),(-1565, 580)), ((-1565, 580), (-1735,250))] #edges of boundary defined here
rows = p1.getBoundaryRows(boundary)
```

### The getBoundaryRows method iterates through all rows of our pandas dataframe and calls the checkBoundary method to check the coordinates extracted from each individual row

```python
    def getBoundaryRows(self, boundary):
        withinBoundary = []
        for row in self.df.iterrows():
            c = (row[1].x, row[1].y, row[1].z) # create list to hold singular xyz coordinate for each row
            if self.checkBoundary(c, boundary):
                 withinBoundary.append(row[0])
        return withinBoundary
```
### This method first checks that given coordinate's z bound is within a certain range before implementing the raycast algorith. This algorithm determines if a given point is inside of a given polygon by 
```python
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
```
## c.

### Method to extract weapon types from a row

![](/screenshots/weapons.png)


# 2
## a. 

## We can see from the below code snippet that Team 2 was in the specified boundary during only a singular round and only with 2 of their players, thus it was not a common strategy for them to enter via this boundary

![](/screenshots/2a.png)

## We can plot the data to see all the individual coordinates compared to the boundary lines

![](/screenshots/2a2.png)


## b. 


## c.

![](/screenshots/2c.png)