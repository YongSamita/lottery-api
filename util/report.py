def handleGetPipelineReport(count, typeLotto, sortByLottery, start_date, end_date):
    pipeline = []
    if count == 'วิ่ง':
        pipeline.append(
            {'$match': {
                'lottery': {'$regex': '^.{1}$'},
                'createdAt': {'$gte': start_date, '$lte': end_date}
            }}
        )
    elif count == '2 ตัว':
        pipeline.append(
            {'$match': {
                'lottery': {'$regex': '^.{2}$'},
                'createdAt': {'$gte': start_date, '$lte': end_date}
            }}
        )
    elif count == '3 ตัว':
        pipeline.append(
            {'$match': {
                'lottery': {'$regex': '^.{3}$'},
                'createdAt': {'$gte': start_date, '$lte': end_date}
            }}
        )
    pipeline.append(
        {
            "$addFields": {
                "createdAt": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$createdAt"
                    }
                }
            }
        }
    )
    pipeline.append(
        {
            '$group': {
                '_id': {
                    'lottery': '$lottery',
                    'createdAt': "$createdAt",
                },
                'top': {'$sum': '$top'},
                'tod': {'$sum': '$tod'},
                'buttom': {'$sum': '$buttom'},
            }
        }
    )
    if (sortByLottery == 'true'):
        pipeline.append({
            '$sort': {
                '_id': 1
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
    return pipeline


def handleMappingResponseData(count, typeLotto, overLottery, resultLottery, resultLimit):
    result = []
    resultSum = []
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
            document['id'] = document['_id']['lottery']
            document['lottery'] = document['_id']['lottery']
            document['createdAt'] = document['_id']['createdAt']
            del document['buttom']
            del document['top']
            del document['tod']
            del document['_id']
            resultSum.append(document)
            if (document['over'] != 0):
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
            document['id'] = document['_id']['lottery']
            document['lottery'] = document['_id']['lottery']
            document['createdAt'] = document['_id']['createdAt']
            del document['buttom']
            del document['top']
            del document['tod']
            del document['_id']
            if (document['over'] != 0):
                result.append(document)

    return result, resultSum


def handleMappingResponseDataOver(count, typeLotto, overLottery, resultLottery, resultLimit):
    result = []
    resultSum = []
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
            document['id'] = document['_id']['lottery']
            document['lottery'] = document['_id']['lottery']
            document['createdAt'] = document['_id']['createdAt']
            del document['buttom']
            del document['top']
            del document['tod']
            del document['_id']
            resultSum.append(document)
            if (document['over'] == 0):
                if (overLottery == 'false'):
                    result.append(document)
            else:
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
            document['id'] = document['_id']['lottery']
            document['lottery'] = document['_id']['lottery']
            document['createdAt'] = document['_id']['createdAt']
            del document['buttom']
            del document['top']
            del document['tod']
            del document['_id']
            if (document['over'] == 0):
                if (overLottery == 'false'):
                    result.append(document)
            else:
                result.append(document)

    return result, resultSum


def handleGetLimitReport(count, typeLotto, resultLimit):
    limit = 0
    if len(resultLimit) > 0:
        if count == "2 ตัว":
            if typeLotto == 'บน':
                limit = resultLimit[0]['twoTop']
            elif typeLotto == 'ล่าง':
                limit = resultLimit[0]['twoButtom']
        elif count == "3 ตัว":
            if typeLotto == 'บน':
                limit = resultLimit[0]['threeTop']
            elif typeLotto == 'โต๊ด':
                limit = resultLimit[0]['threeTod']
            elif typeLotto == 'ล่าง':
                limit = resultLimit[0]['threeButtom']
    return limit
