#imports the flask class from the flask module
from flask import Flask, render_template, jsonify

#import the shutil module
import shutil
import psutil

#create an instance of the class __name__ is a
#shortcut to find flask resources
app = Flask(__name__)


def get_storage_info():

	total, used, free = shutil.disk_usage("/")

	total_gb = round(total / (1024**3),2)
	used_gb = round(used / (1024**3),2)
	free_gb = round(free / (1024**3),2)

	return {
		"total":total_gb,
	    "used":used_gb,
	    "free":free_gb
	}

def get_cpu_info():
	cpu_usage = psutil.cpu_percent(interval=5)
	cpu_usage_per_core = psutil.cpu_percent(interval=5, percpu=True)
	temps = psutil.sensors_temperatures()

	if temps:
		return{"temperature": temps,
			   "total_usage":cpu_usage,
				"per_cpu":cpu_usage_per_core}
	else:
		temps = "this device has no avalible sensors"
		return{"temperature": temps,
			   "total_usage":cpu_usage,
				"per_cpu":cpu_usage_per_core}

def get_memory_info():
	memory = psutil.virtual_memory()

	return{
	"total" : round((memory.total / (1024**3)),2),
	"avalible" : round((memory.available / (1024 ** 3)),2),
	"used" : round((memory.used / (1024 ** 3)),2),
	"percent" : memory.percent
	}



# tells us the web route to trigger the functions
@app.route('/')

#create a function that returns a message
def index():

	storage_info = get_storage_info()
	cpu_info = get_cpu_info()
	memory_info = get_memory_info()


	return render_template('index.html', storage = storage_info, cpu = cpu_info, memory = memory_info)

#if statement checks if the __name__ has been made = __main__ as it
#should become this as it is a placeholder for the script name
if __name__ == '__main__':
	#app.run starts the app, host 0.0.0.0 makes the app accessible from any
	#network interface not just the loopback, port 5000 is the port where
	#the app is run it is usually this by default, debug allows for messages
	#and auto reloads while being edited
	app.run(host='', port=5000, debug=True)


