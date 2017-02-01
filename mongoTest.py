#AIzaSyDdVDTvUM71KwVvUMeP7yBU6KzkuAnYfCg

import requests
import re
from bson.json_util import dumps
from pymongo import MongoClient
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin

app = Flask(__name__)
api = Api(app)
CORS(app)

client = MongoClient()
db = client.windsorHack


def getGeo(street,city,prov):
	requestStr = "https://maps.googleapis.com/maps/api/geocode/json?address={0}+{1}+{2}&key=AIzaSyDdVDTvUM71KwVvUMeP7yBU6KzkuAnYfCg"
	street = re.sub("r'\W+'","",street.split("-")[-1]).replace(" ","+")
	urlAddress = requestStr.format(street, city, prov)
	returnedJson = requests.get(urlAddress).json()
	try:
		lnglat =  returnedJson["results"][0]["geometry"]["location"]
		lnglat = [lnglat["lng"],lnglat["lat"]]
		return lnglat
	except:
		print urlAddress
		return 0

#42.319124, -83.038713

def getLocalAddresses(add):
	cursor = db.locations.find()

def addGeoToAddresses():
	cursor = db.locationsOriginal.find()
	for document in cursor:
		for i in document["WindsorAddresses"]:
			street = str(i["Street"])
			city = str(i["City"])
			prov = str(i["Prov"])
			postal = str(i["Postal"])
			lnglat = getGeo(street,city,prov)
			print lnglat
			if(lnglat != 0):
				db.locations.insert({"loc":{"type": "Point","coordinates":lnglat},"Street":street,"City":city,"Prov":prov,"Postal":postal,"Lng":lnglat[0],"Lat":lnglat[1]})

def getAddressesNearMeters(street,city,prov,radius):
	earthRadius = 6378.1
	radiusVal = ((radius / 1000.0)/ earthRadius) * 2
	geoArray = getGeo(street,city,prov)
	print geoArray
	print radiusVal
	cursor = db.locations.find({"loc":{"$geoWithin":{"$centerSphere":[geoArray,radiusVal]}}})
	return dumps(cursor)
	#for document in cursor:
	#	print document

class LocationHandler(Resource):
	def get(self,street,city,prov,radius):
		return getAddressesNearMeters(street,city,prov,radius)

class DBHandler(Resource):
	def get(self):
		return dumps(db.locations.find())

api.add_resource(LocationHandler, "/api/collide/<string:street>+<string:city>+<string:prov>+<int:radius>")
api.add_resource(DBHandler,"/api/getall")
if __name__ == '__main__':
	#addGeoToAddresses()
	app.run(host='66.228.44.27',debug=True)
