import csv
import datetime
import time
import collections
import glob
import re

def parseWord(text):
    text = text.strip()
    hanguel = "[가-힣ㄱ-ㅎㅏ-ㅣ]"
    dellist = ['한테','에게','께서', '같은', '에서','으로','하고','보다','처럼','만큼','같이','도','조차','마저','까지','부터','이라도','라도',]
    line = re.sub(r"[\s]?[ㅡ]+[\s]?", "", text)
    line = re.sub(r"[\s]?[-]+[\s]?", "", line)
    line = re.sub(r"[ㅋ]+", " ", line)
    line = re.sub(r"(?<="+hanguel+")[?.,;]+", "", line)

    for delitem in dellist:
        line = re.sub(r"(?<="+hanguel+")("+delitem+")[\s]+"," ", line)
        line = re.sub(r"(?<="+hanguel+")("+delitem+")[\s]?$"," ", line)

    line = re.sub(r"(?<="+hanguel+")[은는가을를에의과와][\s]+", " ", line)
    line = re.sub(r"(?<="+hanguel+")[은는가을를에의과와][\s]?$", " ", line)

    line = re.sub(r"(?<="+hanguel+")(?<!차)[이][\s]+", " ", line)
    line = re.sub(r"(?<="+hanguel+")(?<!차)[이][\s]?$", " ", line)
    line = re.sub(r"(?<="+hanguel+")(?<![향바])[로][\s]+", " ", line)
    line = re.sub(r"(?<="+hanguel+")(?<![향바])[로][\s]?$", " ", line)

    line = re.sub(r"^([가-힣])\s+([가-힣])\s+([가-힣])$", r"\1\2\3", line) # for case '가 나 다'

    line = re.sub(r"[\s][\s]+", " ", line)
    line = re.sub(r"([가-힣ㄱ-ㅎㅏ-ㅣ])\1+", r"\1\1", line) # for case like 'ㄷㄷㄷ'
    line = re.sub(r"[?][?]+", "??", line)
    line = re.sub(r"[!][!]+", "!!", line)
    line = re.sub(r"[.][.]+", "..", line)
    line = re.sub(r"[,][,]+", ",,", line)
    #    if text != line:
    #    print(text)
    #       print(line)
    words = re.findall(r'\S+', line)
    return set(words)

logs = (glob.glob('./parsed/parsed_chatlog_*.csv'))
timeCounter = collections.Counter()
wordsDict = {}
chatDict = {}
for log in logs:
    with open(log, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        times = []
        for row in reader:
            times.append(row[0])
            if row[0] not in wordsDict:
                wordsDict[row[0]] = collections.Counter()
            if row[0] not in chatDict:
                chatDict[row[0]] = []
            parsedSet = parseWord(row[2])
            wordsDict[row[0]] += collections.Counter(parsedSet)
            chatDict[row[0]].append(parsedSet)

        timeCounter += collections.Counter(times)
        #print(sorted(timeCounter.items()))
print(len(timeCounter))
#print(wordsDict)

totalWordCounter = collections.Counter()
for key, value in wordsDict.items():
    totalWordCounter += value

limit = 0
topWords = []
for key, value in totalWordCounter.most_common():
    if len(key) > 1:
        limit += 1
        topWords.append(key)
    if limit >= 100:
        break


"""
Rule 1 : count the number of chat contains most common words
"""
chatMCWDict = {}
chatMCWCounter = {}
for time, value in chatDict.items():
    if time not in chatMCWDict:
        chatMCWDict[time] = []
        chatMCWCounter[time] = collections.Counter()
    for chat in chatDict[time]:
        inRank = False
        for idx, word in enumerate(topWords):
            if word in chat:  # 탑 100 단어가 파싱단어 목록(chat)에 있는가
                chatMCWDict[time].append({'rank': idx, 'word': word})
                chatMCWCounter[time] += collections.Counter([word])
                inRank = True
                break
            for word_chat in chat:
                if word in word_chat:  # 탑 100 단어가 피상단어 목록의 단어(word_chat)에 포함되는 단어인가
                    chatMCWDict[time].append({'rank': idx, 'word': word})
                    chatMCWCounter[time] += collections.Counter([word])
                    inRank = True
                    break
            if inRank:
                break
        if not inRank:
            chatMCWDict[time].append({'rank': -1, 'word': ''})
            chatMCWCounter[time] += collections.Counter([''])

for time in chatMCWCounter:
    print(time+": "+str(timeCounter[str(time)]))
    for key, value in chatMCWCounter[time].most_common():
        print(key, value)

"""
Rule 2 : count key words over total words at specific time
Loop over wordsDict and mark it has popular key word in topWords list
"""


