from collections import defaultdict
def gourp_anagrams(words):
    anagram_map=defaultdict(list)

    for word in words:
        key= ''.join(sorted(word))
        anagram_map[key].append(word)
    return list(anagram_map.values())

words=['eat','tea','tan','tae','ate','nat','bat','tab','sushma']
print(gourp_anagrams(words))



def group_anagrams(words):
    anagram_map=defaultdict(list)

    for word in words:
        key=''.join(sorted(word))
        anagram_map[key].append(word)
    return list(anagram_map.values())

words=['tae','tea','ate','aet','nat','tan']