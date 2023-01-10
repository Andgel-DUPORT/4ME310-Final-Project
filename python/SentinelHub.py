import geocoder
import requests
from PIL import Image
import sentinelhub
from sentinelhub import SHConfig, WmsRequest, MimeType, BBox, CRS
import numpy as np
import datetime
from matplotlib import pyplot as plt
from math import radians, cos, pi

# Set up Sentinel Hub configuration
config = SHConfig()
config.instance_id = '9e07c1c1-4768-4a9e-b0c1-81e02e6fa9cb'
config.sh_client_id = '00f5bcf1-7dec-49e4-af76-0acf65c261c0'
config.sh_client_secret = 'zPs4%0{/!i<Y+^+FDHR(F5iGPXtOY4PQ?~~@@GjZ'
config.save()


def create_square(meter, lat, lon):
    # approximate radius of earth in meters
    R = 6371e3

    # convert distance to radians
    lat_distance = meter / R
    lon_distance = meter / (R * cos(radians(lat)))

    # convert radians to degrees
    lat_distance_deg = lat_distance * 180 / pi
    lon_distance_deg = lon_distance * 180 / pi

    # create bounding box around center point
    min_lat = lat - lat_distance_deg
    max_lat = lat + lat_distance_deg
    min_lon = lon - lon_distance_deg
    max_lon = lon + lon_distance_deg

    return [min_lon, min_lat, max_lon, max_lat]


def get_satellite_image(lat, lon, meter_radius):
    # Set the size of the image you want to retrieve
    img_width = 1920
    img_height = 1920

    generated_bbox = BBox(bbox=create_square(meter_radius, lat, lon), crs=CRS.WGS84)
    print(generated_bbox)

    # Set the time of the most recent image you want to retrieve
    time_range = (datetime.datetime.utcnow() - datetime.timedelta(days=365), datetime.datetime.utcnow())

    # Set the cloud coverage threshold (between 0 and 100)
    cloud_coverage_threshold = 0

    # Create a Sentinel Hub WMS request
    wms_request = WmsRequest(
        layer="TRUE_COLOR_L2A",
        width=img_width,
        height=img_height,
        time='latest',
        maxcc=cloud_coverage_threshold,
        image_format=MimeType.PNG,
        bbox=generated_bbox,
        data_collection=sentinelhub.DataCollection.SENTINEL2_L1C
    )
    # Execute the Sentinel Hub WMS request
    wms_img = wms_request.get_data()

    print(
        "There are %d Sentinel-2 images available for this las 365days with cloud coverage less than %1.0f%%."
        % (len(wms_img), wms_request.maxcc * 100.0)
    )
    print("These %d images were taken on the following dates:" % len(wms_img))
    for index, date in enumerate(wms_request.get_dates()):
        print(" - image %d was taken on %s" % (index, date))

    # Convert the image to a NumPy array
    return wms_img


if __name__ == '__main__':
    # Get the user's location
    g = geocoder.ip('me')
    latitude, longitude = g.latlng
    print(f'Your location: {latitude}, {longitude}')
    # Get the satellite image of the surrounding area
    image = get_satellite_image(latitude, longitude, 1000)
    # Display the image
    for i in image:
        plt.imshow(i)
    plt.show()
