import json
import webbrowser
#imports the flask class from the flask module
from flask import Flask, render_template, jsonify, request

#import the shutil module
import shutil
import psutil

import threading
import time
import sqlite3
import re
import ast

#create an instance of the class __name__ is a
#shortcut to find flask resources
app = Flask(__name__)



def create_database():
    conn = sqlite3.connect("snapshot_storage.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snapshotinfo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        storageTotal REAL NOT NULL,
        storageUsed	REAL NOT NULL,
        storageRemaining REAL NOT NULL,
        cpuTotal REAL NOT NULL,
        cpuPerCore TEXT NOT NULL,
        memoryTotal REAL NOT NULL,
        memoryUsed REAL NOT NULL,
        memoryRemaining REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


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
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_usage_per_core = psutil.cpu_percent(interval=1, percpu=True)
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


latest_memory_data = {}


def get_memory_info():
    global latest_memory_data
    while True:
        memory = psutil.virtual_memory()

        latest_memory_data ={
        "total" : round((memory.total / (1024**3)),2),
        "avalible" : round((memory.available / (1024 ** 3)),2),
        "used" : round((memory.used / (1024 ** 3)),2),
        "percent" : memory.percent
        }
        time.sleep(1)


@app.route("/run_script", methods=["POST"])
def run_script():
    try:




        data = request.get_json()
        if not data:
            return jsonify({"error": "no json data received"}), 400

        returned_storage = data["key1"]
        returned_free_storage = data["key2"]
        returned_used_storage = data["key3"]
        returned_cpu_usage = float(data["key4"])
        returned_cpu_per_core = json.loads(data["key5"])
        returned_memory = data["key6"]
        returned_free_memory = float(data["key7"])
        returned_used_memory = float(data["key8"])

        values = (returned_storage, returned_used_storage,returned_free_storage,
                  returned_cpu_usage, str(returned_cpu_per_core), returned_memory,
                  returned_used_memory, returned_free_memory)

        conn = sqlite3.connect("snapshot_storage.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO snapshotinfo (
            storageTotal,
            storageUsed,
            storageRemaining,
            cpuTotal,
            cpuPerCore,
            memoryTotal,
            memoryUsed,
            memoryRemaining)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        
        
        ''', values)

        cursor.execute("SELECT COUNT(*) FROM snapshotinfo")
        row_count = cursor.fetchone()[0]

        if row_count > 10:
            excess_rows = row_count - 10
            cursor.execute('''
                    DELETE FROM snapshotinfo
                    WHERE id IN (
                        SELECT id FROM snapshotinfo 
                        ORDER BY id ASC 
                        LIMIT ?
                    )
                ''', (excess_rows,))


        cursor.execute("SELECT * FROM snapshotinfo")
        rows = cursor.fetchall()
        print("Contents of snapshotinfo table:")
        for row in rows:
            print(row)

        conn.commit()
        conn.close()


        print(returned_storage, returned_free_storage, returned_used_storage,returned_cpu_usage, returned_cpu_per_core, returned_memory, returned_free_memory, returned_used_memory)

        return jsonify({"message": "Data received successfully!", "total storage": returned_storage,"used storage": returned_used_storage, "remaining storage": returned_free_storage, "cpu usage": returned_cpu_usage, "cpu usage per core": returned_cpu_per_core})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/row_count')
def get_row_count():
    try:
        # Connect to the database
        conn = sqlite3.connect("snapshot_storage.db")
        cursor = conn.cursor()

        # Get the row count from the snapshotinfo table
        cursor.execute("SELECT COUNT(*) FROM snapshotinfo")
        row_count = cursor.fetchone()[0]

        conn.close()

        # Return the row count as JSON
        return jsonify({"row_count": row_count})

    except Exception as e:
        # In case of an error, send a JSON error message
        return jsonify({"error": str(e)}), 500




def option_data():
    try:
        data = request.get_json(force=True)  # Force parsing even without the correct content-type header
    except Exception as e:
        return {"error": f"Invalid JSON format: {str(e)}"}

    selected_option = re.sub(r'[^0-9]', '', data.get('key9', ''))
    global value
    value = int(selected_option)
    yup = True
    print(f"Selected Option: {value}")




@app.route('/option_data', methods=['POST'])
def work():
    option_data()
    webbrowser.open("http://127.0.0.1:5000/snapshot")



def get_db_data():
    conn = sqlite3.connect("snapshot_storage.db")
    cursor = conn.cursor()

    row_position = value

    cursor.execute(f"""
        SELECT storageTotal, storageUsed, storageRemaining,
        cpuTotal, cpuPerCore, memoryTotal, memoryUsed, memoryRemaining
        FROM snapshotinfo
        ORDER BY rowid DESC
        LIMIT 1 OFFSET ?
        """, (row_position - 1,))

    row = cursor.fetchone()

    if row:
        storageTotal, storageUsed, storageRemaining, cpuTotal, cpuPerCore_raw, memoryTotal, memoryUsed, memoryRemaining = row


        if isinstance(cpuPerCore_raw, float):
            cpuPerCore = [cpuPerCore_raw]
        elif isinstance(cpuPerCore_raw, str):
            if cpuPerCore_raw.startswith("[") and cpuPerCore_raw.endswith("]"):
                cpuPerCore = ast.literal_eval(cpuPerCore_raw)  # Convert to list
            else:
                cpuPerCore = [float(x) for x in cpuPerCore_raw.split(",")]  # Convert comma-separated values



        print("heres the stats:", storageTotal,
          storageUsed, storageRemaining, cpuTotal,
          cpuPerCore, memoryTotal, memoryUsed, memoryRemaining)


    conn.close()
    return {
        "storageTotal" : storageTotal,
        "storageUsed" : storageUsed,
        "storageRemaining" : storageRemaining,
        "cpuTotal" : cpuTotal,
        "cpuPerCore" : cpuPerCore,
        "memoryTotal" : memoryTotal,
        "memoryUsed" : memoryUsed,
        "memoryRemaining" : memoryRemaining
    }
@app.route('/snapshot')
def work2():
    data = get_db_data()
    return render_template('result.html', data= data)





# tells us the web route to trigger the functions
@app.route('/')

#create a function that returns a message
def index():

    create_database()
    storage_info = get_storage_info()
    cpu_info = get_cpu_info()

    conn = sqlite3.connect("snapshot_storage.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM snapshotinfo")
    row_count = cursor.fetchone()[0]
    conn.close()


    return render_template('index.html', storage = storage_info, cpu = cpu_info, memory = latest_memory_data, row_count=row_count)

thread = threading.Thread(target=get_memory_info)
thread.daemon = True
thread.start()

def open_browser():
    webbrowser.open("http://127.0.0.1:5000/")

#if statement checks if the __name__ has been made = __main__ as it
#should become this as it is a placeholder for the script name
if __name__ == '__main__':
    threading.Timer(1.0, open_browser).start()
    #app.run starts the app, host 0.0.0.0 makes the app accessible from any
    #network interface not just the loopback, port 5000 is the port where
    #the app is run it is usually this by default, debug allows for messages
    #and auto reloads while being edited
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader = False)



