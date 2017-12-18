import csv
import datetime
import time
import glob
import re
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


logs = (glob.glob('chatlog_*.csv'))
for log in logs:
    with open(log, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            with open('parsed_'+log, 'a') as outfile:
                fieldnames = ['id', 'offset_seconds', 'text', 'parsed']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                # parsedTimeStamp = int(time.mktime(datetime.datetime.strptime(row[0][0:19], '%Y-%m-%dT%H:%M:%S').timetuple()))
                writer.writerow({
                    'id': row[0],
                    'offset_seconds': row[1],
                    'text': row[2],
                    'parsed': parseWord(row[2])
                })

