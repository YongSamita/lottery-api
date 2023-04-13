import datetime
from itertools import combinations, permutations
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
                "createdBy": data['createdBy'],
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
                "createdBy": data['createdBy'],
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
            "createdBy": data['createdBy'],
            "createdAt": datetime.datetime.now()
        })

    return json_list


def handleCreateCupleTod(data):
    json_list = []
    three_digits = []
    for i in range(10):
        three_digit = str(i) + data['lottery']
        three_digits.append(three_digit)
    unique_result = list(set(three_digits))  # select only unique values
    unique_result.sort()
    for item in unique_result:
        json_list.append({

            "customerName": data['customerName'],
            "customerID": data['customerID'],
            "lottery": item,
            "top": data['top'],
            "tod": int(round(data['tod'] / 10)),
            "buttom": data['buttom'],
            "type": "คู่โต๊ด",
            "createdBy": data['createdBy'],
            "createdAt": datetime.datetime.now()
        })
    return json_list


def handleCreateLoyPae(data):
    json_list = []
    numbers = []
    for char in data['lottery']:
        num = int(char)
        numbers.append(num)
    result = list(combinations(numbers, 3))
    result = set(result)
    unique_list_set = list(set(result))  # select only unique values
    unique_list_set.sort()
    result_list = [''.join(str(i) for i in tpl) for tpl in unique_list_set]
    for item in result_list:
        json_list.append({

            "customerName": data['customerName'],
            "customerID": data['customerID'],
            "lottery": item,
            "top": data['top'],
            "tod": int(round(data['tod'] / len(result_list))),
            "buttom": data['buttom'],
            "type": "ลอยแพ",
            "createdBy": data['createdBy'],
            "createdAt": datetime.datetime.now()
        })
    return json_list


def handleCreateYums(data):
    json_list = []
    numbers = []
    result_perm = []
    for char in data['lottery']:
        num = int(char)
        numbers.append(num)
    for perm in permutations(numbers, 3):
        swapped_perm = (perm[2], perm[1], perm[0])
        result_perm.append(swapped_perm)
    result_perm = set(result_perm)
    unique_list_set = list(set(result_perm))  # select only unique values
    unique_list_set.sort()
    result_list = [''.join(str(i) for i in tpl) for tpl in unique_list_set]
    for item in result_list:
        json_list.append({

            "customerName": data['customerName'],
            "customerID": data['customerID'],
            "lottery": item,
            "top": int(round(data['top'] / len(result_list))),
            "tod": data['tod'],
            "buttom": data['buttom'],
            "type": "ยำ",
            "createdBy": data['createdBy'],
            "createdAt": datetime.datetime.now()
        })
    return json_list
