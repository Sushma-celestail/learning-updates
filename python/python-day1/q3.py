
def top_k_frequent(nums,k): 

    freq ={} 

    for num in nums: 

        freq[num]=freq.get(num,0)+1 

    buckets=[[]for _ in range(len(nums)+1)] 

 

    for num,count in freq.items(): 

        buckets[count].append(num) 

 

    result=[] 

    for i in range(len(buckets)-1,0,-1): 

        for num in buckets[i]: 

            result.append(num) 

            if len(result)==k: 

                return result    

nums=[1,1,1,2,2,3,] 

k=2 

print(top_k_frequent(nums,k)) 