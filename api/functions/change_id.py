def change_id(arr_data):
    # обрабатывает первый объект в массиве
    # прохожу по объекту и заменяю ObjectId на строку и _id на id
    print('change_id_start', arr_data)
    arr_data = [i for i in arr_data]
    print('change_id_2', arr_data)
    arr_data[0]['id'] = str(arr_data[0]['_id'])
    del arr_data[0]['_id']
    arr_data[0]['author']['id'] = str(arr_data[0]['author']['_id'])
    del arr_data[0]['author']['_id']
    print('change_id_out', arr_data)
    return arr_data[0]

