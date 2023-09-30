from boto3 import client
from bs4 import BeautifulSoup
from csv import writer
from re import sub
from requests import get

S3 = client(
	"s3",
	aws_access_key_id = "",
	aws_secret_access_key = ""
)
SES = client(
	"ses",
	aws_access_key_id = "",
	aws_secret_access_key = "",
	region_name = ""
)
SSM = client(
	"ssm",
	aws_access_key_id = "",
	aws_secret_access_key = "",
	region_name = ""
)
bucket = ""

oddValues = ["-"]
firstLink = "https://www.zameen.com/Homes/Karachi_DHA_Defence-213-1.html"
marla = 30.22
kanal = 604.44
thousand = 1000
lakh = 100 * thousand
crore = 100 * lakh
arab = 100 * crore
general = [
	"Identity",
	"Link",
	"Location",
	"Area",
	"Beds",
	"Baths",
	"Price"
]
special1 = [
	"ATM Machines",
	"Accessible by Road",
	"Balloted",
	"Barbeque Area",
	"Boundary Lines",
	"Boundary Wall",
	"Broadband Internet Access",
	"Business Center or Media Room in Building",
	"CCTV Security",
	"Cafeteria/Canteen",
	"Central Air Conditioning",
	"Central Heating",
	"Communal/Shared Kitchen",
	"Community Centre",
	"Community Gym",
	"Community Lawn or Garden",
	"Community Swimming Pool",
	"Conference Room in Building",
	"Corner",
	"Day Care Centre",
	"Dining Room",
	"Disputed",
	"Double Glazed Windows",
	"Drawing Room",
	"Electricity",
	"Electricity Backup",
	"Elevator or Lift",
	"Facilities for Disabled",
	"File",
	"First Aid or Medical Centre",
	"Flooring",
	"Furnished",
	"Gym",
	"Intercom",
	"Irrigation",
	"Jacuzzi",
	"Kids Play Area",
	"Land Fertility",
	"Laundry Room",
	"Laundry or Dry Cleaning Facility",
	"Lawn or Garden",
	"Lobby in Building",
	"Lounge or Sitting Room",
	"Maintenance Staff",
	"Mosque",
	"Nearby Hospitals",
	"Nearby Public Transport Service",
	"Nearby Restaurants",
	"Nearby Schools",
	"Nearby Shopping Malls",
	"Nearby Water Resources",
	"Park Facing",
	"Perimeter Fencing",
	"Pet Policy",
	"Possesion",
	"Powder Room",
	"Prayer Room",
	"Public Parking",
	"Satellite or Cable TV Ready",
	"Sauna",
	"Security Staff",
	"Service Elevators in Building",
	"Sewerage",
	"Steam Room",
	"Study Room",
	"Sui Gas",
	"Swimming Pool",
	"Tube Wells",
	"Underground Parking",
	"Waste Disposal",
	"Water Supply"
]
special2 = [
	"Built in year",
	"Distance From Airport (kms)",
	"Elevators",
	"Floor",
	"Floors",
	"Floors in Building",
	"Kitchens",
	"Parking Spaces",
	"Servant Quarters",
	"Store Rooms"
]
ignore = [
	"Bathrooms",
	"Bedrooms",
	"Business and Communication",
	"Community Features",
	"Healthcare Recreational",
	"Main Features",
	"Nearby Locations and Other Facilities",
	"Other Business and Communication Facilities",
	"Other Community Facilities",
	"Other Facilities",
	"Other Healthcare and Recreation Facilities",
	"Other Land Features",
	"Other Main Features",
	"Other Nearby Places",
	"Other Rooms",
	"Plot Features",
	"Rooms"
]
Source = "usman.sikandar98@gmail.com"
Destination = {
	"ToAddresses": [Source]
}
Message = {
	"Subject": {
		"Charset": "UTF-8",
		"Data": "ZAMEEN"
	},
	"Body": {
		"Html": {
			"Charset": "UTF-8",
			"Data": None
		}
	}
}

def get_num_from_text(text):
	return float(sub("[a-zA-Z]|\s|,|:", "", text).strip("."))

def oddValuesOk(text):
	if text in oddValues:
		return 0.0
	return get_num_from_text(text)

def oddValuesNotOk(text):
	if text in oddValues:
		return 56789.01234
	return get_num_from_text(text)

def get_correct_next_sibling(element):
	while True:
		if element.next_sibling.name == "style":
			element = element.next_sibling
		else:
			return element.next_sibling

def a1(previousLink):
	soup = BeautifulSoup(get(previousLink).text, "html.parser")
	try:
		return "https://www.zameen.com" + soup.find("div", {"role": "navigation"}).find("a", {"title": "Next"}).get("href")
	except AttributeError:
		links = SSM.get_parameter(Name = "param3")["Parameter"]["Value"].split()
		links.append(links.pop(0))
		SSM.put_parameter(Name = "param3", Value = "\n".join(links), Overwrite = True)
		link = links[0]
		if link == firstLink:
			SSM.put_parameter(Name = "param2", Value = str(int(SSM.get_parameter(Name = "param2")["Parameter"]["Value"]) + 1), Overwrite = True)
		return link

def b2_1(area):
	if "Kanal" in area:
		return get_num_from_text(area) * kanal
	if "Marla" in area:
		return get_num_from_text(area) * marla
	if "Sq. Yd." in area:
		return get_num_from_text(area)
	#separate handling for odd cases
	if area in oddValues:
		return 56789.01234
	raise Exception("Area: " + area)

def b2_2(price):
	if "Arab" in price:
		return get_num_from_text(price) * arab
	if "Crore" in price:
		return get_num_from_text(price) * crore
	if "Lakh" in price:
		return get_num_from_text(price) * lakh
	if "Thousand" in price:
		return get_num_from_text(price) * thousand
	#separate handling for odd cases
	if price in oddValues:
		return 56789.01234
	if price[-1].isdigit():
		return 56789.01234
	raise Exception("Price: " + price)

def b2_3(amenities):
	var = [0] * len(special1)
	if amenities:
		for amenity in amenities:
			if ":" in amenity:
				pass
			elif amenity in special2:
				pass
			elif amenity in ignore:
				pass
			elif amenity in special1:
				var[special1.index(amenity)] = 1
			else:
				raise Exception("1: " + amenity)
	return var

def b2_4(amenities):
	var = [0.0] * len(special2)
	if amenities:
		found = []
		for i, amenity in enumerate(amenities):
			if ":" in amenity:
				previousAmenity = amenities[i - 1]
				if previousAmenity in ignore:
					pass
				elif previousAmenity in special2:
					var[special2.index(previousAmenity)] = get_num_from_text(amenity)
					found.append(previousAmenity)
				else:
					raise Exception("2: " + previousAmenity)
		for amenity in amenities:
			if amenity in special2:
				if not amenity in found:
					var[special2.index(amenity)] = 1.0
	return var

def b2(propertyLink):
	try:
		print(propertyLink)
		soup = BeautifulSoup(get(propertyLink).text, "html.parser")
		location = [x.next_sibling.text for x in soup.find_all("div", {"aria-label": "Link delimiter"})]
		try:
			amenities = [x for x in get_correct_next_sibling(soup.find("h3", text = "Amenities")).stripped_strings]
		except AttributeError:
			amenities = False
		return [
			location.pop(),
			propertyLink,
			" > ".join(location),
			b2_1(soup.find("span", {"aria-label": "Area"}).text),
			oddValuesOk(soup.find("span", {"aria-label": "Beds"}).text),
			oddValuesOk(soup.find("span", {"aria-label": "Baths"}).text),
			b2_2(soup.find("span", {"aria-label": "Price"}).text),
		] + b2_3(amenities) + b2_4(amenities)
	except Exception as e:
		raise Exception(propertyLink + "<br>" + str(e))

def c3(link):
	var1 = link.split("/")
	var2 = var1[-1].split("-")
	return str(int(SSM.get_parameter(Name = "param2")["Parameter"]["Value"]) + 1) + "/" + var2[0] + "/" + var1[3] + "/" + var2[-1][:-4] + "csv"

def lambda_insider():
	rows = [general + special1 + special2]
	previousLink = SSM.get_parameter(Name = "param1")["Parameter"]["Value"]
	link = a1(previousLink)
	soup = BeautifulSoup(get(link).text, "html.parser")
	for li in soup.find_all("li", {"role": "article"}):
		propertyLink = "https://www.zameen.com" + li.article.div.a.get("href")
		if "/Property/" in propertyLink:
			rows.append(b2(propertyLink))
	with open("/tmp/.csv", "w", newline = "") as csv:
		writer(csv, dialect = "excel").writerows(rows)
	S3.upload_file("/tmp/.csv", bucket, c3(link))
	SSM.put_parameter(Name = "param1", Value = link, Overwrite = True)

def lambda_handler(event, context):
	try:
		lambda_insider()
	except Exception as e:
		Message["Body"]["Html"]["Data"] = str(e)
		SES.send_email(Source = Source, Destination = Destination, Message = Message)