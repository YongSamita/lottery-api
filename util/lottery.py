import datetime
from itertools import permutations
from flask import request


def handleCreateThreeSixSwitch(data):
    json_list = []
    list_set = []
    list_lottery = [int(digit) for digit in list(data['lottery'])]
    for perm in permutations(list_lottery, 3):
        swapped_perm = (perm[0], perm[1], perm[2])
        list_set.append(swapped_perm)
    list_set = set(list_set)
    unique_list_set = list(set(list_set))
    unique_list_set.sort()
    result_list = [''.join(str(i) for i in tpl) for tpl in unique_list_set]
    for item in result_list:

        if len(result_list) == 6:
            json_list.append({
                "customerName": data['customerName'],
                "customerID": data['customerID'],
                "lottery": item,
                "top": data['top'],
                "tod": data['tod'],
                "buttom": data['buttom'],
                "type": "6 กลับ",
                "createdBy": request.remote_addr,
                "createdAt": datetime.datetime.now()
            })
        else:
            json_list.append({
                "customerName": data['customerName'],
                "customerID": data['customerID'],
                "lottery": item,
                "top": data['top'],
                "tod": data['tod'],
                "buttom": data['buttom'],
                "type": "3 กลับ",
                "createdBy": request.remote_addr,
                "createdAt": datetime.datetime.now()
            })
    return json_list


def handleCreateNineteen(data):
    json_list = []
    two_digits = []

    lottery = [int(data['lottery'])]

    for i in range(10):
        two_digit = str(i) + str(lottery[0])
        two_digits.append(two_digit)
        two_digit = str(lottery[0]) + str(i)
        two_digits.append(two_digit)
    two_digits = set(two_digits)
    unique_result = list(set(two_digits))
    unique_result.sort()

    for item in unique_result:

        json_list.append({
            "customerName": data['customerName'],
            "customerID": data['customerID'],
            "lottery": item,
            "top": data['top'],
            "tod": data['tod'],
            "buttom": data['buttom'],
            "type": "19 ประตู",
            "createdBy": request.remote_addr,
            "createdAt": datetime.datetime.now()
        })

    return json_list
