from bit import PrivateKeyTestnet, wif_to_key, network
import requests

# my_key = PrivateKeyTestnet()

# print(my_key.address)
# print(my_key.to_int())
# print(my_key.to_wif())

key = PrivateKeyTestnet('cMhi7YXQQTzaWLxRvcrAHXBhqKp3dn2ufhxJjKYq5bNLw6AWuxWW')
key1 = PrivateKeyTestnet('cSES7oBGk4Cpf6eQrb8pzYWZxcYCSPhABK7uVELPbpfYwvW6rvSf')

print('---------------Address Info---------------------')
print(key.address)
print(key1.address)

print('---------------Before Transaction---------------------')
print(key.get_balance('btc'))
print(key1.get_balance('btc'))
# print(key.unspents)

print(key.get_transactions())
print(key1.get_transactions())

print(network.get_fee(fast=False))
print(network.get_fee_cached())

# print(key.get_unspents())
# print(key1.get_unspents())
# #sess = requests.session()

# tx_hash = key1.send([(key.address, 0.0005, 'btc')])
# print(tx_hash)


# print('---------------After Transaction---------------------')
# print(key.get_balance('btc'))
# print(key1.get_balance('btc'))
# # print(key.unspents)


# print(key.get_transactions())
# print(key1.get_transactions())
# key.send()


# #r = sess.get('https://testnet-faucet.mempool.co/')

# #print(r.status_code)
# # print(r.text)