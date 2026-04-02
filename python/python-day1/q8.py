#data1=[{'name':'A','age':30},{'name':'B','age':10}]

#sorted_data=sorted(data1,key=lambda x:x['age'])
#print(sorted_data)

data3=[
    {'name':'surya','age':30},
    {'name':'sangeeta','age':33},
    {'name':'anita','age':44}
]
data2=[{'name':'anita','age':26},
       {'name':'sagar','age':40},
       {'name':'sony','age':10}]
sorted_Data=sorted(data3,key=lambda x:x['name'])
print(sorted_Data)
