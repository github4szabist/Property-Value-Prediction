from flask import Flask, redirect, render_template, request
from joblib import load
from markupsafe import Markup

joblibDict = {
	"Karachi": {
		"DHA": {
			"Home": "static/Karachi_DHA_Defence_Homes.joblib",
			"Plot": "static/Karachi_DHA_Defence_Plots.joblib"
		},
		"Bahria Town": {
			"Home": "static/Karachi_Bahria_Town_Karachi_Homes.joblib",
			"Plot": "static/Karachi_Bahria_Town_Karachi_Plots.joblib"
		}
	},
	"Lahore": {
		"DHA": {
			"Home": "static/Lahore_DHA_Defence_Homes.joblib",
			"Plot": "static/Lahore_DHA_Defence_Plots.joblib"
		},
		"Bahria Town": {
			"Home": "static/Lahore_Bahria_Town_Homes.joblib",
			"Plot": "static/Lahore_Bahria_Town_Plots.joblib"
		}
	},
	"Islamabad": {
		"DHA": {
			"Home": "static/Islamabad_DHA_Defence_Homes.joblib",
			"Plot": "static/Islamabad_DHA_Defence_Plots.joblib"
		},
		"Bahria Town": {
			"Home": "static/Islamabad_Bahria_Town_Homes.joblib",
			"Plot": "static/Islamabad_Bahria_Town_Plots.joblib"
		}
	}
}
unitDict = {
	"Sq. Yd.": 1.0,
	"Marla": 30.22,
	"Kanal": 604.44
}
decisionDict = {
	"No": 0,
	"Yes": 1
}
app = Flask(__name__)

def getLayer1Column(location):
	if not " > " in location:
		return "0_" + location
	return "0_" + location.split(" > ")[0]

@app.route("/")
def a1():
	return render_template("A.html")

@app.route("/1", methods = ["GET", "POST"])
def b2():
	if request.method == "POST":
		global category
		city = request.form["city"]
		place = request.form["place"]
		category = request.form["category"]
		global model
		global data
		global int64Ids
		global float64Ids
		global int64Options
		global float64Options
		global boolColumns
		global joblibAddress
		global rfAddress
		global gbAddress
		joblibAddress = joblibDict[city][place][category]
		rfAddress = joblibAddress[:-6] + "csvRF.png"
		gbAddress = joblibAddress[:-6] + "csvGB.png"
		model, data, int64Ids, float64Ids, typeAndLocationOptions, int64Options, float64Options, boolColumns = load(joblibAddress)
		typeAndLocationOptions_ = Markup("".join(typeAndLocationOptions))
		return render_template("B.html", city = city, place = place, category = category, typeAndLocationOptions = typeAndLocationOptions_)
	return redirect("/")

@app.route("/2", methods = ["GET", "POST"])
def c3():
	if request.method == "POST":
		global typeAndLocation
		global area
		global unit
		typeAndLocation = request.form["typeAndLocation"]
		area = request.form["area"]
		unit = request.form["unit"]
		
		
		
		layer1Column = getLayer1Column(typeAndLocation)
		print(layer1Column)
		df = data.loc[data[layer1Column] == 1]
		dfInt64 = df.select_dtypes(include = "int64")
		dfFloat64 = df.drop(["Area", "Price"], axis = 1).select_dtypes(include = "float64")
		
		
		
		ignoreInt64 = [x for x in dfInt64 if list(dfInt64[x].unique()) == [0]]
		ignoreFloat64 = [x for x in dfFloat64 if list(dfFloat64[x].unique()) == [0.0]]
		
		
		
		irrelevantInt64 = [x for x in int64Options if any(y in x for y in ignoreInt64)]
		irrelevantFloat64 = [x for x in float64Options if any(y in x for y in ignoreFloat64)]
		
		
		
		relevantInt64 = [x for x in int64Options if x not in irrelevantInt64]
		relevantFloat64 = [x for x in float64Options if x not in irrelevantFloat64]
		
		
		
		if relevantInt64 or relevantFloat64:
			upperPortion = "<h4>Fantastic! Just one more step. Please provide a detailed and accurate description of your "
			upperPortion += category
			upperPortion += " using the given features below.</h4><br><div class=\"row\">"
			upperPortion += "".join(relevantInt64)
			upperPortion += "".join(relevantFloat64)
			upperPortion += "</div><br>"
		else:
			upperPortion = ""
		
		
		
		if irrelevantInt64 or irrelevantFloat64:
			lowerPortion = "<h4>Caution! We have detected that "
			lowerPortion += category
			lowerPortion += "s similar to yours, based on the information you have provided, seldom or never have any of the features listed below. Only modify if sure; otherwise, leave as is.</h4><br><div class=\"row optional\">"
			lowerPortion += "".join(irrelevantInt64)
			lowerPortion += "".join(irrelevantFloat64)
			lowerPortion += "</div><br>"
		else:
			lowerPortion = ""
		
		
		
		return render_template("C.html", upperPortion = Markup(upperPortion), lowerPortion = Markup(lowerPortion))
	return redirect("/")

@app.route("/3", methods = ["GET", "POST"])
def d4():
	if request.method == "POST":
		inputPart1 = [decisionDict[request.form[x]] for x in int64Ids]
		inputPart2 = [float(area) * unitDict[unit]]
		inputPart3 = [float(request.form[x]) for x in float64Ids]
		inputPart4 = [0] * len(boolColumns)
		for i, column in enumerate(typeAndLocation.split(" > ")):
			inputPart4[boolColumns.index(str(i) + "_" + column)] = 1
		price = "{:,}".format(int(model.predict([inputPart1 + inputPart2 + inputPart3 + inputPart4])[0]))
		return render_template("D.html", price = price, rfAddress = rfAddress, gbAddress = gbAddress)
	return redirect("/")

if __name__ == "__main__":
	app.run(debug = True)