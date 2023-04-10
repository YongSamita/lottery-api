from flask import Flask, request, jsonify
from itertools import combinations, permutations
from pymongo import MongoClient
app = Flask(__name__)


# กำหนดค่าเชื่อมต่อ database MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
collection = db['mycollection']


# รับinput
@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    # insert data เข้า collection
    collection.insert_many(data)
    response = {'status': 'success'}
    return jsonify(response)


@app.route('/api/lottery/total', methods=['GET'])
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

    result = collection.aggregate(pipeline)

    # นำผลลัพธ์มาเก็บใน list ของ dict
    output = []
    for doc in result:
        output.append(doc)

    return jsonify(output)


# ลอยแพ
@app.route('/combinations', methods=['POST'])
def get_combinations():
    data = request.get_json()['name']
    if len(data) != 5:
        return jsonify({'error': 'Invalid number of parameters.'}), 400
    result = list(combinations(data, 3))
    result = set(result)
    unique_result = list(set(result))  # select only unique values
    unique_result.sort()
    return jsonify({'combinations': unique_result})


# ยำ(มั้ง)
@app.route('/api/permutations', methods=['POST'])
def get_permutations():
    data = request.get_json()['name']
    if len(data) != 5:
        return jsonify({'error': 'Invalid number of parameters.'}), 400
    result = []
    for perm in permutations(data, 3):
        swapped_perm = (perm[2], perm[1], perm[0])
        result.append(swapped_perm)
    result = set(result)
    unique_result = list(set(result))  # select only unique values
    unique_result.sort()
    return jsonify({'permutations': unique_result})


# 19ประตู
@app.route('/api/get_two_digits', methods=['POST'])
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
@app.route('/permute', methods=['POST'])
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
@app.route('/api/get_three_digits', methods=['POST'])
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
