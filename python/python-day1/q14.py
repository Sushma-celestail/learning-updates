nums=[1,-2,3,-4,-5,-6,7,8,9]

#result=[x if x >=0 else 0 for x in nums]
#print(result)

result=[]
for item in nums:
    if item >=0 :
        result.append(item)
    else:
        result.append(0)
print(result)

