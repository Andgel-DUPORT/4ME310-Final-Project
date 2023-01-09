import geocoder
import GoogleEarthAPI

# Use the geocoder library to determine the latitude and longitude of the location
location = 'San Francisco, CA'
g = geocoder.google(location)
lat = g.latlng[0]
lng = g.latlng[1]

# Use the Google Earth API to request the satellite image for the location
image = GoogleEarthAPI.fetch(lat=lat, lng=lng)