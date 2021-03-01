import re
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
    #typetext = re.sub(r" ADJ_N_1 ADV_V_1 ADJ_N_2 PREP_1 ADJ_N_3 ", r" ADJ_N_1 ADV_V_1 ADJ_N_2 , ADJ_N_1 PREP_1 ADJ_N_3 , ADJ_N_2 PREP_1 ADJ_N_3 ", typetext)
    if toNarsese:
        #ADJ_N ADV_V ADJ_N -> <(ADJ_N * ADJ_N) --> ADV_V>
        typetext = re.sub(r" ADJ_N_([0-9]) ADV_V_([0-9]) ADJ_N_([0-9]) ", r" <( ADJ_N_\1 * ADJ_N_\3 ) --> ADV_V_\2 > ", typetext)
        #ADJ_N PREP ADJ_N -> <(ADJ_N * ADJ_N) --> PREP>
        typetext = re.sub(r" ADJ_N_([0-9]) PREP_([0-9]) ADJ_N_([0-9]) ", r" <( ADJ_N_\1 * ADJ_N_\3 ) --> PREP_\2 > ", typetext)
    return typetext

sentence = " the green cat quickly eats the blue mouse in the old house "
typetext = " DET_1 ADJ_1 N_1 ADV_1 V_1 DET_2 ADJ_2 N_2 PREP_1 DET_3 ADJ_3 N_3 "
typeWord = dict(zip(sentence.split(" "), typetext.split(" ")))
  
print("What? Tell \"" + sentence.strip() + "\" in simple sentences:")

sentence2 = " the green cat quickly eats the blue mouse "
print(sentence2)

sentence3 = " the green cat in the old house "
print(sentence3)

sentence4 = " the blue mouse in the old house "
print(sentence4)

L = [sentence2, sentence3, sentence4]
mapped = ",".join([reduceTypetext(" ".join([typeWord.get(x, "") for x in sentence.split(" ")]), toNarsese = False) for sentence in L])
print("( r\"" + reduceTypetext(typetext, toNarsese = False) + "\", r\"" + mapped + "\")")
