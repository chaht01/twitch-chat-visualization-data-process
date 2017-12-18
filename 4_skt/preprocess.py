import csv
import datetime
import time
import glob
import re
import collections
import shutil
from tempfile import NamedTemporaryFile

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
    return line
    #    if text != line:
    #    print(text)
    #       print(line)
    # words = re.findall(r'\S+', line)
    # return set(words)

wordsDict = {}
logDictPerTick= {}
logs = (glob.glob('chatlog_*.csv'))
with open('parsed/parsed_log.csv', 'a') as outfile:
    fieldnames = ['id', 'offset_seconds', 'text', 'parsed']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for log in logs:
        with open(log, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                parsedStr = parseWord(row[2])
                tick = int(float(row[1]))
                if tick not in logDictPerTick:
                    logDictPerTick[tick] = []
                logDictPerTick[tick].append(parsedStr)
                writer.writerow({
                    'id': row[0],
                    'offset_seconds': tick,
                    'text': row[2],
                    'parsed': parsedStr
                })
                if tick not in wordsDict:
                    wordsDict[tick] = collections.Counter()
                words = set(re.findall(r'\S+', parsedStr))
                wordsDict[tick] += collections.Counter(words)

totalWordCounter = collections.Counter()
for key, value in wordsDict.items():
    totalWordCounter += value

limit = 0
topWords = []
catDictPerTick = {}
with open('parsed/most_words.csv', 'a') as outfile:
    fieldnames = ['words', 'counts']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for word, value in totalWordCounter.most_common():
        if len(word) > 1:
            limit += 1
            writer.writerow({
                'words': word,
                'counts': value
            })
            topWords.append(word)
        if limit >= 20:
            break

for i, v in enumerate(topWords):
    for k in logDictPerTick:
        if k not in catDictPerTick:
            catDictPerTick[k] = [20]*len(logDictPerTick[k])
        for j, l in enumerate(logDictPerTick[k]):
            if v in l and catDictPerTick[k][j] is 20:
                catDictPerTick[k][j] = i

with open('parsed/tick_to_cats.csv', 'a') as outfile:
    fieldnames = ['tick']
    for w in topWords:
        fieldnames.append(w)
    fieldnames.append('not_classified')
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for tick in catDictPerTick:
        counter = [0]*21
        for item in catDictPerTick[tick]:
            counter[item] += 1
        result = {'tick': tick}
        for i, w in enumerate(topWords):
            result[w] = counter[i]
        # result['not_classified'] = counter[20]
        result['not_classified'] = 0
        writer.writerow(result)
print(catDictPerTick)
