# twitter-crawler

Twitter Crawler and Analyser 

University Of Glasgow

Computer Science 2020


## Required Dependencies 
* tweepy
* pymongo
* matplotlib
* networkx

## File Locations

* The data crawler is located in the Data crawl file. This is a python file
* The data analyser is in a jupyter notebook TweetAnalysers (1).ipynb

## How to Run 
To run the data crawler

 1- unzip the txt file 
 
 2- Connect to mongodb
 
 3- python3 Hybrid.py (Crawl data based on both STREAM and REST API's)
 
 4- python3 Stream.py (Crawl data based on STREAM API)
 

The data will then be stored in mongodb. 
Note: Config.py has the twitter credentials, this can be changed and replaced with your own. 


