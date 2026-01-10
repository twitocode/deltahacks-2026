Our simplifications and constraints
General idea:
Split the map into a grid containing squares 
An agent starts at an inputted coordinate from the frontend (the hiker’s last known location)
Each square will have its own XY (longitude and latitude) and Z values (Z being the elevation)
We want to avoid a lot of ML/DL algorithms because we lack data on where missing persons were found, there only really exist datasets where missing persons were last seen
The agent will follow rules due to various factors 
Depending on age, sex, experience, inputted from the front end, the agent will have a certain weight as to their actions (i.e. experience hikers are more likely to go uphill) - from the frontend
Things like temperature, precipitation, and wind will impact the probability that the agent will move to an adjacent square - from the backend apis
Elevation can restrict movement paths
The agent will also follow certain lost hiker patterns as detailed before
Additionally, agents will stay next to trails and roads
Overall, the algorithm will follow human behaviour patterns

The idea: 
The heat map is generated in intervals of 15 minutes from the time last seen to the current time. Additionally, an extra 12 hours will be generated afterwards. In this, use websocket to send the data in real time to minimize processing time.


Give feedback and start the backend.

https://www.mdpi.com/2504-446X/9/9/628 
Assume monte carlo simulation 
