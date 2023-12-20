import urllib3
from bit import Key
from multiprocessing import cpu_count, Process
import requests
from bit.wallet import BaseKey
from cryptos.main import privtopub, get_privkey_format
from cryptos.main import generate_private_key, encode_privkey, privkey_to_pubkey

from requests import get
from time import sleep

from lib.pybitcointools.cryptos import get_private_keys, from_xprv
from lib.pybitcointools.cryptos.script_utils import get_coin

with open('wallets.txt', 'r') as file:
    wallets = set(file.read().split('\n'))
    if '' in wallets:
        wallets.remove('')

max_p = 115792089237316195423570985008687907852837564279074904382605163141518161494336


def writeFoundDatas(filename, wif, address, pk):
    with open(filename, 'a') as result:
        resultToWrite = "Address: {} PKwif: {} PK: {}\n".format(address, wif, pk)
        result.write(resultToWrite)


# random bruteforce
# Will randomly generate addresses
def RBF(r, sep_p):
    print('Instance: {} - Generating random addresses...'.format(r + 1))
    while True:
        pk = Key()
        if pk.address in wallets:
            print('Instance: {} - Found: {}'.format(r + 1, pk.address))
            writeFoundDatas("found_RBF.txt", pk.to_wif(), pk.address, pk)


# random bruteforce output
def debug_RBF(r, sep_p):
    print('Instance: {} - Generating random addresses...'.format(r + 1))
    while True:
        pk = Key()
        print('Instance: {} - Generated: {}'.format(r + 1, pk.address))
        if pk.address in wallets:
            print('Instance: {} - Found: {}'.format(r + 1, pk.address))
            writeFoundDatas("found_dRB.txt", pk.to_wif(), pk.address, pk)


# traditional bruteforce (slowest)
# Will try every INT from 0 to max possible
def TBF(r, sep_p):
    sint = sep_p * r if sep_p * r != 0 else 1
    mint = sep_p * (r + 1)
    print('Instance: {} - Generating addresses...'.format(r + 1))
    while sint < mint:
        pk = Key.from_int(sint)
        if pk.address in wallets:
            print('Instance: {} - Found: {}'.format(r + 1, pk.address))
            writeFoundDatas("found_TBF.txt", pk.to_wif(), pk.address, pk)
        sint += 1
    print('Instance: {}  - Done'.format(r + 1))


def pub_from_wif(pk):
    wif = pk.to_wif()
    privKey = Key(wif)

    myprivKey = generate_private_key()
    print('Instance: 1 - myprivKey: {}'.format(myprivKey))

   # my_pk_private_keys = get_private_keys(privKey)
   # print('Instance: 1 - privKey get_private_keys: {}'.format(my_pk_private_keys))

    my_private_keys = get_private_keys(myprivKey)
    print('Instance: 1 - get_private_keys: {}'.format(my_private_keys))

    myprivKey2 = encode_privkey(myprivKey, get_privkey_format(len(str(myprivKey))))
    print('Instance: 1 - myprivKey2: {}'.format(myprivKey2))

    theCoin = get_coin('btc', False)
    print('Instance: 1 - get_coin: {}'.format(theCoin))

    my_xpub = privkey_to_pubkey(myprivKey)
    print('Instance: 1 - privkey_to_pubkey: {}'.format(my_xpub))

    bitcoinAddress = privKey.address
    print('Instance: 1 - bitcoinAddress: {}'.format(bitcoinAddress))

    segwit_address = privKey.segwit_address
    print('Instance: 1 - segwit_address: {}'.format(segwit_address))

    public_key = privKey.public_key
    print('Instance: 1 - public_key: {}'.format(public_key))

    public_point = privKey.public_point
    print('Instance: 1 - public_point: {}'.format(public_point))

    privkey_format = get_privkey_format(len(str(myprivKey)))
    print('Instance: 1 - privkey_format: {}'.format(privkey_format))

    print('Instance: 1 - pub_to_hex: {} wif: {}'.format(BaseKey.pub_to_hex(pk), wif))
    print('Instance: 1 - Key: {} public_key: {}'.format(Key(str(wif)), privKey.public_key))

    encoded_privkey = encode_privkey(myprivKey, 'decimal')
    print('Instance: 1 - encoded_privkey: {}'.format(encoded_privkey))

    return public_key


# online bruteforce (randomized)
def OBF():
    print('Instance: 1 - Generating random addresses...')
    while True:
        pk = Key()

        print('Instance: 1 - Generated: {} wif: {}'.format(pk.address, pk.to_wif()))
        print('Instance: 1 - Checking balance...')

        try:
            getThisAddress = "https://blockchain.info/q/addressbalance/{}/".format(pk.address)
            balance = int(get(getThisAddress).text)
        except ValueError:
            print('Instance: 1 - Error reading balance from: {}'.format(pk.address))
            continue
        except (ConnectionError, urllib3.exceptions.ProtocolError, requests.exceptions.ConnectionError):
            print('Instance: 1 - Error Connection sleep for 10 seconds and try forver')
            sleep(10)
            continue
        except (requests.exceptions.ReadTimeout, urllib3.exceptions.ProtocolError, requests.exceptions.ConnectionError):
            print('Instance: 1 - Error ReadTimeout sleep for 10 seconds and try forver')
            sleep(10)
            continue

        print('Instance: 1 - {} has balance: {}'.format(pk.address, balance))
        if balance > 0:
            writeFoundDatas("found_OBF.txt", pk.to_wif(), pk.address, pk.public_key)
            print('Instance: 1 - Added address to found.txt')
        else:
            writeFoundDatas("not_found_OBF.txt", pk.to_wif(), pk.address, pk.public_key)

            print('Instance: 1 - pub_from_wif {}'.format(pub_from_wif(pk)))
            print('Instance: 1 - Added address to notfound.txt')

        print('Sleeping for 10 seconds...')
        sleep(10)


# traditional bruteforce output
def debug_TBF(r, sep_p):
    sint = sep_p * r if sep_p * r != 0 else 1
    mint = sep_p * (r + 1)
    print('Instance: {} - Generating addresses...'.format(r + 1))
    while sint < mint:
        pk = Key.from_int(sint)
        print('Instance: {} - Generated: {}'.format(r + 1, pk.address))
        if pk.address in wallets:
            print('Instance: {} - Found: {}'.format(r + 1, pk.address))
            writeFoundDatas("found_dTBF.txt", pk.to_wif(), pk.address, pk)
        sint += 1
    print('Instance: {}  - Done'.format(r + 1))


# optimized traditional bruteforce
# Will try every INT between 10**75 and max possibility.
# This methode is based on the best practice to get the safest address possible.
def OTBF(r, sep_p):
    sint = (sep_p * r) + 10 ** 75 if r == 0 else (sep_p * r)
    mint = (sep_p * (r + 1))
    print('Instance: {} - Generating addresses...'.format(r + 1))
    while sint < mint:
        pk = Key.from_int(sint)
        if pk.address in wallets:
            print('Instance: {} - Found: {}'.format(r + 1, pk.address))
            writeFoundDatas("found_OTBF.txt", pk.to_wif(), pk.address, pk)
        sint += 1
    print('Instance: {}  - Done'.format(r + 1))


# optimized traditional bruteforce ouput
def debug_OTBF(r, sep_p):
    sint = (sep_p * r) + 10 ** 75 if r == 0 else (sep_p * r)
    mint = (sep_p * (r + 1))
    print('Instance: {} - Generating addresses...'.format(r + 1))
    while sint < mint:
        pk = Key.from_int(sint)
        print('Instance: {} - Generated: {}'.format(r + 1, pk.address))
        if pk.address in wallets:
            print('Instance: {} - Found: {}'.format(r + 1, pk.address))
            writeFoundDatas("found_dOTBF.txt", pk.to_wif(), pk.address, pk)
        sint += 1
    print('Instance: {}  - Done'.format(r + 1))


def main():
    # set bruteforce mode
    mode = (None, RBF, TBF, OTBF, OBF, debug_RBF, debug_TBF, debug_OTBF)

    # print menu
    menu_string = 'Select bruteforce mode:\n'
    for count, function in enumerate(mode):
        try:
            if 'debug' in function.__name__:
                menu_string += '{} - {} (Prints output)\n'.format(count, function.__name__)
            else:
                menu_string += '{} - {}\n'.format(count, function.__name__)
        except AttributeError:
            menu_string += '{} - Exit\n'.format(count)
    print(menu_string)

    try:
        choice = int(input('> '))
        if choice == 4:
            option = 4
            cpu_cores = 1
        elif choice != 0:
            print('How many cores do you want to use ({} available)'.format(cpu_count()))
            cpu_cores = int(input('> '))
            cpu_cores = cpu_cores if 0 < cpu_cores < cpu_count() else cpu_count()
            option = choice if 0 < choice <= len(mode) - 1 else 0
        else:
            option = 0
            cpu_cores = 0
    except ValueError:
        option = 0
        cpu_cores = 0

    if mode[option] and mode[option].__name__ != 'OBF':
        print('Starting bruteforce instances in mode: {} with {} core(s)\n'.format(mode[option].__name__, cpu_cores))

        instances = []
        for i in range(cpu_cores):
            instance = Process(target=mode[option], args=(i, round(max_p / cpu_cores)))
            instances.append(instance)
            instance.start()

        for instance in instances:
            instance.join()

    elif mode[option].__name__ == 'OBF':
        print('Starting bruteforce in mode: {} (6 per minute to '
              'respect API rate limit)\n'.format(mode[option].__name__))
        OBF()

    print('Stopping...')


if __name__ == '__main__':
    try:
        main()
    except TimeoutError:
        sleep(30)
        main()
    except requests.exceptions.ReadTimeout:
        sleep(60)
        main()
    finally:
        print("...")
        # https://www.blockchain.com/explorer/assets/btc/xpub/
        # http://blockchain.info/q/getblockcount
        # http://blockchain.info/address/$bitcoin_address?format=json&limit=50&offset=0
        # http://blockchain.info/latestblock
        # http://blockchain.info/address/$hash_160?format=json
        # https://www.blockchain.com/explorer/api/q
        #
