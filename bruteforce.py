from bit import Key
from multiprocessing import cpu_count, Process
from requests import get
from time import sleep

with open('wallets.txt', 'r') as file:
    wallets = set(file.read().split('\n'))
    if '' in wallets:
        wallets.remove('')

max_p = 115792089237316195423570985008687907852837564279074904382605163141518161494336


def writeFoundDatas(filename, wif, address):
    with open(filename, 'a') as result:
        resultToWrite = "Address: {} PKwif: {}\n".format(address, wif)
        result.write(resultToWrite)


# random bruteforce
# Will randomly generate addresses
def RBF(r, sep_p):
    print('Instance: {} - Generating random addresses...'.format(r + 1))
    while True:
        pk = Key()
        if pk.address in wallets:
            print('Instance: {} - Found: {}'.format(r + 1, pk.address))
            writeFoundDatas("found_RBF.txt", pk.to_wif(), pk.address)


# random bruteforce output
def debug_RBF(r, sep_p):
    print('Instance: {} - Generating random addresses...'.format(r + 1))
    while True:
        pk = Key()
        print('Instance: {} - Generated: {}'.format(r + 1, pk.address))
        if pk.address in wallets:
            print('Instance: {} - Found: {}'.format(r + 1, pk.address))
            writeFoundDatas("found_dRB.txt", pk.to_wif(), pk.address)


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
            writeFoundDatas("found_TBF.txt", pk.to_wif(), pk.address)
        sint += 1
    print('Instance: {}  - Done'.format(r + 1))


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

        print('Instance: 1 - {} has balance: {}'.format(pk.address, balance))
        if balance > 0:
            writeFoundDatas("found_OBF.txt", pk.to_wif(), pk.address)
            print('Instance: 1 - Added address to found.txt')
        else:
            writeFoundDatas("not_found_OBF.txt", pk.to_wif(), pk.address)
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
            writeFoundDatas("found_dTBF.txt", pk.to_wif(), pk.address)
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
            writeFoundDatas("found_OTBF.txt", pk.to_wif(), pk.address)
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
            writeFoundDatas("found_dOTBF.txt", pk.to_wif(), pk.address)
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
    main()
