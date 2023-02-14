from random import shuffle
from itertools import groupby, permutations, combinations
import json
import yaml

#with open('indstillinger.json') as f:
	#indstillinger = json.load(f)l
with open('indstillinger.yaml') as f:
    indstillinger = yaml.load(f)

beboere = indstillinger['beboere']
vil_gerne_sammen = indstillinger['vil_gerne_sammen']
vil_ikke_sammen = indstillinger['vil_ikke_sammen']
vil_gerne_uger = indstillinger['vil_gerne_uger']
vil_ikke_uger = indstillinger['vil_ikke_uger']


for par in vil_gerne_sammen:
	for x in par:
		assert x in beboere, "%s er ikke blandt beboere. Fejl i vil_gerne_sammen." %x

for par in vil_ikke_sammen:
	for x in par:
		assert x in beboere, "%s er ikke blandt beboere. Fejl i vil_ikke_sammen." %x
beboere_allerede_fastlagt = []
for uge in vil_gerne_uger:
	assert len(uge)<=5, "der maa maks vaere 5 per linie i vil_gerne_uger"

	for x in uge:
		assert x in beboere, "%s er ikke blandt beboere. Fejl i vil_gerne_uger" %x
		assert x not in beboere_allerede_fastlagt, "%s er allerede placeret i en uge. Man kan ikke vaere i flere uger." %x
		beboere_allerede_fastlagt.append(x)

for uge in vil_ikke_uger:
	for x in uge:
		assert x in beboere, "%s er ikke blandt beboere. Fejl i vil_ikke_uger" %x


print "\nvil ikke sammen:\n%s" % '\n'.join([str(s) for s in vil_ikke_sammen])


print "\nvil gerne sammen:\n " + '\n'.join([str(s) for s in vil_gerne_sammen])


print "\nvil gerne uger:\n" + '\n'.join([str(s) for s in zip(range(1,6), vil_gerne_uger)])


print "\nvil ikke uger:\n" + '\n'.join([str(s) for s in zip(range(1,6), vil_ikke_uger)])

"""
indstillinger = {'beboere':beboere, 'vil_gerne_sammen':vil_gerne_sammen, 'vil_ikke_sammen':vil_ikke_sammen,
'vil_gerne_uger':vil_gerne_uger, 'vil_ikke_uger':vil_ikke_uger}
with open('indstillinger.json','w') as f:
	json.dump(indstillinger, f)

"""
#yaml.safe_dump(indstillinger, file('indstillinger.yaml','w'), encoding='utf-8', allow_unicode=True)

def tjek_uge(madhold, vil_gerne_sammen, vil_ikke_sammen, vil_gerne_denne_uge, vil_ikke_denne_uge):
    """
    Denne funktion tester om en maduge gaar op
    """
    navne = madhold

    for par in vil_gerne_sammen:
        navn1, navn2 = par
        if navn1 in navne and not navn2 in navne:
            #print '%s og %s vil gerne vaere sammen' %(navn1, navn2)
            return False

    for par in vil_ikke_sammen:
        navn1, navn2 = par
        if navn1 in navne and navn2 in navne:
            #print '%s og %s vil ikke vaere sammen' %(navn1, navn2)
            return False

    if any([navn in vil_ikke_denne_uge for navn in navne]):
        #print '%s vil ikke denne uge' % ' '.join(vil_ikke_denne_uge)
        return False

    if vil_gerne_denne_uge is not None:
        if not all([navn in navne for navn in vil_gerne_denne_uge]):
            #print '%s vil skal denne uge' % ' '.join(vil_gerne_denne_uge)
            return False

    return True


def find_madplan_shuffle(beboere, vil_gerne_sammen, vil_ikke_sammen, vil_gerne_uger, vil_ikke_uger, max_forsoeg = 1000000000):
    """
    Denne funktion proever sig frem indtil den finder en 5ugers madplan der gaar op
    """
    forsoeg = 0
    madplan = beboere
    while forsoeg<max_forsoeg:
        shuffle(madplan)
        #for madplan in permutations(beboere):
        if forsoeg % 10000 == 0:
            print forsoeg
        uge_tjek = []
        for j in range(5):
            madhold = madplan[j*5:(j+1)*5]
            s = tjek_uge(madhold, vil_gerne_sammen, vil_ikke_sammen, vil_gerne_uger[j], vil_ikke_uger[j])
            uge_tjek.append(s)
            if not s:
                break
        if all(uge_tjek):
            return [madplan[j*5:(j+1)*5] for j in range(5)]
        forsoeg+=1
        if forsoeg>max_forsoeg:
            return ((),(),(),(),())

    print "Forsoeg: ", forsoeg


def rekursiv_gennemgaa_uger(frie_beboere, vil_gerne_sammen, vil_ikke_sammen, vil_gerne_uger, vil_ikke_uger, n_per_hold):
    #print "Uge : ", 5-len(n_per_hold)
    #print vil_ikke_uger[0]
    #print n_per_hold[0]
    for hold in combinations(frie_beboere, n_per_hold[0]):
        rest_frie_beboere = set(frie_beboere) - set(hold)
        hold = set(hold) | set(vil_gerne_uger[0])
        if tjek_uge(hold, vil_gerne_sammen, vil_ikke_sammen, None, vil_ikke_uger[0]):
            if len(vil_ikke_uger)>1:
                #print "vil ikke naste uge : " , vil_ikke_uger[1:]
                naeste_hold = rekursiv_gennemgaa_uger(rest_frie_beboere, vil_gerne_sammen, vil_ikke_sammen, vil_gerne_uger[1:], vil_ikke_uger[1:], n_per_hold[1:])
                #print naeste_hold
                if naeste_hold is not False:
                    return [hold] + [h for h in naeste_hold]
                else:
                    continue
            else:
                return [hold]
    return False


def find_madplan_systematic(beboere, vil_gerne_sammen, vil_ikke_sammen, vil_gerne_uger, vil_ikke_uger):

    n_per_hold_basis = 5
    n_uger = 5
    n_per_hold = []
    for i in range(n_uger):
        n_per_hold.append(n_per_hold_basis - len(vil_gerne_uger[i]))
        print "Frie personer i uge %d: %d" % (i+1, n_per_hold[i])

    n_combi = []
    print "Kombinations muligheder:"
    try:
        import sympy
        raise
    except:
        pass
        
    else:
        for i in range(n_uger):
            n_combi.append(sympy.binomial(sum(n_per_hold[i:]), n_per_hold[i]))
            print "Uge %d: %d" % (i+1, n_combi[i])

        x = 1
        for y in n_combi:
            x*=y
        print "Total kombinations muligheder: %d" %x

    planer = []


    frie_beboere = set(beboere) - set(vil_gerne_uger[0]) - set(vil_gerne_uger[1]) - set(vil_gerne_uger[2]) - set(vil_gerne_uger[3]) - set(vil_gerne_uger[4])
    start_gaet = list(frie_beboere)
    shuffle(start_gaet)

    madplan = rekursiv_gennemgaa_uger(start_gaet, vil_gerne_sammen, vil_ikke_sammen, vil_gerne_uger, vil_ikke_uger, n_per_hold)
    return madplan



#madplan = find_madplan_shuffle(beboere, vil_gerne_sammen, vil_ikke_sammen, vil_gerne_uger, vil_ikke_uger)
madplan = find_madplan_systematic(beboere, vil_gerne_sammen, vil_ikke_sammen, vil_gerne_uger, vil_ikke_uger)
print ""
print "Uge plan: "
if madplan is not False:
    resultat = {}
    for j in range(5):
        print "Uge %d: %s" % (j+1, ', '.join(madplan[j]))
        resultat['uge%d'%(j+1)]=list(madplan[j])

    with open('resultat.yaml', 'w') as rf:
        yaml.dump(resultat, rf)


else:
    print "Madplan findes ikke"
s = raw_input('Faerdig')
