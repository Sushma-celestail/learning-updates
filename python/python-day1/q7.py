def flatten_list(nested_list):
    result=[]
    for item in nested_list:
        if isinstance(item,list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result
data=[1,[2,[3,4],5],6]
print(flatten_list(data))



def flattened_list(nested_list):
    result=[]

    for item in nested_list:
        if isinstance(item,list):
            result.extend(flattened_list)
        else:
            result.append(item)
    return result
data=[1,[2,[3,4],5],6]
print(flattened_list(data))
