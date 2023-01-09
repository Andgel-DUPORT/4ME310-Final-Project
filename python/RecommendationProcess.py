import math

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
import numpy as np


# take a tree id and return the tree in database
def find_tree(tree_id, df):
    row = df.loc[df['IDBASE'] == tree_id]
    return row


# Take a tree and in entry and give all similar trees within the trust interval in a dataframe
def recommend_tree():
    return


# take two lat/long tuple and return the distance in meters between them
def calculate_distance_from_point(point1, point2):

    d_lat = point2[0] - point1[0]
    d_lng = point2[1] - point2[1]

    temp = (
            math.sin(d_lat / 2) ** 2
            + math.cos(point1[0])
            * math.cos(point2[0])
            * math.sin(d_lng / 2) ** 2
    )

    return 6373.0 * (2 * math.atan2(math.sqrt(temp), math.sqrt(1 - temp)))


# take a location and sort all the trees by proximity to this location
def sort_by_loc(df, point):
    df['Distance From Point'] = df['geo_point_2d'].apply(calculate_distance_from_point(point))
    df.sort_values(by='Distance From Point')
    return df


# take a radius in meter and drops all the outside elements
def filter_by_radius(radius, df):
    distanceDf = sort_by_loc(df)
    for index in reversed(distanceDf.Index()):
        if distanceDf.at[index, 'Distance From Point'] < radius:
            break
        distanceDf.drop(index)
    return distanceDf


# take the user preferences and filter a dataframe according to it
def filter_by_preferences(df):
    df = filter_by_radius(df)
    return df
