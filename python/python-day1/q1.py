##second largest number
'''
def second_largest(nums):

    first=second=float('-inf')
    for num in set(nums):
        if num > first:
            second=first
            first=num 

        elif num > second:
            second=num
    if second==float('-inf'):
        return None
    return second

nums=[10,20,30,40,60,88]
print(second_largest(nums))

'''
def second_largest(nums):
    first=second=float('-inf')
    for num in set(nums):
        if num > first:
            second=first
            first=num 

        elif num > second:
            second=num
    if second==float('-inf'):
        return None
    return second
nums=[10,33,9,99,33,22,19,82,17]
print(second_largest(nums))
print(set(nums))
        