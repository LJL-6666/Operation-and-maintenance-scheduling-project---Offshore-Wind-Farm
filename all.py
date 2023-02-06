from flask import Flask, jsonify, request
from O_S_model import one2seven_model
from model import SupportOrgModel
import LCModel_V3
from LCModel_V3 import LifeCycleModel

app = Flask(__name__)


@app.route('/getcoordinates', methods=['POST'])
def hello_world1():
    params = request.json if request.method == "POST" else request.args
    if params:
        dataset = params
        print (dataset)
        return_data = one2seven_model(dataset)
        print("************")
        print(return_data)
        return return_data
    return jsonify({"code": 400, "msg": "No data received"})


@app.route('/getcoordinatestwo', methods=['POST'])
def hello_world2():
    params = request.json if request.method == "POST" else request.args
    if params:
        dataset = params
        Model2 = LifeCycleModel(dataset)
        outjson = Model2.model_optimize()
        print("************")
        print(outjson)
        return outjson
    return jsonify({"code": 400, "msg": "No data received"})


@app.route('/getcoordinatesthree', methods=['POST'])
def hello_world3():
    params = request.json if request.method == "POST" else request.args
    print(params)
    if params:
        dataset = params
        print (dataset)
        Model = SupportOrgModel(dataset)
        return_data1 = Model.analyze()
        print("************")
        print(return_data1)
        return return_data1
    return jsonify({"code": 400, "msg": "No data received"})

if __name__ == '__main__':
    app.run("0.0.0.0", 8083, True)