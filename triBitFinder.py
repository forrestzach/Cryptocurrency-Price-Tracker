import json
from lib2to3.pgen2.token import EQUAL
import requests
from requests.exceptions import Timeout

def get_crypto_combinations(market_symbols, base):
    combinations = []
    for sym1 in market_symbols:   
        sym1_token1 = sym1.split('-')[0]
        sym1_token2 = sym1.split('-')[1]   
        if (sym1_token2 == base):
            for sym2 in market_symbols:
                sym2_token1 = sym2.split('-')[0]
                sym2_token2 = sym2.split('-')[1]
                if (sym1_token1 == sym2_token2):
                    for sym3 in market_symbols:
                        sym3_token1 = sym3.split('-')[0]
                        sym3_token2 = sym3.split('-')[1]
                        if((sym2_token1 == sym3_token1) and (sym3_token2 == sym1_token2)):
                            combination = {
                                'base':sym1_token2,
                                'intermediate':sym1_token1,
                                'ticker':sym2_token1,
                            }
                            combinations.append(combination)
    return combinations

try: 
    response = requests.get("https://api.bittrex.com/v3/markets", timeout=4)

except:
    print("failed")

json_response = json.loads(response.text)
#print(json_response)
clearedMarkets = []

for i in json_response:
    if len(i.get('prohibitedIn')) == 0:
        clearedMarkets.append(i.get('symbol'))

spiffyMarkets = []
for i in range(0, len(clearedMarkets), 1):
    if i != 0 or i != len(clearedMarkets):
        if clearedMarkets[i-1].split('-')[0] == clearedMarkets[i].split('-')[0] or clearedMarkets[i+1].split('-')[0] == clearedMarkets[i].split('-')[0]:
            spiffyMarkets.append(clearedMarkets[i])

symbols = []
for i in clearedMarkets:
    symbols.append(f'ticker_{i}')

###for i in symbols:
###    print(i)

for i in spiffyMarkets:
     print(i)
print(len(spiffyMarkets))

combos = get_crypto_combinations(clearedMarkets, 'USD')
#for i in combos:
    #print(i)

#print(len(combos))