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
sentence = " the green cat quickly eats the blue mouse in the old house "
typetext = " DET_1 ADJ_1 N_1 ADV_1 V_1 DET_2 ADJ_2 N_2 PREP_1 DET_3 ADJ_3 N_3 "
wordType = dict(zip(typetext.split(" "), sentence.split(" ")))
print("//" + sentence)
print("//" + typetext)

def subsModifiers(schema, type):
    m = re.match(schema, type)
    if not m:
        return type
    modifier = type.split("_")[0] + "_" + m.group(1)
    subject = type.split("_")[1] + "_" + m.group(1)
    if modifier in wordType:
        return "([ " + wordType[modifier] + " ] & " + wordType[subject] + " )"
    return subject

def getWord(type):
    #ADJ_N -> ([ADJ] & N):
    type = subsModifiers(r"ADJ_N_([0-9])", type)
    #ADV_V -> ([ADV] & V)
    type = subsModifiers(r"ADV_V_([0-9])", type)
    return wordType.get(type, type)

def reduceTypetext(typetext, toNarsese=True):
    #DET -> .:
    typetext = re.sub(r" DET_([0-9]) ", r" ", typetext)
    #ADJ N -> ADJ_N:
    typetext = re.sub(r" ADJ_([0-9]) N_([0-9]) ", r" ADJ_N_\2 ", typetext)
    #N -> ADJ_N:
    typetext = re.sub(r" N_([0-9]) ", r" ADJ_N_\1 ", typetext)
    #ADV V -> ADV_V:
    typetext = re.sub(r" ADV_([0-9]) V_([0-9]) ", r" ADV_V_\2 ", typetext)
    #V -> ADV_V:
    typetext = re.sub(r" V_([0-9]) ", r" ADJ_V_\1 ", typetext)
    #ADJ_N_1 ADV_V_1 ADJ_N_2 PREP_1 ADJ_N_3 -> ADJ_N_1 ADV_V_1 ADJ_N_2 , ADJ_N_1 PREP_1 ADJ_N_3 , ADJ_N_2 PREP_1 ADJ_N_3 (THIS ONE SHOULD BE LEARNED!)
    typetext = re.sub(r" ADJ_N_1 ADV_V_1 ADJ_N_2 PREP_1 ADJ_N_3 ", r" ADJ_N_1 ADV_V_1 ADJ_N_2 , ADJ_N_1 PREP_1 ADJ_N_3 , ADJ_N_2 PREP_1 ADJ_N_3 ", typetext)
    if toNarsese:
        #ADJ_N ADV_V ADJ_N -> <(ADJ_N * ADJ_N) --> ADV_V>
        typetext = re.sub(r" ADJ_N_([0-9]) ADV_V_([0-9]) ADJ_N_([0-9]) ", r" <( ADJ_N_\1 * ADJ_N_\3 ) --> ADV_V_\2 > ", typetext)
        #ADJ_N PREP ADJ_N -> <(ADJ_N * ADJ_N) --> PREP>
        typetext = re.sub(r" ADJ_N_([0-9]) PREP_([0-9]) ADJ_N_([0-9]) ", r" <( ADJ_N_\1 * ADJ_N_\3 ) --> PREP_\2 > ", typetext)
    return typetext

typetext = reduceTypetext(typetext)
print("//" + typetext)
for y in " ".join([getWord(x) for x in typetext.split(" ")]).split(" , "):
    if not y.strip().startswith("<") or not y.strip().endswith(">"): #may need better check
        print("What? Tell \"" + sentence.strip() + "\" in simple sentences:")
        break
    print(y.strip() + ". :|:")
