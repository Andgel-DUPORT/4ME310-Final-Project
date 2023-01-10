import math

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np


# take a tree id and return the tree in database
def find_tree(tree_id, df):
    row = df.loc[df['IDBASE'] == tree_id]
    return row


# take a dataframe and scale it using standard scaling method
def scale_df(df):
    scaler = StandardScaler()
    df = scaler.fit_transform(df)
    return df


# take a formatted dataframe with the id of the tree, the column for x value, and the column for y value and give back the same dataset with a new column attributing a cluster
def create_kmean_df(df, nb_clusters):
    df = df.loc[:, ['CIRCUMFERENCE (cm)', 'HEIGHT (m)']]
    df = scale_df(df)
    kmeans = KMeans(n_clusters=nb_clusters)
    kmeans.fit(df)
    return kmeans.labels_


def remove_different_stage_of_developpment(df):
    element_to_keep = df.at[0, 'STAGE OF DEVELOPMENT']
    df = df[df['STAGE OF DEVELOPMENT'] == element_to_keep]
    return df


def remove_different_type_of_trees(df):
    element_to_keep = df.at[0, 'TYPE']
    df = df[df['TYPE'] == element_to_keep]
    return df


def remove_different_domanialite(df):
    element_to_keep = df.at[0, 'DOMANIALITE']
    df = df[df['DOMANIALITE'] == element_to_keep]
    return df

def remove_height_between(low, high, df):
    mask = (df["HEIGHT (m)"] < low) | (df["HEIGHT (m)"] > high)
    df = df[~mask]
    return df

def remove_circumference_between(low, high, df):
    mask = (df["CIRCUMFERENCE (cm)"] < low) | (df["CIRCUMFERENCE (cm)"] > high)
    df = df[~mask]
    return df

# Take a tree and in entry and give all similar trees within the trust interval in a dataframe
def recommend_a_set_of_tree(df, tree_ID):
    clustered = create_kmean_df(df, 5)
    df['kmeans'] = clustered
    cluster_label_to_keep = find_tree(tree_ID, df)['kmeans'].values[0]
    # Use boolean indexing to select only the rows that have the specified cluster label
    df = df[df['kmeans'] == cluster_label_to_keep]
    return df


# take two lat/long tuple and return the distance in meters between them
def calculate_distance_from_point(point1, point2):
    if point2 == "":
        return 0
    coordinates_list = point1.split(',')
    point1 = tuple(map(float, coordinates_list))
    coordinates_list = point2.split(',')
    point2 = tuple(map(float, coordinates_list))
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
    dfcopy = df.copy()
    df.loc[:, 'Distance From Point'] = dfcopy['geo_point_2d'].apply(lambda x: calculate_distance_from_point(point, x))
    df.sort_values(by='Distance From Point', inplace=True)
    return df


# take a radius in meter and drops all the outside elements
def filter_by_radius(m_radius, df, user_position):
    distanceDf = sort_by_loc(df, user_position)
    mask = distanceDf['Distance From Point'] > m_radius

    # Use the mask to drop the unwanted rows
    return distanceDf[~mask]


# take the user preferences and filter a dataframe according to it
# def filter_by_preferences(df):
#     df = filter_by_radius(df)
#     return df

# take tree values and create a new tree to be inserted in the dataframe
def create_tree(domanialite, frenchname, type, species, stageofdev, circumference, height, df):
    data = pd.Series({"IDBASE": 0,
            "LOCATION TYPE": "arbre",
            "DISTRICT": "",
            "ADRESS COMPLEMENT": "",
            "NUMBER": "",
            "LOCATION / ADDRESS": "",
            "IDEMPLACEMENT": "",
            "DOMANIALITE": domanialite,
            "FRENCH NAME": frenchname,
            "TYPE": type,
            "SPECIES": species,
            "VARIETY": "",
            "CIRCUMFERENCE (cm)": circumference,
            "HEIGHT (m)": height,
            "STAGE OF DEVELOPMENT": stageofdev,
            "REMARKABLE": "",
            "geo_point_2d": ""})
    df.loc[0] = data
    return df


def process_with_a_new_tree(domanialite, frenchname, type, species, stageofdev, min_circumference, max_circumference,
                            min_height,
                            max_height, df, radius, position):
    df = create_tree(domanialite, frenchname, type, species, stageofdev, (max_circumference - min_circumference) / 2,
                     (max_height - min_height) / 2, df)
    result = recommend_a_set_of_tree(df, 0)
    result.reset_index
    if radius is not None :
        result = filter_by_radius(radius, result, position)
    if type is not None :
        result = remove_different_type_of_trees(result)
    if domanialite is not None :
        result = remove_different_domanialite(result)
    if stageofdev is not None :
        result = remove_different_stage_of_developpment(result)
    if min_height is not None and max_height is not None :
        result = remove_height_between(min_height, max_height, result)
    if min_circumference is not None and max_height is not None:
        result = remove_circumference_between(min_circumference,max_circumference, result)
    return result


if __name__ == '__main__':
    dfp = pd.read_csv("../resources/les-arbres.csv", encoding='latin1', sep=';')
    print(dfp.columns)
    result = process_with_a_new_tree("ALIGMENT", "Marronier", "Aesculus", "hippocastanum", "YOUNG", 10, 30, 0, 10,dfp,1000,"48.84129152798434, 2.373479285945392")
    print(result)
