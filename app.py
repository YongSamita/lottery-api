from flask import Flask, make_response, request, jsonify
from itertools import permutations
from pymongo import MongoClient
import pymongo
from util.lottery import handleCreateCupleTod, handleCreateLoyPae, handleCreateNineteen, handleCreateThreeSixSwitch, handleCreateYums
from bson import ObjectId
from flask_cors import CORS
from datetime import datetime, time, timedelta
from fpdf import FPDF
from util.report import handleGetLimitReport, handleGetPipelineReport, handleMappingResponseData
import pandas as pd
import numpy as np
import pytz


app = Flask(__name__)
CORS(app)


client = MongoClient(
    'mongodb+srv://komsark01:promix02.@lotto.atl56bl.mongodb.net/?retryWrites=true&w=majority')
db = client['lotto']
lotteryDB = db['lottery']
customerDB = db['customer']
limitDB = db['limit']
result_lottery_DB = db['result_lottery']
tz = pytz.timezone('Asia/Bangkok')


class ResultPDF(FPDF):
    def header(self):
        self.add_font('DB-Heavent', '', 'fonts/DB-Heavent.ttf', uni=True)
        self.set_font('DB-Heavent', '', 16)
        self.set_x(85)
        self.cell(100, 10, 'ใบสรุปยอดเงินลูกค้า')
        self.cell(0, 10, f'แผ่นที่ {self.page_no()}')
        self.ln()
        self.set_y(25)


class ReportPDF(FPDF):
    def header(self):
        self.add_font('DB-Heavent', '', 'fonts/DB-Heavent.ttf', uni=True)
        self.set_font('DB-Heavent', '', 16)
        self.set_x(185)
        self.cell(0, 10, f'แผ่นที่ {self.page_no()}')
        self.ln()
        self.set_y(25)


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
            req['createdAt'] = datetime.now(tz=tz)
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
        current_date = datetime.today()
        current_start_of_day = datetime.combine(current_date, time.max)
        past_date = current_date - timedelta(days=10)
        past_start_of_day = datetime.combine(past_date, time.min)
        projection = {'buttom': 1,
                      'customerName': 1, 'lottery': 1, 'tod': 1, 'top': 1, 'type': 1}
        result = list(lotteryDB.find({"createdBy": req,
                                      "createdAt": {"$gte": past_start_of_day, "$lt": current_start_of_day}}, projection).sort(
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


@app.route('/api/delete-data-by-date', methods=['POST'])
def delete_lottery_by_date():
    try:
        dateLottery = request.args.get('dateLottery')
        print('/api/delete-lottery-by-date req:', dateLottery)
        start_date = datetime.strptime(dateLottery, '%a, %d %b %Y %H:%M:%S %Z')
        end_date = start_date.replace(hour=23, minute=59, second=59)
        lotteryDB.delete_many(
            {"createdAt": {"$gte": start_date, "$lt": end_date}})
        result_lottery_DB.delete_many(
            {"createdAt": {"$gte": start_date, "$lt": end_date}})
        limitDB.delete_many(
            {"createdAt": {"$gte": start_date, "$lt": end_date}})
        resp = jsonify(
            {"data": 'delete lottery by date success', "status": 200})
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


@ app.route('/api/delete-customer-all', methods=['POST'])
def deleteAll():
    customerDB.delete_many({})
    return jsonify({"status": "success"})


@app.route('/api/create-limit-lottery', methods=['POST'])
def create_limit_lottery():
    try:
        req = request.get_json()
        print('/api/create-limit-lottery req:', req)
        now = datetime.now()
        start_date = datetime.combine(now.date(), time.min)
        end_date = datetime.combine(now.date(), time.max)
        data = {
            "threeTop": req['threeTop'],
            "threeTod": req['threeTod'],
            "threeButtom": req['threeButtom'],
            "twoTop": req['twoTop'],
            "twoButtom": req['twoButtom'],
            "createdAt": datetime.now(tz=tz)
        }
        document = list(limitDB.find(
            {"createdAt": {"$gte": start_date, "$lt": end_date}}))
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
        response = []
        result = list(limitDB.find({}).sort(
            'createdAt', pymongo.DESCENDING))
        if (len(result) > 0):
            response.append(result[0])
            for document in response:
                del document['_id']
            resp = jsonify({"data": response, "status": 200})
        else:
            resp = jsonify({"data": [], "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@app.route('/api/create-result-lottery', methods=['POST'])
def create_result_lottery():
    try:
        req = request.get_json()
        print('/api/create-result-lottery req:', req)
        now = datetime.now()
        start_date = datetime.combine(now.date(), time.min)
        end_date = datetime.combine(now.date(), time.max)
        data = {
            "threeTop": req['threeTop'],
            "threeButtom_1": req['threeButtom_1'],
            "threeButtom_2": req['threeButtom_2'],
            "threeButtom_3": req['threeButtom_3'],
            "threeButtom_4": req['threeButtom_4'],
            "twoTop": req['twoTop'],
            "twoButtom": req['twoButtom'],
            "createdAt": datetime.now(tz=tz)
        }
        document = list(result_lottery_DB.find(
            {"createdAt": {"$gte": start_date, "$lt": end_date}}))
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
        response = []
        result = list(result_lottery_DB.find({}).sort(
            'createdAt', pymongo.DESCENDING))
        if (len(result) > 0):
            response.append(result[0])
            for document in response:
                del document['_id']
            resp = jsonify({"data": response, "status": 200})
        else:
            resp = jsonify({"data": [], "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@app.route('/api/get-result-lottery-by-date', methods=['GET'])
def get_result_lottery_by_date():
    try:
        dateLottery = request.args.get('dateLottery')
        print('/api/get-result-lottery-by-date req:', dateLottery)
        start_date = datetime.strptime(dateLottery, '%a, %d %b %Y %H:%M:%S %Z')
        end_date = start_date.replace(hour=23, minute=59, second=59)
        result = list(result_lottery_DB.find(
            {"createdAt": {"$gte": start_date, "$lt": end_date}}))
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
        sum_sum = 0
        deduction = 0
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
        resultLimit = list(limitDB.find(
            {"createdAt": {"$gte": start_date, "$lt": end_date}}))
        if len(resultLimit) == 0:
            resultLimit = list(limitDB.find({}).sort(
                'createdAt', pymongo.DESCENDING))
        resultMapping = handleMappingResponseData(
            count, typeLotto, overLottery, resultLottery, resultLimit)
        limitReport = handleGetLimitReport(count, typeLotto, resultLimit)
        for lottery in resultMapping:
            sum_sum += lottery["sum"]
        deduction = sum_sum - (sum_sum*(35/100))
        resp = jsonify({"data": {'resultTable': resultMapping, 'summarize': {
                       'sum': sum_sum, 'limit': limitReport, 'deduction': deduction}}, "status": 200})
    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@ app.route('/api/download-report', methods=['GET'])
def download_report():
    try:
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
        resultLimit = list(limitDB.find(
            {"createdAt": {"$gte": start_date, "$lt": end_date}}))
        if len(resultLimit) == 0:
            resultLimit = list(limitDB.find({}).sort(
                'createdAt', pymongo.DESCENDING))
            data = {
                "threeTop": resultLimit[0]['threeTop'],
                "threeTod": resultLimit[0]['threeTod'],
                "threeButtom": resultLimit[0]['threeButtom'],
                "twoTop": resultLimit[0]['twoTop'],
                "twoButtom": resultLimit[0]['twoButtom'],
                "createdAt": datetime.now(tz=tz)
            }
            limitDB.insert_one(data)
        resultMapping = handleMappingResponseData(
            count, typeLotto, overLottery, resultLottery, resultLimit)
        limitReport = handleGetLimitReport(count, typeLotto, resultLimit)
        for lottery in resultMapping:
            sum_sum += lottery["sum"]
        thai_months = [
            None, 'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม',
            'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน',
            'ธันวาคม'
        ]
        thai_year_offset = 543
        thai_date_str = f"{start_date.day} {thai_months[start_date.month]} {start_date.year + thai_year_offset}"
        header = ['ตัวเลข', 'ยอดรวม', 'ยอดเกิน']
        pdf = ReportPDF()
        pdf.add_font('DB-Heavent', '', 'fonts/DB-Heavent.ttf', uni=True)
        pdf.set_font('DB-Heavent', '', 16)
        pdf.set_auto_page_break(auto=True, margin=15)
        if len(resultMapping) > 0:
            for i, doc in enumerate(resultMapping):
                if i == 0:
                    pdf.add_page()
                    pdf.set_font('DB-Heavent', '', 16)
                    pdf.set_xy(20, 10)
                    pdf.cell(60, 10, 'ค่าตั้งรับ')
                    pdf.cell(100, 10, thai_date_str)
                    pdf.ln()
                    pdf.set_x(20)
                    pdf.cell(65, 10, str(format(limitReport, ',')))
                    pdf.cell(60, 10, count+typeLotto)
                    pdf.ln(20)
                    pdf.set_x(30)
                    for j in range(len(header)):
                        pdf.cell(50, 10, header[j], border=1)
                    pdf.ln()
                pdf.set_x(30)
                pdf.cell(50, 10, doc['lottery'], border=1)
                pdf.cell(50, 10, str(format(doc['sum'], ',')), border=1)
                pdf.cell(50, 10, str(
                    format(doc['over'], ',')), border=1)
                pdf.ln()
        else:
            pdf.add_page()
            pdf.set_font('DB-Heavent', '', 16)
            pdf.set_xy(20, 10)
            pdf.cell(60, 10, 'ค่าตั้งรับ')
            pdf.cell(100, 10, thai_date_str)
            pdf.ln()
            pdf.set_x(20)
            pdf.cell(65, 10, str(format(limitReport, ',')))
            pdf.cell(60, 10, count+typeLotto)
            pdf.ln(20)
            pdf.set_x(30)
            for j in range(len(header)):
                pdf.cell(50, 10, header[j], border=1)
            pdf.ln()
        pdf.ln(10)
        pdf.set_x(30)
        pdf.cell(50, 10, 'รวมยอดรวม: '+str(format(sum_sum, ',')), ln=1)
        pdf.set_x(30)
        pdf.cell(50, 10, 'ยอดรับ: '+str(format(limitReport, ',')), ln=1)
        pdf.set_x(30)
        pdf.cell(50, 10, 'ยอดหัก 35%: ' +
                 str(format(sum_sum - (sum_sum*(35/100)), ',')), ln=1)
        pdf_content = pdf.output(dest='S').encode('latin-1')
        resp = make_response(pdf_content)
        resp.headers['Content-Type'] = 'application/pdf'
        resp.headers['Content-Disposition'] = 'attachment; filename=report.pdf'

    except Exception as e:
        print("The error is: ", e)
        resp = jsonify({"data": '', "status": 400})
    return resp


@ app.route('/api/download-result', methods=['GET'])
def download_result():
    try:
        dateLottery = request.args.get('dateLottery')
        print('/api/download-result req:', dateLottery)
        start_date = datetime.strptime(dateLottery, '%a, %d %b %Y %H:%M:%S %Z')
        end_date = start_date.replace(hour=23, minute=59, second=59)
        resultLottery = list(result_lottery_DB.find(
            {"createdAt": {"$gte": start_date, "$lt": end_date}}))

        resultLottery = pd.DataFrame(resultLottery)
        customer = list(customerDB.find().sort(
            "customerName", pymongo.ASCENDING))
        customer = pd.DataFrame(customer)
        lottery = list(lotteryDB.find(
            {"createdAt": {"$gte": start_date, "$lt": end_date}}))
        lottery = pd.DataFrame(lottery)

        mergeLot = pd.merge(lottery, customer, on='customerName', how='left')
        mergeLot['WinthreetopP'] = mergeLot['top']*mergeLot['threeTopPrice']
        mergeLot['WinthreetodP'] = mergeLot['tod']*mergeLot['threeTodPrice']
        mergeLot['WinthreebuttomP'] = mergeLot['buttom'] * \
            mergeLot['threeButtomPrice']
        mergeLot['WintwotopP'] = mergeLot['top']*mergeLot['twoTopPrice']
        mergeLot['WintwobuttomP'] = mergeLot['top']*mergeLot['twoTopPrice']
        mergeLot['WinonetopP'] = mergeLot['top']*mergeLot['oneTopPrice']
        mergeLot['WinonebuttomP'] = mergeLot['top']*mergeLot['oneTopPrice']
        mergeLot['WincoupletodP'] = mergeLot['tod']*mergeLot['coupleTodPrice']
        mergeLot['WinloypaeP'] = mergeLot['tod']*mergeLot['loypaePrice']
        mergeLot['WinyumP'] = mergeLot['top']*mergeLot['yumPrice']

        resultTwoButtom = resultLottery.twoButtom[0]
        resultTwoButtom = str(resultTwoButtom)
        resultTwoButtom = resultTwoButtom[0] + resultTwoButtom[1]
        winoneTwoButtom1 = resultTwoButtom[0]
        winoneTwoButtom2 = resultTwoButtom[1]
        winButtomone = mergeLot[mergeLot['lottery'].isin(
            [str(winoneTwoButtom1), str(winoneTwoButtom2)]) & (mergeLot['top'] != 0)]
        groupBywinButtomone = winButtomone.groupby(['customerName', 'lottery', '_id_x'], as_index=False)[['customerName', 'lottery', '_id_x', 'type', 'buttom', 'WinonebuttomP']].apply(
            lambda group: group.rename(columns={'buttom': 'ราคาซื้อ', 'WinonebuttomP': 'ราคาจ่าย'})).reset_index(drop=True)

        resultThreeTop = resultLottery.threeTop[0]
        resultThreeTop = str(resultThreeTop)
        resultThreeTop = resultThreeTop[0] + \
            resultThreeTop[1] + resultThreeTop[2]
        winoneTop1 = resultThreeTop[0]
        winoneTop2 = resultThreeTop[1]
        winoneTop3 = resultThreeTop[2]
        winoneTop = mergeLot[mergeLot['lottery'].isin(
            [str(winoneTop1), str(winoneTop2), str(winoneTop3)]) & (mergeLot['top'] != 0)]

        groupBywinTopone = winoneTop.groupby(['customerName', 'lottery', '_id_x'], as_index=False)[['customerName', 'lottery', '_id_x', 'type', 'top', 'WinonetopP']].apply(
            lambda group: group.rename(columns={'top': 'ราคาซื้อ', 'WinonetopP': 'ราคาจ่าย'})).reset_index(drop=True)

        winThreeTod = list(permutations(resultThreeTop))
        winThreeTod = set(winThreeTod)
        winThreeTod = ["".join(t) for t in winThreeTod]
        winThreeTod = mergeLot[(mergeLot['lottery'].isin(
            winThreeTod)) & (mergeLot['tod'] != 0)]
        winThreeTod = winThreeTod.replace({'type': {'3 ตัว': '3 ตัวโต๊ด'}})
        winloypae = winThreeTod.loc[winThreeTod['type'] == 'ลอยแพ']
        wincoupletod = winThreeTod.loc[winThreeTod['type'] == 'คู่โต๊ด']
        winThreeTod = winThreeTod.loc[winThreeTod['type'] == '3 ตัวโต๊ด']

        groupByWinThreeTod = winThreeTod.groupby(['customerName', 'lottery', '_id_x'], as_index=False)[['customerName', 'lottery', '_id_x', 'type', 'tod', 'WinthreetodP']].apply(
            lambda group: group.rename(columns={'tod': 'ราคาซื้อ', 'WinthreetodP': 'ราคาจ่าย'})).reset_index(drop=True)
        groupByWincoupletod = wincoupletod.groupby(['customerName', 'lottery', '_id_x'], as_index=False)[['customerName', 'lottery', '_id_x', 'type', 'tod', 'WincoupletodP']].apply(
            lambda group: group.rename(columns={'tod': 'ราคาซื้อ', 'WincoupletodP': 'ราคาจ่าย'})).reset_index(drop=True)
        groupByWinloypae = winloypae.groupby(['customerName', 'lottery', '_id_x'], as_index=False)[['customerName', 'lottery', '_id_x', 'type', 'tod', 'WinloypaeP']].apply(
            lambda group: group.rename(columns={'tod': 'ราคาซื้อ', 'WinloypaeP': 'ราคาจ่าย'})).reset_index(drop=True)

        resultTopThree = resultLottery.threeTop[0]
        winTopThree = mergeLot[(mergeLot['lottery'] == str(
            resultTopThree)) & (mergeLot['top'] != 0)]
        winTopThree = winTopThree.replace({'type': {'3 ตัว': '3 ตัวบน'}})
        winYum = winTopThree.loc[winTopThree['type'] == 'ยำ']
        winTopThree = winTopThree.loc[(winTopThree['type'] == '6 กลับ') | (
            winTopThree['type'] == '3 กลับ') | (winTopThree['type'] == '3 ตัวบน')]
        groupByWinTopThree = winTopThree.groupby(['customerName', 'lottery', '_id_x'], as_index=False)[['customerName', 'lottery', '_id_x', 'type', 'top', 'WinthreetopP']].apply(
            lambda group: group.rename(columns={'top': 'ราคาซื้อ', 'WinthreetopP': 'ราคาจ่าย'})).reset_index(drop=True)
        groupByWinyumP = winYum.groupby(['customerName', 'lottery', '_id_x'], as_index=False)[['customerName', 'lottery', '_id_x', 'type', 'top', 'WinyumP']].apply(
            lambda group: group.rename(columns={'top': 'ราคาซื้อ', 'WinyumP': 'ราคาจ่าย'})).reset_index(drop=True)

        winThreeButtom_1 = resultLottery.threeButtom_1[0]
        winThreeButtom_2 = resultLottery.threeButtom_2[0]
        winThreeButtom_3 = resultLottery.threeButtom_3[0]
        winThreeButtom_4 = resultLottery.threeButtom_4[0]
        winThreeButtom = mergeLot[((mergeLot['lottery'] == str(winThreeButtom_1)) | (mergeLot['lottery'] == str(winThreeButtom_2)) | (
            mergeLot['lottery'] == str(winThreeButtom_3)) | (mergeLot['lottery'] == str(winThreeButtom_4))) & (mergeLot['buttom'] != 0)]
        winThreeButtom = winThreeButtom.replace(
            {'type': {'3 ตัว': '3 ตัวล่าง'}})
        groupByWinThreeButtom = winThreeButtom.groupby(['customerName', 'lottery', '_id_x'], as_index=False)[['customerName', 'lottery', '_id_x', 'type', 'buttom', 'WinthreebuttomP']].apply(
            lambda group: group.rename(columns={'buttom': 'ราคาซื้อ', 'WinthreebuttomP': 'ราคาจ่าย'})).reset_index(drop=True)

        winThreeTop = resultLottery.threeTop[0]
        winTopTwo = mergeLot[(mergeLot['lottery'] == str(
            winThreeTop)[1:]) & (mergeLot['top'] != 0)]
        winTopTwo = winTopTwo.replace({'type': {'2 ตัว': '2 ตัวบน'}})
        groupBywinTopTwo = winTopTwo.groupby(['customerName', 'lottery', '_id_x'], as_index=False)[['customerName', 'lottery', '_id_x', 'type', 'top', 'WintwotopP']].apply(
            lambda group: group.rename(columns={'top': 'ราคาซื้อ', 'WintwotopP': 'ราคาจ่าย'})).reset_index(drop=True)
        winTwoButtom = resultLottery.twoButtom[0]
        winTwoButtom = mergeLot[(mergeLot['lottery'] == str(
            winTwoButtom)) & (mergeLot['buttom'] != 0)]
        winTwoButtom = winTwoButtom.replace({'type': {'2 ตัว': '2 ตัวล่าง'}})
        groupBywinTwoButtom = winTwoButtom.groupby(['customerName', 'lottery', '_id_x'], as_index=False)[['customerName', 'lottery', '_id_x', 'type', 'buttom', 'WintwobuttomP']].apply(
            lambda group: group.rename(columns={'buttom': 'ราคาซื้อ', 'WintwobuttomP': 'ราคาจ่าย'})).reset_index(drop=True)
        concatenated = pd.concat([groupByWinTopThree, groupByWinThreeTod, groupBywinButtomone, groupBywinTopone,
                                  groupByWinThreeButtom, groupBywinTopTwo, groupBywinTwoButtom, groupByWincoupletod, groupByWinloypae, groupByWinyumP])

        groupbycustomerName = concatenated.groupby(['customerName', 'lottery', '_id_x'], as_index=False)[
            ['customerName', '_id_x', 'lottery', 'type', 'ราคาซื้อ', 'ราคาจ่าย']].apply(lambda group: group.rename(columns={'type': 'หมายเหตุ'})).reset_index(drop=True)
        sum_buy = concatenated.groupby(['customerName'])['ราคาจ่าย'].sum()
        sum_buy = sum_buy.reset_index()
        sumlot = lottery.replace(
            {'type': {'19 ประตู': '2 ตัว', '3 กลับ': '3 ตัว', '6 กลับ': '3 ตัว'}})
        sumlot['sum'] = sumlot['top'] + sumlot['tod'] + sumlot['buttom']
        pv_lot = pd.pivot_table(sumlot, values='sum', index=[
                                'customerID', 'customerName', 'type'], aggfunc=np.sum)
        pv_lot = pd.DataFrame(pv_lot.to_records())
        pv_lot.fillna(0, inplace=True)
        pc = pd.DataFrame(customer)
        pc['3 ตัว'] = pc['threeTopPercent']
        pc['2 ตัว'] = pc['twoTopPercent']
        pc['วิ่ง'] = pc['oneTopPercent']
        pc['คู่โต๊ด'] = pc['coupleTodPercent']
        pc['ลอยแพ'] = pc['loypaePercent']
        pc['ยำ'] = pc['yumPercent']
        new_pc = pd.melt(pc, id_vars=['customerID', 'customerName'], value_vars=[
            '2 ตัว', '3 ตัว', 'คู่โต๊ด', 'ยำ', 'ลอยแพ', 'วิ่ง'], var_name='type', value_name='percen')
        merge_pc = pd.merge(new_pc, pv_lot, on=[
                            'customerID', 'customerName', 'type'], how='outer')
        merge_pc.fillna(0, inplace=True)
        merge_pc = pd.pivot_table(merge_pc, values=['sum', 'percen'], index=[
            'customerID', 'customerName', 'type'], aggfunc=np.sum)
        merge_pc = pd.DataFrame(merge_pc.to_records())
        merge_pc['หัก'] = merge_pc['sum']*merge_pc['percen']/100
        merge_pc['คงเหลือ'] = merge_pc['sum']-merge_pc['หัก']
        summarize = pd.pivot_table(merge_pc, values=['sum', 'หัก', 'คงเหลือ'], index=[
            'customerID', 'customerName'], aggfunc=np.sum)
        summarize = pd.DataFrame(summarize.to_records())
        summarize = pd.merge(summarize, sum_buy, on=[
                             'customerName'], how='outer')
        summarize.fillna(0, inplace=True)
        summarize['จ่าย'] = summarize['คงเหลือ'] - summarize['ราคาจ่าย']
        customer = pd.merge(customer, summarize, on=[
                            'customerName'], how='outer')
        customer = customer.loc[customer['sum'] != 0]

        pdf = ResultPDF()
        pdf.add_font('DB-Heavent', '', 'fonts/DB-Heavent.ttf', uni=True)
        pdf.set_font('DB-Heavent', '', 16)
        pdf.set_auto_page_break(auto=True, margin=15)

        header = ['ประเภท', 'ตัวเลข', 'ซื้อ', 'จำนวนเงิน']
        header2 = ['', 'ยอดซื้อ', 'เปอร์เซ็น', 'ยอดหัก', 'คิดเป็นเงิน']

        for indexCust, rowCust in customer.iterrows():
            pdf.add_page()
            pdf.set_font('DB-Heavent', '', 16)
            pdf.set_xy(20, 20)
            pdf.cell(20, 10, 'ชื่อลูกค้า : ' +
                     rowCust['customerName'])
            pdf.ln()
            pdf.set_x(20)
            for j in range(len(header)):
                pdf.cell(40, 10, header[j], border=1)
            pdf.ln()
            for indexGroupby,  rowGroupby in groupbycustomerName.iterrows():
                if (rowGroupby['customerName'] == rowCust['customerName']):
                    pdf.set_x(20)
                    pdf.cell(40, 10, rowGroupby['หมายเหตุ'], border=1)
                    pdf.cell(40, 10, str(rowGroupby['lottery']), border=1)
                    pdf.cell(40, 10, str(
                        format(rowGroupby['ราคาซื้อ'], ',')), border=1)
                    pdf.cell(40, 10, str(
                        format(rowGroupby['ราคาจ่าย'], ',')), border=1, ln=True)
                n = 0
            for indexGroupby,  rowGroupby in merge_pc.iterrows():
                if (rowGroupby['customerName'] == rowCust['customerName']):
                    if n == 0:
                        pdf.cell(30, 5, "", ln=True)
                        for j in range(len(header2)):
                            pdf.cell(35, 10, header2[j])
                    pdf.ln()
                    pdf.set_x(20)
                    pdf.cell(30, 10, str(rowGroupby['type']))
                    pdf.cell(30, 10, str(format(rowGroupby['sum'], ',')))
                    pdf.cell(30, 10, str(rowGroupby['percen']) + "%")
                    pdf.cell(30, 10, str(format(rowGroupby['หัก'], ',')))
                    pdf.cell(30, 10, str(format(rowGroupby['คงเหลือ'], ',')))
                    n = n+1
            for indexGroupby,  rowGroupby in summarize.iterrows():
                if (rowGroupby['customerName'] == rowCust['customerName']):
                    pdf.ln()
                    pdf.cell(
                        20, 10, '---------------------------------------------------------------------------------------------------------')
                    pdf.ln()
                    pdf.set_x(20)
                    pdf.cell(20, 10, 'สรุป')
                    pdf.cell(40, 10, 'ยอดซื้อ : ' +
                             str(format(round(rowGroupby['sum'], 1), ',')))
                    pdf.cell(40, 10, 'ยอดหัก : ' +
                             str(format(round(rowGroupby['หัก'], 1), ',')))
                    pdf.cell(40, 10, 'ยอดคงเหลือ : ' +
                             str(format(round(rowGroupby['คงเหลือ'], 1), ',')))
                    pdf.ln()
                    pdf.set_x(40)
                    pdf.cell(40, 10, 'ยอดถูก : ' +
                             str(format(round(rowGroupby['ราคาจ่าย'], 1), ',')))
                    pdf.cell(40, 10, 'ยอดจ่าย : ' +
                             str(format(round(rowGroupby['จ่าย'], 1), ',')))

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
