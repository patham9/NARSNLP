"""
 * The MIT License
 *
 * Copyright 2021 The OpenNARS authors.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 * """

import re
import sys
import time
import subprocess
import nltk as nltk
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk import WordNetLemmatizer
from nltk.corpus import wordnet

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')
nltk.download('wordnet')

#convert universal tag set to the wordnet word types
def wordnet_tag(tag):
    if tag == "ADJ":
        return wordnet.ADJ
    elif tag == "VERB":
        return wordnet.VERB
    elif tag == "NOUN":
        return wordnet.NOUN
    elif tag == 'ADV':
        return wordnet.ADV
    else:          
        return wordnet.NOUN #default

#pos-tag the words in the input sentence, and lemmatize them thereafter using Wordnet
def words_and_types(text):
    tokens = [word.lower() for word in word_tokenize(text) if word.isalpha()]
    wordtypes_ordered = nltk.pos_tag(tokens, tagset='universal')
    wordtypes = dict(wordtypes_ordered)
    lemma = WordNetLemmatizer()
    tokens = [lemma.lemmatize(word, pos = wordnet_tag(wordtypes[word])) for word in tokens]
    wordtypes = dict([(tokens[i], wordtypes_ordered[i][1] if tokens[i] != "what" else "?1") for i in range(len(tokens))])
    sys.stdout.flush()
    indexed_wordtypes = []
    for i in range(len(tokens)):
        token = tokens[i]
        indexed_wordtypes.append(wordtypes[token] + "_" + str(i))
    return tokens, wordtypes, " " + " ".join(indexed_wordtypes) + " "

SyntacticalTransformations = [
    (r" DET_([0-9]) ", r" "),
    (r" ADJ_([0-9]) NOUN_([0-9]) ", r" ADJ_NOUN_\2 "),
    (r" NOUN_([0-9]) ", r" ADJ_NOUN_\1 "),
    (r" ADV_([0-9]) VERB_([0-9]) ", r" ADV_VERB_\2 "),
    (r" VERB_([0-9]) ", r" ADV_VERB_\1 ")
]

TermRepresentRelations = [
    (r"ADJ_NOUN_([0-9])", "([ %s ] & %s )", (1.0, 0.9)),
    (r"ADV_VERB_([0-9])", "([ %s ] & %s )", (1.0, 0.9))
]

StatementRepresentRelations = [
    (r" ADJ_NOUN_([0-9]) ADV_VERB_([0-9]) ADJ_NOUN_([0-9]) ", r" <( ADJ_NOUN_\1 * ADJ_NOUN_\3 ) --> ADV_VERB_\2 > ", (1.0, 0.9)),
    (r" ADJ_NOUN_([0-9]) ADP_([0-9]) ADJ_NOUN_([0-9]) ", r" <( ADJ_NOUN_\1 * ADJ_NOUN_\3 ) --> ADP_\2 > ", (1.0, 0.9)),
    (r" ADJ_NOUN_([0-9]) ADV_VERB_([0-9]) ADJ_([0-9]) ", r" <( ADJ_NOUN_\1 * [ ADJ_\3 ] ) --> ADV_VERB_\2 > ", (1.0, 0.9))
]

#Return what the word represents
def modifyWordTerm(schema, term, compound):
    m = re.match(schema, term)
    if not m:
        return term
    modifier = term.split("_")[0] + "_" + str(int(m.group(1))-1)
    atomic =  term.split("_")[1] + "_" + m.group(1)
    if modifier in wordType:
        return compound % (wordType[modifier], wordType[atomic]) 
    return atomic

#Return the concrete word (compound) term
def getWordTerm(term):
    for (a, b, _) in TermRepresentRelations:
        term = modifyWordTerm(a, term, b)
    if term.startswith("PRON_"):
        return "?1"
    return wordType.get(term, term)

def reduceTypetext(typetext, toNarsese=True):
    for (a,b) in SyntacticalTransformations:
        typetext = re.sub(a, b, typetext)
    if toNarsese:
        for (a,b,_) in StatementRepresentRelations:
            typetext = re.sub(a, b, typetext)
    return typetext

while True:
    line = " " + input().rstrip("\n") + " "
    print(line.rstrip("\n"))
    #sentence = " the green cat quickly eats the yellow mouse in the old house "
    sentence = line
    print(words_and_types(sentence)[2])
    typetext = words_and_types(sentence)[2] #" DET_1 ADJ_1 NOUN_1 ADV_1 VERB_1 DET_2 ADJ_2 NOUN_2 ADP_1 DET_3 ADJ_3 NOUN_3 "
    wordType = dict(zip(typetext.split(" "), sentence.split(" ")))
    typeWord = dict(zip(sentence.split(" "), typetext.split(" ")))
    print("//" + sentence)
    print("//" + typetext)
    typetextNarsese = reduceTypetext(typetext)
    typetextReduced = reduceTypetext(typetext, toNarsese = False)
    print("//" + typetextNarsese)
    for y in " ".join([getWordTerm(x) for x in typetextNarsese.split(" ")]).split(" , "):
        if not y.strip().startswith("<") or not y.strip().endswith(">"): #may need better check
            print("// What? Tell \"" + sentence.strip() + "\" in simple sentences:")
            L = []
            while True:
                s = " " + input().rstrip("\n") + " "
                if s.strip() == "":
                    break
                L.append(s)
            mapped = ",".join([reduceTypetext(" " + " ".join([typeWord.get(x, "") for x in part.split(" ") if x.strip() != ""]) + " ", toNarsese = False) for part in L])
            if mapped.strip() != "":
                REPRESENT = ( reduceTypetext(typetextReduced, toNarsese = False), mapped, (1.0, 0.45))
                print("//Added REPRESENT relation: " + str(REPRESENT))
                StatementRepresentRelations = [REPRESENT] + StatementRepresentRelations
            break
        print(re.sub(r"<\( ([^:]*) \* ([^:]*) \) --> is >", r"< \1 --> \2 >", y.strip() + ("?. :|:" if "?" in y else ". :|:")).replace("what","?1").replace("who","?1"))
