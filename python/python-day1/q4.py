import string 
def word_frequency(file_path):
    freq={ }
    with open(r"C:\practice\day2\text.txt",'r')as f:
        for line in f:
            line=line.lower()
            line=line.translate(str.maketrans("","",string.punctuation))
            words=line.split()

            for word in words:
                if word in freq:
                    freq[word]+=1
                else:
                    freq[word]=1
    return freq
print(word_frequency('text.txt'))
