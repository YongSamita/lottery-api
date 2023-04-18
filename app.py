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
customerDB = db['customer']
limitDB = db['limit']
result_lottery_DB = db['result_lottery']


@app.route('/api/result-lottery', methods=['GET'])
def result_lottery():
    # ใช้ aggregation pipeline เพื่อหาผลรวมของ top, tod และ bottom ของเลขหวยเดียวกัน
    result = lotteryDB.aggregate([
        {"$group": {
            "_id": "$lottery_number",
            "total_top": {"$sum": {"$toInt": "$top"}},
            "total_tod": {"$sum": {"$toInt": "$tod"}},
            "total_bottom": {"$sum": {"$sum": {"$map": {"input": "$bottom", "in": {"$toInt": "$$this"}}}}}
        }}
    ])

    # พิมพ์ผลลัพธ์
    for doc in result:
        print(doc)

    return result


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
            req['createdAt'] = datetime.datetime.now()
            result.append(req)
        lotteryDB.insert_many(result)
        for document in result:
            document['createdAt'] = document['createdAt'].strftime(
                '%Y-%m-%d %H:%M:%S.%f')
            document['_id'] = str(document['_id'])
            document['id'] = str(document['_id'])

        resp = jsonify({"data": result, "status": 200})
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
            del document['_id']
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


@app.route('/api/edit-lottery', methods=['POST'])
def edit_lottery():
    try:
        req = request.get_json()
        print('/api/edit-lottery req:', req)
        filter = {'_id': ObjectId(req['id'])}
        newvalues = {
            "$set": {'customerName': req['customerName'], 'top': req['top'], 'tod': req['tod'], 'buttom': req['buttom'], 'lottery': req['lottery'], 'type': req['type']}}
        lotteryDB.update_one(filter, newvalues)
        resp = jsonify({"data": req, "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@ app.route('/api/delete-lottery-all', methods=['POST'])
def delete_lottery_all():
    lotteryDB.delete_many({})
    return jsonify({"status": "success"})


@app.route('/api/get-list-customer', methods=['GET'])
def get_list_customer():
    try:
        result = list(customerDB.find({}).sort(
            'customerID', pymongo.ASCENDING))
        for document in result:
            document['id'] = str(document['_id'])
            del document['_id']
        resp = jsonify({"data": result, "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@app.route('/api/create-upsert-customer', methods=['POST'])
def create_customer():
    try:
        req = request.get_json()
        result = []
        print('/api/add-custommer req:', req)
        document = list(customerDB.find({"customerID": req['customerID']}))
        data = {}
        data = {
            "customerName": req['customerName'],
            "customerID": req['customerID'],
            "createdBy": req['createdBy'],
            "createdAt": datetime.datetime.now(),
            "threeTop": {
                'threeTopPrice':  req['threeTopPrice'],
                'threeTopPercent':  req['threeTopPercent']
            },
            "threeTod": {
                'threeTodPrice':  req['threeTodPrice'],
                'threeTodPercent':  req['threeTodPercent']
            },
            "threeButtom": {
                'threeButtomPrice':  req['threeButtomPrice'],
                'threeButtomPercent':  req['threeButtomPercent']
            },
            "twoTop": {
                'twoTopPrice':  req['twoTopPrice'],
                'twoTopPercent':  req['twoTopPercent']
            },
            "twoButtom": {
                'twoButtomPrice':  req['twoButtomPrice'],
                'twoButtomPercent':  req['twoButtomPercent']
            },
            "oneTop": {
                'oneTopPrice':  req['oneTopPrice'],
                'oneTopPercent':  req['oneTopPercent']
            },
            "oneButtom": {
                'oneButtomPrice':  req['oneButtomPrice'],
                'oneButtomPercent':  req['oneButtomPercent']
            },
            "coupleTod": {
                'coupleTodPrice':  req['coupleTodPrice'],
                'coupleTodPercent':  req['coupleTodPercent']
            },
            "loypae": {
                'loypaePrice':  req['loypaePrice'],
                'loypaePercent':  req['loypaePercent']
            },
            "yum": {
                'yumPrice':  req['yumPrice'],
                'yumPercent':  req['yumPercent']
            },
        }
        if (len(document) == 0):
            result.append(data)
            customerDB.insert_many(result)
            for document in result:
                document['id'] = str(document['_id'])
                del document['_id']
            resp = jsonify({"data": result, "status": 200})
        else:
            filter = {}
            filter = {'customerID': req['customerID']}
            newvalues = {
                "$set": {'customerName': req['customerName'], 'customerID': req['customerID'],
                         'threeTop': {'threeTopPrice': req['threeTopPrice'], 'threeTopPercent': req['threeTopPercent']},
                         'threeTod': {'threeTodPrice': req['threeTodPrice'], 'threeTodPercent': req['threeTodPercent']},
                         'threeButtom': {'threeButtomPrice': req['threeButtomPrice'], 'threeButtomPercent': req['threeButtomPercent']},
                         'twoTop': {'twoTopPrice': req['twoTopPrice'], 'twoTopPercent': req['twoTopPercent']},
                         'twoButtom': {'twoButtomPrice': req['twoButtomPrice'], 'twoButtomPercent': req['twoButtomPercent']},
                         'oneTop': {'oneTopPrice': req['oneTopPrice'], 'oneTopPercent': req['oneTopPercent']},
                         'oneButtom': {'oneButtomPrice': req['oneButtomPrice'], 'oneButtomPercent': req['oneButtomPercent']},
                         'coupleTod': {'coupleTodPrice': req['coupleTodPrice'], 'coupleTodPercent': req['coupleTodPercent']},
                         'loypae': {'loypaePrice': req['loypaePrice'], 'loypaePercent': req['loypaePercent']},
                         'yum': {'yumPrice': req['yumPrice'], 'yumPercent': req['yumPercent']},
                         }}
            customerDB.update_one(filter, newvalues)
            resp = jsonify({"data": 'update success', "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@app.route('/api/delete-customer', methods=['POST'])
def delete_customer():
    try:
        req = request.get_json()
        print('/api/delete-customer req:', req)
        for item in req['id']:
            customerDB.delete_one({'_id': ObjectId(item)})
        resp = jsonify({"data": 'delete success', "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@ app.route('/api/customer/deleteAll', methods=['POST'])
def deleteAll():
    customerDB.delete_many({})
    return jsonify({"status": "success"})


@app.route('/api/create-limit-lottery', methods=['POST'])
def create_limit_lottery():
    try:
        req = request.get_json()
        print('/api/create-limit-lottery req:', req)
        data = {}
        data = {
            "threeTop": req['threeTop'],
            "threeTod": req['threeTod'],
            "threeButtom": req['threeButtom'],
            "twoTop": req['twoTop'],
            "twoButtom": req['twoButtom']
        }
        document = list(limitDB.find({}))
        if (len(document) > 0):
            newvalues = {
                "$set": data
            }
            limitDB.update_one(
                {'_id': ObjectId(document[0]['_id'])}, newvalues)
        else:
            limitDB.insert_one(data)
        resp = jsonify(
            {"data": 'create upsert limit lottery success', "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@app.route('/api/get-limit', methods=['GET'])
def get_limit():
    try:
        result = list(limitDB.find({}))
        for document in result:
            del document['_id']
        resp = jsonify({"data": result, "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@app.route('/api/create-result-lottery', methods=['POST'])
def create_result_lottery():
    try:
        req = request.get_json()
        result = []
        print('/api/create-result-lottery req:', req)
        data = {}
        data = {
            "threetop": req['threetop'],
            "threebuttom_1": req['threebuttom'],
            "threebuttom_2": req['threebuttom'],
            "threebuttom_3": req['threebuttom'],
            "threebuttom_4": req['threebuttom'],
            "twotop": req['twotop'],
            "twobuttom": req['twobuttom']
        }
        result.append(data)
        insert_result = result_lottery_DB.insert_many(result)
        inserted_ids = [str(id) for id in insert_result.inserted_ids]
        resp = jsonify({"data": inserted_ids, "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@ app.route('/api/get-report', methods=['GET'])
def get_lottery_report():
    try:
        count = request.args.get('count')
        typeLotto = request.args.get('type')
        sortByLottery = request.args.get('sortByLottery')
        pipeline = []
        result = []
        if count == 'วิ่ง':
            pipeline.append(
                {'$match': {
                    'lottery': {'$regex': '^.{1}$'}
                }}
            )
        elif count == '2 ตัว':
            pipeline.append(
                {'$match': {
                    'lottery': {'$regex': '^.{2}$'}
                }}
            )
        elif count == '3 ตัว':
            pipeline.append(
                {'$match': {
                    'lottery': {'$regex': '^.{3}$'}
                }}
            )

        pipeline.append(
            {
                '$group': {
                    '_id': '$lottery',
                    'top': {'$sum': '$top'},
                    'tod': {'$sum': '$tod'},
                    'buttom': {'$sum': '$buttom'},
                }
            }
        )
        if (sortByLottery):
            pipeline.append({
                '$sort': {
                    '_id': -1
                }
            })
        else:
            if (typeLotto == 'บน'):
                pipeline.append({
                    '$sort': {
                        'top': -1
                    }
                })
            elif (typeLotto == 'โต๊ด'):
                pipeline.append({
                    '$sort': {
                        'tod': -1
                    }
                })
            elif (typeLotto == 'ล่าง'):
                pipeline.append({
                    '$sort': {
                        'buttom': -1
                    }
                })
        resultLottery = list(lotteryDB.aggregate(pipeline))
        resultLimit = list(limitDB.find({}))
        if (len(resultLimit) > 0):
            for document in resultLottery:
                if (count == '3 ตัว'):
                    if (typeLotto == 'บน'):
                        over = document['top'] - resultLimit[0]['threeTop']
                        document['sum'] = document['top']
                        if (over <= 0):
                            document['over'] = 0
                        else:
                            document['over'] = over
                    elif (typeLotto == 'โต๊ด'):
                        over = document['tod'] - resultLimit[0]['threeTod']
                        document['sum'] = document['tod']
                        if (over <= 0):
                            document['over'] = 0
                        else:
                            document['over'] = over
                    elif (typeLotto == 'ล่าง'):
                        over = document['buttom'] - \
                            resultLimit[0]['threeButtom']
                        document['sum'] = document['buttom']
                        if (over <= 0):
                            document['over'] = 0
                        else:
                            document['over'] = over
                if (count == '2 ตัว'):
                    if (typeLotto == 'บน'):
                        over = document['top'] - resultLimit[0]['twoTop']
                        document['sum'] = document['top']
                        if (over <= 0):
                            document['over'] = 0
                        else:
                            document['over'] = over
                    elif (typeLotto == 'ล่าง'):
                        over = document['buttom'] - resultLimit[0]['twoButtom']
                        document['sum'] = document['buttom']
                        if (over <= 0):
                            document['over'] = 0
                        else:
                            document['over'] = over
                if (count == 'วิ่ง'):
                    if (typeLotto == 'บน'):
                        document['sum'] = document['top']
                        document['over'] = 0
                    elif (typeLotto == 'ล่าง'):
                        document['sum'] = document['buttom']
                        document['over'] = 0
                document['id'] = document['_id']
                document['lottery'] = document['_id']
                del document['buttom']
                del document['top']
                del document['tod']
                del document['_id']
                result.append(document)
        else:
            for document in resultLottery:
                if (count == '3 ตัว'):
                    if (typeLotto == 'บน'):
                        document['sum'] = document['top']
                        document['over'] = 0
                    elif (typeLotto == 'โต๊ด'):
                        document['sum'] = document['tod']
                        document['over'] = 0
                    elif (typeLotto == 'ล่าง'):
                        document['sum'] = document['buttom']
                        document['over'] = 0
                if (count == '2 ตัว'):
                    if (typeLotto == 'บน'):
                        document['sum'] = document['top']
                        document['over'] = 0
                    elif (typeLotto == 'ล่าง'):
                        document['sum'] = document['buttom']
                        document['over'] = 0
                if (count == 'วิ่ง'):
                    if (typeLotto == 'บน'):
                        document['sum'] = document['top']
                        document['over'] = 0
                    elif (typeLotto == 'ล่าง'):
                        document['sum'] = document['buttom']
                        document['over'] = 0
                document['id'] = document['_id']
                document['lottery'] = document['_id']
                del document['buttom']
                del document['top']
                del document['tod']
                del document['_id']
                result.append(document)
        resp = jsonify({"data": result, "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


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


#  pipeline = [
#             {'$match': {
#                 'lottery': {'$regex': '^.{3}$'}
#             }},
#             {
#                 '$group': {
#                     '_id': '$lottery',
#                     'top': {'$sum': '$top'},
#                     'tod': {'$sum': '$tod'},
#                     'buttom': {'$sum': '$buttom'},
#                 }},

#             {

#                 '$sort': {
#                     '_id': -1
#                 }
#             },

#             {

#                 '$project': {
#                     'lottery': '$_id',
#                     '_id': 0,
#                     'top': 1,
#                     'tod': 1,
#                     'buttom': 1,
#                 }
#             }
#         ]
