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
    wordtypes = dict([(tokens[i], wordtypes_ordered[i][1]) for i in range(len(tokens))])
    sys.stdout.flush()
    indexes = {} #index for each wordtype
    indexed_wordtypes = []
    for token in tokens:
        if wordtypes[token] not in indexes:
            indexes[wordtypes[token]] = 0
        indexes[wordtypes[token]] += 1
        indexed_wordtypes.append(wordtypes[token] + "_" + str(indexes[wordtypes[token]]))
    return tokens, wordtypes, " " + " ".join(indexed_wordtypes) + " "

#Return modified concrete word term ([modified] & term) if term was modified (by adjective or adverb), else return term
def modifyWordTerm(schema, term):
    m = re.match(schema, term)
    if not m:
        return term
    modifier = term.split("_")[0] + "_" + m.group(1)
    subject = term.split("_")[1] + "_" + m.group(1)
    if modifier in wordType:
        return "([ " + wordType[modifier] + " ] & " + wordType[subject] + " )"
    return subject

#Return the concrete word (compound) term
def getWordTerm(term):
    #ADJ_NOUN -> ([ADJ] & NOUN):
    term = modifyWordTerm(r"ADJ_NOUN_([0-9])", term)
    #ADV_VERB -> ([ADV] & VERB)
    term = modifyWordTerm(r"ADV_VERB_([0-9])", term)
    return wordType.get(term, term)

InnateSyntacticalTransformations = [
    (r" DET_([0-9]) ", r" "),
    (r" ADJ_([0-9]) NOUN_([0-9]) ", r" ADJ_NOUN_\2 "),
    (r" NOUN_([0-9]) ", r" ADJ_NOUN_\1 "),
    (r" ADV_([0-9]) VERB_([0-9]) ", r" ADV_VERB_\2 "),
    (r" VERB_([0-9]) ", r" ADJ_VERB_\1 ")
]

InnateRepresentRelations = [
    (r" ADJ_NOUN_([0-9]) ADV_VERB_([0-9]) ADJ_NOUN_([0-9]) ", r" <( ADJ_NOUN_\1 * ADJ_NOUN_\3 ) --> ADV_VERB_\2 > "),
    (r" ADJ_NOUN_([0-9]) ADP_([0-9]) ADJ_NOUN_([0-9]) ", r" <( ADJ_NOUN_\1 * ADJ_NOUN_\3 ) --> ADP_\2 > ")
]

def reduceTypetext(typetext, toNarsese=True):
    for (a,b) in InnateSyntacticalTransformations:
        typetext = re.sub(a, b, typetext)
    #ADJ_NOUN_1 ADV_VERB_1 ADJ_NOUN_2 ADP_1 ADJ_NOUN_3 -> ADJ_NOUN_1 ADV_VERB_1 ADJ_NOUN_2 , ADJ_NOUN_1 ADP_1 ADJ_NOUN_3 , ADJ_NOUN_2 ADP_1 ADJ_NOUN_3 (THIS ONE SHOULD BE LEARNED!)
    typetext = re.sub(r" ADJ_NOUN_1 ADV_VERB_1 ADJ_NOUN_2 ADP_1 ADJ_NOUN_3 ", r" ADJ_NOUN_1 ADV_VERB_1 ADJ_NOUN_2 , ADJ_NOUN_1 ADP_1 ADJ_NOUN_3 , ADJ_NOUN_2 ADP_1 ADJ_NOUN_3 ", typetext)
    if toNarsese:
        for (a,b) in InnateRepresentRelations:
            typetext = re.sub(a, b, typetext)
    return typetext

while True:
    line = " " + input().rstrip("\n") + " "
    print(line.rstrip("\n"))
    sentence = " the green cat quickly eats the yellow mouse in the old house "
    #sentence = line
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
            print("What? Tell \"" + sentence.strip() + "\" in simple sentences:")
            
            sentence2 = " the green cat quickly eats the yellow mouse "
            #print(sentence2)
            sentence3 = " the green cat in the old house "
            #print(sentence3)
            sentence4 = " the yellow mouse in the old house "
            #print(sentence4)
            L = [sentence2, sentence3, sentence4]
            #L = []
            while True:
                s = " " + input().rstrip("\n") + " "
                if s.strip() == "":
                    break
                L.append(s)
            mapped = ",".join([reduceTypetext(" " + " ".join([typeWord.get(x, "") for x in part.split(" ") if x.strip() != ""]) + " ", toNarsese = False) for part in L])
            print("( r\"" + reduceTypetext(typetextReduced, toNarsese = False) + "\", r\"" + mapped + "\")")
            break
        print(y.strip() + ". :|:")
