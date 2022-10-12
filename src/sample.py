## General Imports
import requests
import json
import pandas as pd
import time
import requests 
import numpy as np
import os
import sys

## Image Manipulation
import urllib
from PIL import Image
import matplotlib.pyplot as plt
import io

## MongoDB Connection
from pymongo import MongoClient

## MongoDB Upload
import pickle
from bson.binary import Binary, USER_DEFINED_SUBTYPE

## Module Imports
import extract_images as eis

#def save_locally(): 
     #for (file_num, image) in enumerate(image_links): 
     #    file_name = os.path.join(folder, "test", str(file_num))
     #    ei.save_image(image, file_name)

def get_database():
 
   # Provide the mongodb atlas url to connect python to mongodb using pymongo
    connection_string = "mongodb://localhost:27017"
 
   # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(connection_string)
 
   # Return the connection to the instance 
    return client


if __name__ == "__main__":

# Data Processing - Data Reading

    ## Read the JSON file that contains the sneaker information from sneakers-api 
    root = os.path.abspath(os.curdir)
    data = os.path.join(root, "sneaker_json.json")

    with open(data, "rb") as read:
        sneaker_json = json.load(read)
        sneaker_df = pd.read_json(data)

    ## Write a function that check's whether the unqiue_id's are still valid -- Future Steps

# Data Processing - Data Cleaning

    ## Let's find any sneakers re-sale items that are not specifically sneakers, and filter them out
    sneaker_df = sneaker_df[sneaker_df['category'] == 'sneakers']

    ## We have a problem where some of our shoeNames have the backward slash that throw an error when
    ## creating the directory, so let's change '/' to '|'
    sneaker_df['shoeName'] = sneaker_df['shoeName'].apply(lambda x: x.replace('/', '|'))
    any(sneaker_df['shoeName'].str.find('/') != -1)

    ## We know that none of our shoeNames are NA
    assert(len(sneaker_df) == len(sneaker_df['shoeName']))

    ## Let's set our dataframe index to be our unique_id which will be the styleID
    sneaker_df = sneaker_df.set_index('shoeName')    

    ## We're going to take the shoe_name, silhoutte, styleId, and colorway to be our unique_query parameters
    query = pd.DataFrame(sneaker_df[['silhoutte', 'colorway']].agg('-'.join, axis = 1), columns=['query'])

    ## Let's add the query column to our sneaker's dataframe
    sneaker_df['query'] = (query.index + '-' + query['query']).to_list()

    ## Create Shoe Objects -- Future Steps

# Data Processing - Data Upload

    ## Creating/Checking directories for all of our sneakers 

    ## Create our directory for images
    eis.check_dir("images", True)
    imagesPath = os.chdir(os.path.join(root, "images"))


    sneaker_dict = sneaker_df.to_dict(orient = 'index')
    for (index, sneaker) in sneaker_dict.items(): 
        eis.check_dir(index, True)

    
    ## Establish connection to Database
    db = get_database()['sneakers']
    collection = db['test']

    ## Specify the driver path
    driver_path = os.path.join(root, 'chromedriver')
    driver = eis.select_driver(driver_path)

    ## Here we use the dict of our dataframe, and iterate through the key's, and passing the query keyword to our extract function. 
    ## We try opening the image url before we decide to save it, thus ensuring that we have an equal amount of images in our DB
    sneaker_dict = sneaker_df.to_dict(orient = 'index')
    max_num_links = 50

    try:
        for (index, sneaker_data) in sneaker_dict.items():
            eis.check_dir(index, True)
            query = sneaker_data["query"]
            path = os.path.join(root, index)
            url_paths = eis.extract(query, max_num_links, path, driver, 1) 
            print(len(os.listdir(os.path.join(path, index))), len(url_paths))
            assert(len(os.listdir(os.path.join(path, index))) == max_num_links & len(url_paths) == max_num_links)

            sneaker_dict[index]['url_paths'] = url_paths
            break;
        
        sneaker_df = pd.DataFrame.from_dict(sneaker_dict, orient = 'index')
        items = [{sneaker: details} for (sneaker,details) in sneaker_df.to_dict(orient='index').items()]
        collection.insert_many(items)
    except Exception as e:
        raise(e)


    



