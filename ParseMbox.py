import mailbox, re, os, string, nltk
from nltk.corpus import wordnet
from nltk import ngrams
from nltk import sent_tokenize
arr = []

donate_words = ['donate', 'donation', 'give',
                'contribute','contribution', ['chip','in']
                ]


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
    day_month = re.sub(' ','-', day_month)
    arr.append(day_month)

def get_features(ngram, mbox):
    donation_amount = ngram[2]
    firstWord = ngram[0]
    secondWord = ngram[1]
    fourthWord = ngram[3]
    fifthWord = ngram[4]
    author = mbox

    features = ({"first_word":firstWord,
                 "second_word":secondWord,
                 "fourth_word":fourthWord,
                 "fifth_word":fifthWord,
                 "donation_amount":donation_amount,
                 "author:":author})
    return features

super_dict = {}
punct = ";.?!,:()[]{}"
exclude = set(string.punctuation)



count = 0
for mbox in os.listdir('./Mail2/'):
    print(mbox)
    mail = mailbox.mbox('./Mail2/' + mbox)
    super_dict[mbox] = {}
    #mail = mailbox.mbox('./Mail/Democrats-Clinton.mbox')

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

        #For getting sentences
        '''
        sentArr = []
        for sent in re.split('[?.!]', msg):
            sent = re.sub('\n', '',sent)
            sent = re.sub(u"\u200c",'',sent)
            sent = re.sub(u"\u200b",'',sent)
            sent = re.sub(r'<[^<]+?>', '',sent)

            if(sent != ''):
                sentArr.append(sent)
        print(sentArr)
        '''
        '''
        sents = sent_tokenize(msg)
        #print(sents)
        for sent in sents:
            sent = re.sub('\n', '',sent)
            sent = re.sub(u"\u200c",'',sent)
            sent = re.sub(u"\u200b",'',sent)
            sent = re.sub(r'<[^<]+?>', '',sent)
            if('$' in sent and
                   ('donate' in sent or 'give' in sent or
                    'donation' in sent or 'giving' in sent or
                    'chip in' in sent or 'contribute' in sent or
                    'contribution' in sent)):
                print(sent)
        '''

        #For getting individual words
        prev_word = ''
        for w in msg.split():
            word = re.sub('\n', '',w)
            word = re.sub(u"\u200c",'',word)
            word = re.sub(u"\u200b",'',word)
            word = re.sub(r'<[^<]+?>', '',word)

            if('$' in word):
                words.append(word)
            else:
                word = ''.join(chr for chr in word
                               if chr not in punct)
                if(word != '' and "http" not in word):
                    words.append(word)

        sents = ' '.join(words)
        #print(sents)
        fivegrams = ngrams(sents.split(), 5)
        for gram in fivegrams:
            if('$' in gram[2] and
                   ('donate' in gram or 'give' in gram or
                    'donation' in gram or 'giving' in gram or
                    'chip in' in gram or 'contribute' in gram or
                    'contribution' in gram)):
                print(gram)
                get_features(gram, mbox)

        super_dict[mbox][date]['body'] = words

        #print(words)
        #print()
        count += 1
        #if(count == 20):
        #    exit(1)
    #print(super_dict[mbox])
    #break
#exit(1)


'''
#Done with this part, look at dates.txt

fdist = nltk.FreqDist(arr)
print(count)
print(sum(fdist.values()))

fp = open("dates.txt", 'w+')
for item, count in fdist.items():
    fp.write(item + " " + str(count) + '\n')
fp.close()

print(sorted(fdist.items(),key=lambda x: x[1]))
'''