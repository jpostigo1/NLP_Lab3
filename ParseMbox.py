import mailbox, re, os, string, nltk, random
from nltk.corpus import wordnet
from nltk import ngrams
from nltk import sent_tokenize

arr = []
author_feats = []
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
        msg = msg.get_payload()[0]
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

    #binning didn't help improve the accuracy
    '''
    #binning categories: $0-99, 100-199, 200+
    bin1 = "0_99"
    bin2 = "100_199"
    bin3 = "200+"

    num = re.findall(r'\d+',donation_amount)
    num = int(num[0])
    #print(num)
    if(num >= 0 and num <= 99):
        donation_amount = bin1
    elif(num >= 100 and num <= 199):
        donation_amount = bin2
    else:
        donation_amount = bin3
    '''

    #predict author based on donation amount
    #and 4 words
    features = ({"first_word":firstWord,
                 "second_word":secondWord,
                 "fourth_word":fourthWord,
                 "fifth_word":fifthWord,
                 "donation_amount":donation_amount},
                author)
    author_feats.append(features)
    return

def PredictAuthor():
    avg_accuracy = 0
    num_trials = 5
    for i in range(num_trials):
        ratio = len(author_feats)//3
        random.shuffle(author_feats)
        train_set = author_feats[:ratio]
        test_set = author_feats[ratio:]

        NBClassifier = nltk.NaiveBayesClassifier.train(train_set)
        correct = 0
        cnt = 0

        for feature, label in test_set:
            correctLabel = label
            classifiedLabel = NBClassifier.classify(feature)
            if (classifiedLabel == correctLabel):
                correct += 1
            cnt += 1
        avg_accuracy += float(correct/cnt)
        #print("Trial",str(i+1) + ":", correct/cnt)

    return avg_accuracy/num_trials

super_dict = {}
punct = ";.?!,:()[]{}"
exclude = set(string.punctuation)
#count = 0
for mbox in os.listdir('./Mail2/'):
    print(mbox)
    mail = mailbox.mbox('./Mail2/' + mbox)
    super_dict[mbox] = {}

    for message in mail:
        words = []
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
        #trying to do POS tagging with sentences

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
                    ('chip' in sent and 'in' in sent) or 'contribute' in sent or
                    'contribution' in sent)):
                print(sent)
                text = nltk.word_tokenize(sent)
                pos = nltk.pos_tag(text)
                for word, speech in pos:
                    print(word, speech)
                exit(1)
        '''

        #For getting individual words
        #prev_word = ''
        for w in msg.split():
            word = re.sub('\n','',w)
            word = re.sub(u"\u200c",'',word)
            word = re.sub(u"\u200b",'',word)
            word = re.sub(r'<[^<]+?>', '',word)

            if('$' in word):
                words.append(word)
            else:
                word = ''.join(chr for chr in word
                               if chr not in punct)
                if(word != '' and "http" not in word):
                    #added .lower() to help with ngrams
                    words.append(word.lower())

        sents = ' '.join(words)

        fivegrams = ngrams(sents.split(), 5)
        for gram in fivegrams:
            if('$' in gram[2] and
                   ('donate' in gram or 'give' in gram or
                            'donation' in gram or 'giving' in gram or
                        ('chip' in gram and 'in' in gram) or
                            'contribute' in gram or 'contribution' in gram)):
                #print(gram)
                get_features(gram, mbox)


        super_dict[mbox][date]['body'] = words
        #count += 1
        #print(super_dict[mbox])

print("   Average predict authorship accuracy: {}".format(PredictAuthor()))

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
