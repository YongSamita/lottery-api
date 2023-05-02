from flask import Flask, make_response, request, jsonify
from itertools import combinations, permutations
from pymongo import MongoClient
import pymongo
from util.lottery import handleCreateCupleTod, handleCreateLoyPae, handleCreateNineteen, handleCreateThreeSixSwitch, handleCreateYums
from bson import ObjectId
from flask_cors import CORS
from datetime import datetime
from fpdf import FPDF
from util.report import handleGetLimitReport, handleGetPipelineReport, handleMappingResponseData

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
            req['createdAt'] = datetime.now()
            result.append(req)
        lotteryDB.insert_many(result)
        for document in result:
            document['_id'] = str(document['_id'])
            document['id'] = str(document['_id'])
            del document['createdAt']

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
            "threeTopPrice": req['threeTopPrice'],
            "threeTopPercent": req['threeTopPercent'],
            "threeTodPrice": req['threeTodPrice'],
            "threeTodPercent": req['threeTodPercent'],
            "threeButtomPrice": req['threeButtomPrice'],
            "threeButtomPercent": req['threeButtomPercent'],
            "twoTopPrice": req['twoTopPrice'],
            "twoTopPercent": req['twoTopPercent'],
            "twoButtomPrice": req['twoButtomPrice'],
            "twoButtomPercent": req['twoButtomPercent'],
            "oneTopPrice": req['oneTopPrice'],
            "oneTopPercent": req['oneTopPercent'],
            "oneButtomPrice": req['oneButtomPrice'],
            "oneButtomPercent": req['oneButtomPercent'],
            "coupleTodPrice": req['coupleTodPrice'],
            "coupleTodPercent": req['coupleTodPercent'],
            "loypaePrice": req['loypaePrice'],
            "loypaePercent": req['loypaePercent'],
            "yumPrice": req['yumPrice'],
            "yumPercent": req['yumPercent']
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
                "$set": {'customerName': req['customerName'], 'customerID': req['customerID'], 'threeTopPrice': req['threeTopPrice'],
                         'threeTopPercent': req['threeTopPercent'], 'threeTodPrice': req['threeTodPrice'], 'threeTodPercent': req['threeTodPercent'],
                         'threeButtomPrice': req['threeButtomPrice'], 'threeButtomPercent': req['threeButtomPercent'],
                         'twoTopPrice': req['twoTopPrice'], 'twoTopPercent': req['twoTopPercent'], 'twoButtomPrice': req['twoButtomPrice'],
                         'twoButtomPercent': req['twoButtomPercent'], 'oneTopPrice': req['oneTopPrice'], 'oneTopPercent': req['oneTopPercent'],
                         'oneButtomPrice': req['oneButtomPrice'], 'oneButtomPercent': req['oneButtomPercent'], 'coupleTodPrice': req['coupleTodPrice'],
                         'coupleTodPercent': req['coupleTodPercent'], 'loypaePrice': req['loypaePrice'], 'loypaePercent': req['loypaePercent'],
                         'yumPrice': req['yumPrice'], 'yumPercent': req['yumPercent'],
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
        print('/api/create-result-lottery req:', req)
        data = {}
        data = {
            "threeTop": req['threeTop'],
            "threeButtom_1": req['threeButtom_1'],
            "threeButtom_2": req['threeButtom_2'],
            "threeButtom_3": req['threeButtom_3'],
            "threeButtom_4": req['threeButtom_4'],
            "twoTop": req['twoTop'],
            "twoButtom": req['twoButtom']
        }
        document = list(result_lottery_DB.find({}))
        if (len(document) > 0):
            newvalues = {
                "$set": data
            }
            result_lottery_DB.update_one(
                {'_id': ObjectId(document[0]['_id'])}, newvalues)
        else:
            result_lottery_DB.insert_one(data)
        resp = jsonify(
            {"data": 'create upsert result lottery success', "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@app.route('/api/get-result-lottery', methods=['GET'])
def get_result_lottery():
    try:
        result = list(result_lottery_DB.find({}))
        for document in result:
            del document['_id']
        resp = jsonify({"data": result, "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@app.route('/api/get-date-lottery', methods=['GET'])
def get_date_lottery():
    try:
        pipeline = [
            {"$match": {"createdAt": {"$type": "date"}}},
            {"$project": {
                "_id": 0,
                "year": {"$year": "$createdAt"},
                "month": {"$month": "$createdAt"},
                "day": {"$dayOfMonth": "$createdAt"}
            }},
            {"$group": {
                "_id": {"year": "$year", "month": "$month", "day": "$day"},
            }},
            {"$project": {
                "_id": 0,
                "createdAt": {"$dateFromParts": {"year": "$_id.year", "month": "$_id.month", "day": "$_id.day"}}
            }},
            {"$sort": {"createdAt": -1}}
        ]
        result = list(lotteryDB.aggregate(pipeline))
        resp = jsonify({"data": result, "status": 200})
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
        dateLottery = request.args.get('dateLottery')
        overLottery = request.args.get('overLottery')
        print('get-report req:', count, typeLotto,
              sortByLottery, overLottery, dateLottery)
        start_date = datetime.strptime(dateLottery, '%a, %d %b %Y %H:%M:%S %Z')
        end_date = start_date.replace(hour=23, minute=59, second=59)
        pipeline = handleGetPipelineReport(
            count, typeLotto, sortByLottery, start_date, end_date)
        resultLottery = list(lotteryDB.aggregate(pipeline))
        resultLimit = list(limitDB.find({}))
        resultMapping = handleMappingResponseData(
            count, typeLotto, overLottery, resultLottery, resultLimit)
        resp = jsonify({"data": resultMapping, "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@ app.route('/api/download-report', methods=['GET'])
def download_report():
    try:
        over_sum = 0
        sum_sum = 0
        count = request.args.get('count')
        typeLotto = request.args.get('type')
        sortByLottery = request.args.get('sortByLottery')
        dateLottery = request.args.get('dateLottery')
        overLottery = request.args.get('overLottery')
        print('get-report req:', count, typeLotto,
              sortByLottery, overLottery, dateLottery)
        start_date = datetime.strptime(dateLottery, '%a, %d %b %Y %H:%M:%S %Z')
        end_date = start_date.replace(hour=23, minute=59, second=59)
        pipeline = handleGetPipelineReport(
            count, typeLotto, sortByLottery, start_date, end_date)
        resultLottery = list(lotteryDB.aggregate(pipeline))
        resultLimit = list(limitDB.find({}))
        resultMapping = handleMappingResponseData(
            count, typeLotto, overLottery, resultLottery, resultLimit)
        limitReport = handleGetLimitReport(count, typeLotto, resultLimit)
        for lottery in resultMapping:
            over_sum += lottery["over"]
            sum_sum += lottery["sum"]
        thai_months = [
            None, 'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม',
            'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน',
            'ธันวาคม'
        ]
        thai_year_offset = 543
        thai_date_str = f"{start_date.day} {thai_months[start_date.month]} {start_date.year + thai_year_offset}"
        header = ['ตัวเลข', 'ยอดรวม', 'ยอดเกิน']
        pdf = FPDF()
        pdf.add_font('DB-Heavent', '', 'fonts/DB-Heavent.ttf', uni=True)
        page_count = 1
        if len(resultMapping) > 0:
            for i, doc in enumerate(resultMapping):
                if i == 0 or i % 15 == 0:
                    pdf.add_page()
                    pdf.set_font('DB-Heavent', '', 16)
                    pdf.set_xy(20, 20)
                    pdf.cell(60, 10, 'ค่าตั้งรับ')
                    pdf.cell(100, 10, thai_date_str)
                    pdf.cell(0, 10,
                             'แผ่นที่ ' + str(page_count))
                    pdf.ln()
                    pdf.set_x(20)
                    pdf.cell(65, 10, str(limitReport))
                    pdf.cell(60, 10, count+typeLotto)
                    page_count += 1
                    pdf.ln(20)
                    pdf.set_x(30)
                    for j in range(len(header)):
                        pdf.cell(50, 10, header[j], border=1)
                    pdf.ln()
                pdf.set_x(30)
                pdf.cell(50, 10, doc['lottery'], border=1)
                pdf.cell(50, 10, str(doc['sum']), border=1)
                pdf.cell(50, 10, str(
                    doc['over']), border=1)
                pdf.ln()
        else:
            pdf.add_page()
            pdf.set_font('DB-Heavent', '', 16)
            pdf.set_xy(20, 20)
            pdf.cell(60, 10, 'ค่าตั้งรับ')
            pdf.cell(100, 10, thai_date_str)
            pdf.cell(0, 10,
                     'แผ่นที่ ' + str(page_count))
            pdf.ln()
            pdf.set_x(20)
            pdf.cell(65, 10, str(limitReport))
            pdf.cell(60, 10, count+typeLotto)
            page_count += 1
            pdf.ln(20)
            pdf.set_x(30)
            for j in range(len(header)):
                pdf.cell(50, 10, header[j], border=1)
            pdf.ln()
        pdf.ln(10)
        pdf.set_x(30)
        pdf.cell(50, 10, 'รวมยอดรวม: '+str(sum_sum), ln=1)
        pdf.set_x(30)
        pdf.cell(50, 10, 'ยอดรับ: '+str(limitReport), ln=1)
        pdf.set_x(30)
        pdf.cell(50, 10, 'รวมยอดเกิน: '+str(over_sum), ln=1)
        pdf_content = pdf.output(dest='S').encode('latin-1')
        resp = make_response(pdf_content)
        resp.headers['Content-Type'] = 'application/pdf'
        resp.headers['Content-Disposition'] = 'attachment; filename=report.pdf'

    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


if __name__ == '__main__':
    app.run(debug=True)
