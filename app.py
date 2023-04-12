import datetime
import json
from flask import Flask, request, jsonify, Response
from itertools import combinations, permutations
from pymongo import MongoClient
import pymongo
from util.lottery import handleCreateCupleTod, handleCreateLoyPae, handleCreateNineteen, handleCreateThreeSixSwitch, handleCreateYums
from bson import ObjectId
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

client = MongoClient(
    'mongodb+srv://komsark01:promix02.@lotto.atl56bl.mongodb.net/?retryWrites=true&w=majority')
db = client['lotto']
lotteryDB = db['lottery']


@app.route('/api/create-lottery', methods=['POST'])
def create_lottery():
    try:
        req = request.get_json()
        print('/api/create-lottery req:', req)
        result = []
        if req['type'] == '3 กลับ':
            result = handleCreateThreeSixSwitch(req)
        elif req['type'] == '19 ประตู':
            result = handleCreateNineteen(req)
        elif req['type'] == 'คู่โต๊ด':
            result = handleCreateCupleTod(req)
        elif req['type'] == 'ลอยแพ':
            result = handleCreateLoyPae(req)
        elif req['type'] == 'ยำ':
            result = handleCreateYums(req)
        else:
            result.append(req)
        lotteryDB.insert_many(result)
        resp = jsonify({"data": 'create success', "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@app.route('/api/get-lottery', methods=['GET'])
def get_lottery():
    try:
        req = request.args.get('createdBy')
        print('/api/get-lottery req:', req)
        projection = {'buttom': 1,
                      'customerName': 1, 'lottery': 1, 'tod': 1, 'top': 1, 'type': 1}
        result = list(lotteryDB.find({"createdBy": req}, projection).sort(
            'createdAt', pymongo.ASCENDING))
        for document in result:
            document['id'] = str(document['_id'])
        resp = jsonify({"data": result, "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@app.route('/api/delete-lottery', methods=['POST'])
def delete_lottery():
    try:
        req = request.get_json()
        print('/api/delete-lottery req:', req)
        for item in req['id']:
            lotteryDB.delete_one({'_id': ObjectId(item)})
        resp = jsonify({"data": 'delete success', "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@ app.route('/api/lottery/total', methods=['GET'])
def get_lottery_total():
    pipeline = [
        {
            # กำหนดเงื่อนไขการ query ใน collection
            '$match': {}
        },
        {
            # กำหนดเงื่อนไขการ groupby ด้วย lottery
            '$group': {
                '_id': '$lottery',
                'top': {'$sum': '$top'},
                'tod': {'$sum': '$tod'},
                'buttom': {'$sum': '$buttom'},
            }
        },
        {
            # กำหนดชื่อ column ใหม่สำหรับตัวแปร _id
            '$project': {
                'lottery': '$_id',
                '_id': 0,
                'top': 1,
                'tod': 1,
                'buttom': 1,
            }
        }
    ]

    result = lotteryDB.aggregate(pipeline)

    # นำผลลัพธ์มาเก็บใน list ของ dict
    output = []
    for doc in result:
        output.append(doc)

    return jsonify(output)


@ app.route('/api/lottery/deleteAll', methods=['POST'])
def deleteAll():
    lotteryDB.delete_many({})
    return jsonify({"status": "success"})


# ลอยแพ
@ app.route('/combinations', methods=['POST'])
def get_combinations():
    data = request.get_json()['name']
    result = list(combinations(data, 3))
    result = set(result)
    unique_result = list(set(result))  # select only unique values
    unique_result.sort()
    return jsonify({'combinations': unique_result})


# ยำ(มั้ง)
@ app.route('/api/permutations', methods=['POST'])
def get_permutations():
    data = request.get_json()['name']
    result = []
    for perm in permutations(data, 3):
        swapped_perm = (perm[2], perm[1], perm[0])
        result.append(swapped_perm)
    result = set(result)
    unique_result = list(set(result))  # select only unique values
    unique_result.sort()
    return jsonify({'permutations': unique_result})


# 19ประตู
@ app.route('/api/get_two_digits', methods=['POST'])
def get_two_digits():
    data = request.get_json()['name']
    print(data)
    two_digits = []
    for i in range(10):
        two_digit = str(i) + str(data[0])
        two_digits.append(two_digit)
        two_digit = str(data[0]) + str(i)
        two_digits.append(two_digit)
    two_digits = set(two_digits)
    unique_result = list(set(two_digits))  # select only unique values
    unique_result.sort()
    return jsonify({'two_digits': unique_result})


# 3กลับ/6กลับ
@ app.route('/permute', methods=['POST'])
def get_permute():
    data = request.get_json()['name']
    result = []
    for perm in permutations(data, 3):
        swapped_perm = (perm[0], perm[1], perm[2])
        result.append(swapped_perm)
    result = set(result)
    unique_result = list(set(result))  # select only unique values
    unique_result.sort()
    return jsonify({'permutations': unique_result})


# คู่โต๊ด
@ app.route('/api/get_three_digits', methods=['POST'])
def get_three_digits():
    data = request.get_json()['name']
    print(data)
    three_digits = []
    result = []
    for i in range(10):
        three_digit = str(i) + str(data[0]) + str(data[1])
        three_digits.append(three_digit)
    unique_result = list(set(three_digits))  # select only unique values
    unique_result.sort()
    return jsonify({'three_digits': unique_result})


if __name__ == '__main__':
    app.run(debug=True)
