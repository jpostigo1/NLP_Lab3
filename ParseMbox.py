import mailbox, re, os, string, nltk

arr = []

def getcharsets(msg):
    charsets = set({})
    for c in msg.get_charsets():
        if c is not None:
            charsets.update([c])
    return charsets

def getBody(msg):
    while msg.is_multipart():
        msg=msg.get_payload()[0]
    t = msg.get_payload(decode=True)
    for charset in getcharsets(msg):
        t = t.decode(charset)
    return t


def parseDate(date):
    day_month_year = date.split(',')[1].strip()
    day_month = day_month_year[:6].strip()
    if(day_month[0] == '0'):
        day_month = day_month[1:]
    arr.append(day_month)

super_dict = {}
punct = ";.?!,:()[]{}"
exclude = set(string.punctuation)


for mbox in os.listdir('./Mail/'):
    print(mbox)
    mail = mailbox.mbox('./Mail/' + mbox)
    super_dict[mbox] = {}
    #mail = mailbox.mbox('./Mail/Democrats-Clinton.mbox')
    count = 0

    for message in mail:
        words = []
        #print(message['from'])
        #print(message['date'])
        date = message['date']
        parseDate(date)

        super_dict[mbox][date] = {}
        super_dict[mbox][date]['from'] = message['from']
        super_dict[mbox][date]['subject'] = message['subject']

        msg = getBody(message)
        #print(msg)
        #For getting individual words
        for w in msg.split():
            word = re.sub('\n', '',w)
            word = re.sub(u"\u200c",'',word)
            word = ''.join(chr for chr in word
                           if chr not in punct)
            if(word != ''):
                words.append(word)

        super_dict[mbox][date]['body'] = words
        #print(words)
        #print()
        #count += 1
        #if(count == 2):
    #print(super_dict[mbox])

fdist = nltk.FreqDist(arr)
print(sorted(fdist.items(),key=lambda x: x[1]))
#print(super_dict)

