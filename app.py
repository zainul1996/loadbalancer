# app.py
import json
from flask import Flask, request, jsonify
import boto3
from itertools import cycle
from threading import Thread, Timer
import time
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Dictionary to store number of task
taskManager = {}

session = boto3.Session(
    aws_access_key_id="AKIAU45RG4DG3KV6R5LJ",
    aws_secret_access_key="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",
    region_name='us-east-2'
)

# Connect to EC2
ec2 = session.resource('ec2')

# Create CloudWatch client
cloudwatch = session.client('cloudwatch')

list_ip = []
pool = cycle(list_ip)


def get_cpu_utilization(id):
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': id
            }
        ],
        MetricName='CPUUtilization',
        StartTime=datetime.utcnow() - timedelta(minutes=10),
        EndTime=datetime.utcnow(),
        Period=60,
        Statistics=[
            'Maximum'
        ],
        Unit='Percent'
    )
    response['Datapoints']
    if not response['Datapoints'] or response['Datapoints'][0]['Maximum'] > 0.5:
        return 0
    return response['Datapoints'][0]['Maximum']


def round_robin():
    while True:
        instances = ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        instance_list = [instance for instance in instances]

        # if new instance have been added 5 mins ago
        # add update circular list
        if len(list_ip) is not len(instance_list):
            list_ip.clear()
            for instance in instances:
                list_ip.append(instance.public_ip_address)
            pool = cycle(list_ip)
            print(list_ip)

        max_cpu_utilization = 0
        last_instance_id = ""

        for instance in instances:
            max_cpu_utilization = get_cpu_utilization(
                instance.instance_id)/0.5*100
            last_instance_id = instance.instance_id

        print("max", max_cpu_utilization)
        # if above threshold
        if max_cpu_utilization > 70:
            url = "https://khmwesl75f.execute-api.us-east-2.amazonaws.com/default/addInstance"
            # scale up
            response = requests.request("POST", url)
            print("added new instance")

        # if below threshold
        elif max_cpu_utilization < 40:
            # if length of list_ip > 2
            if(len(list_ip) > 2):
                # remove last item from list
                del list_ip[-1]
                # reinitialize circular list
                pool = cycle(list_ip)
                # scale down
                url = "https://y7nwunkj3a.execute-api.us-east-2.amazonaws.com/default/deleteInstance"

                payload = json.dumps({
                    "instanceId": last_instance_id
                })
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request(
                    "POST", url, headers=headers, data=payload)

                print("removed instance ", last_instance_id)

        time.sleep(600)


t = Thread(target=round_robin)
t.daemon = True
t.start()

def next_instance():
    return next(pool)

@app.route("/getUser", methods=["POST"])
def getUser():
    next_server_ip = next_instance()
    url = "http://{0}/getUser".format(next_server_ip)
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", url, headers=headers, data=request.json)
    return response.text


@app.route("/login", methods=["POST"])
def login():
    next_server_ip = next_instance()
    url = "http://{0}/login".format(next_server_ip)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request(
        "POST", url, headers=headers, data=request.json)
    print(next_server_ip, response.text)
    return response.text


@app.route("/createUser", methods=["POST"])
def logcreateUserin():
    next_server_ip = next_instance()
    url = "http://{0}/createUser".format(next_server_ip)
    headers = {
        'Content-Type': 'application/json'
    }
    print(request.json)
    response = requests.request(
        "POST", url, headers=headers, data=request.json)
    print(response.text)
    return response.text


@app.route("/getUserPrefs", methods=["POST"])
def getUserPrefs():
    url = "http://13.59.12.240/getUserPrefs"

    payload = json.dumps({
        "userid": 298926916172251650
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


@app.route("/insertUserPrefs", methods=["POST"])
def insertUserPrefs():
    next_server_ip = next_instance()
    url = "http://{0}/insertUserPrefs".format(next_server_ip)
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", url, headers=headers, data=request.json)
    return response.text


if __name__ == "__main__":
    # Threaded option to enable multiple instances for multiple user access support
    app.run(debug=False, threaded=True, port=5000)
