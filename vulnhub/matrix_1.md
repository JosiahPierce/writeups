Matrix: 1 is a Boot2Root challenge recently posted on vulnhub.com. I encourage you to try to solve the VM on your own first, or to follow along with the guide on your own machine. The description for the VM is as follows:

<i>
Description: Matrix is a medium level boot2root challenge. The OVA has been tested on both VMware and Virtual Box.

Difficulty: Intermediate

Flags: Your Goal is to get root and read /root/flag.txt

Networking: DHCP: Enabled IP Address: Automatically assigned

Hint: Follow your intuitions ... and enumerate!

For any questions, feel free to contact me on Twitter: @unknowndevice64

</i>

For this challenge, we'll be using the host-only subnet 192.168.56.0/24.

<h2>Discovery</h2>

For the initial discovery of the VM's IP address, we can use nmap's ping scan capability (invoked with the -sn flag) to scan the host-only subnet:

<code>nmap -sn 192.168.56.0/24</code>
![Alt text](/images/matrix_1.png?raw=true "IP discovery")




My attacking machine's IP is 192.168.56.101, and since 192.168.56.102 references a VirtualBox NIC, we know that's the target machine.

<h2>Port scan</h2>

As I mentioned in my previous writeup on Bulldog, I split my port scans into three stages; first I start with a basic port scan using nmap with no extra flags. This scans the top 1000 ports and runs quickly. Once that completes, I run a more aggressive full port scan with service fingerprinting, OS detection and some NSE scripts. This sometimes takes a while to run, so I can let it work in the background while digging into the basic information uncovered with the first nmap scan. Once the aggressive scan is done, I'll perform an nmap scan of the top 1000 UDP ports. Occasionally there'll be a useful UDP service to target, so it's important not to skip that step.

Below are the results of the three scans (some slightly truncated for brevity's sake):

Basic scan (<code>nmap 192.168.56.102</code>):
<i>

Nmap scan report for 192.168.56.102<br>
Host is up (0.00017s latency).<br>
Not shown: 997 closed ports<br>
PORT      STATE SERVICE<br>
22/tcp    open  ssh<br>
80/tcp    open  http<br>
31337/tcp open  Elite<br>
MAC Address: 08:00:27:E5:B2:AA (Oracle VirtualBox virtual NIC)<br>
</i>

Full scan (<code>nmap -A 192.168.56.102 -p-</code>):
<i>

Nmap scan report for 192.168.56.102<br>
Host is up (0.00040s latency).<br>
Not shown: 65532 closed ports<br>
PORT      STATE SERVICE VERSION<br>
22/tcp    open  ssh     OpenSSH 7.7 (protocol 2.0)<br>
| ssh-hostkey: <br>
|   2048 9c:8b:c7:7b:48:db:db:0c:4b:68:69:80:7b:12:4e:49 (RSA)<br>
|   256 49:6c:23:38:fb:79:cb:e0:b3:fe:b2:f4:32:a2:70:8e (ECDSA)<br>
|_  256 53:27:6f:04:ed:d1:e7:81:fb:00:98:54:e6:00:84:4a (ED25519)<br>
80/tcp    open  http    SimpleHTTPServer 0.6 (Python 2.7.14)<br>
|_http-server-header: SimpleHTTP/0.6 Python/2.7.14<br>
|_http-title: Welcome in Matrix<br>
31337/tcp open  http    SimpleHTTPServer 0.6 (Python 2.7.14)<br>
|_http-title: Welcome in Matrix<br>
MAC Address: 08:00:27:E5:B2:AA (Oracle VirtualBox virtual NIC)<br>
Device type: general purpose<br>
Running: Linux 3.X|4.X<br>
OS CPE: cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:4<br>
OS details: Linux 3.2 - 4.9<br>
Network Distance: 1 hop<br>

TRACEROUTE<br>
HOP RTT     ADDRESS<br>
1   0.40 ms 192.168.56.102<br>
</i>

UDP scan (<code>nmap -sU 192.168.56.102</code>):
<i>

Nmap scan report for 192.168.56.102<br>
Host is up (0.00036s latency).<br>
Not shown: 999 closed ports<br>
PORT   STATE         SERVICE<br>
68/udp open|filtered dhcpc<br>
MAC Address: 08:00:27:E5:B2:AA (Oracle VirtualBox virtual NIC)<br>
</i>



<h2>Enumeration</h2>

Based on these results, the VM is running three TCP services: SSH, HTTP, and HTTP on the non-standard port 31337. The only enumerated UDP service is dhcpc, which is very typical and probably not interesting to us. I like to break down my enumeration by service.

<h3>SSH</h3>

Nmap reported that this is OpenSSH 7.7. There was recently a <a href="https://www.exploit-db.com/exploits/45233">username enumeration vulnerability</a> in OpenSSH, but that only applies to versions < 7.7, so we know this machine is patched against this attack. That's a useful vulnerability to know about, though, and it's always worth checking the OpenSSH version.

The next enumeration step against SSH is to just try connecting. We're looking for two pieces of information:
-Is there an SSH banner that might disclose any helpful info?
-Is there a message indicating that SSH authentication can only be performed via SSH keys (at least for the root user, since that's who we'll be trying to connect as here)?

If we enumerate a new username, we'll want to go back and perform this step again to see if that user seems to require key-based auth. If not, it might be worth trying to brute-force their credentials in the background.
![Alt text](/images/matrix_2.png?raw=true "SSH enum")




In this case, there's no banner and no immediate permission denied message related to key-based auth, so there's not much to see here for now.



<h2>HTTP</h2>

Upon visiting the page's index, we're presented with a fairly simple-looking page without any links:
![Alt text](/images/matrix_3.png?raw=true "HTTP port 80")




We'll want to perform the typical web enumeration steps, which include viewing the page source, running a nikto scan, and running dirbuster or another directory brute-forcing tool to discover hidden content. We'll also probably want to dig into any .js files for interesting content and identify the web page's technology stack.

Before launching any tools, though, start by reading the page source, looking carefully for comments or interesting file paths. By viewing the source, I noticed this line (highlighted in blue):
![Alt text](/images/matrix_4.png?raw=true "HTTP source port 80")




This line references the file path assets/img/p0rt_31337.png. Following that link presents a picture of a white rabbit. In Matrix style, we'll want to follow the rabbit, so it seems that we're being encouraged to visit the service running on port 31337. Thanks to having a good enumeration process, we already discovered the HTTP service on port 31337 earlier. 

In the interest of performing thorough enumeration, though, it's still important to run through the process outlined earlier; running nikto and dirbuster (or another similar tool) is still worthwhile. I won't inlcude the output here, because I ultimately didn't discover anything else relevant to the challenge on this service, but make certain that you don't skip these steps just because you've seen something else interesting; you might end up missing something crucial. For reference, the command to run nikto against this service would be:

<code>nikto -h http://192.168.56.102/</code>

You should also run dirbuster or another directory brute-forcing tool with a wordlist of your choice. Don't forget to define several different likely file extensions; I usually choose .html and .txt plus whatever the technology stack seems to include (.php, .js, .py, etc.). You can also include things like .bak or .backup. Keep in mind that the more file extensions you add, the longer your scan will take. 

<h2>HTTP on port 31337</h2>

Navigating to this service in a browser shows a page that looks quite similar to the one on port 80:
![Alt text](/images/matrix_5.png?raw=true "HTTP port 31337")



Let's go through the same enumeration process we performed on port 80, starting with reading the page source. Doing this reveals a new secret (relevant line highlighted in blue):
![Alt text](/images/matrix_6.png?raw=true "HTTP source port 31337")




This line contains a base64-encoded string. This can be decoded by running the following command:

<code>echo "ZWNobyAiVGhlbiB5b3UnbGwgc2VlLCB0aGF0IGl0IGlzIG5vdCB0aGUgc3Bvb24gdGhhdCBiZW5kcywgaXQgaXMgb25seSB5b3Vyc2VsZi4gIiA+IEN5cGhlci5tYXRyaXg=" |base64 -d</code>

This provides the output:
<i>
echo "Then you'll see, that it is not the spoon that bends, it is only yourself. " > Cypher.matrix
</i>

Note that the word "echo" is part of the decoded string. Initially I believed that this might be referring to <a href="https://en.wikipedia.org/wiki/Virtual_hosting">virtual hosting</a>, in which navigating to a page by using a specific domain name can cause it to serve up specific content that differs from what you'd get if you used the IP address (or a different domain name also being hosted on that IP). However, noticing the use of the word "echo" and the output redirector ">" indicates that something is actually being placed in a file called Cypher.matrix. This led me to try navigating to the page http://192.168.56.102:31337/Cypher.matrix, which allowed me to download the file.

Viewing the file produces this very unusual output:
![Alt text](/images/matrix_7.png?raw=true "Cypher.matrix contents")



I thought this looked familiar, and after searching around for a few moments, I determined that this was Brainfuck, a novelty programming language. I then searched for an online Brainfuck interpreter that would run the code contained in Cypher.matrix, pasted in the code, ran it, and got this output:

<i>
You can enter into matrix as guest, with password k1ll0rXX

Note: Actually, I forget last two characters so I have replaced with XX try your luck and find correct string of password.
</i>

Looks like we'll need to find some way of generating all of the possible passwords that begin with "k1ll0r" and conclude with two more characters. There's probably some super fancy way of using the Crunch wordlist generation tool to do this, but instead I spent a little while making this Python script:

<code>
#!/usr/bin/python

import itertools
import time

initial_password = "k1ll0r"

charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_-+=}{[]';:?/><,."

# generate all 2-byte permutations of the charset
guesses = [''.join(i) for i in itertools.permutations(charset, 2)]

# append the guesses to the password and
# write to a file in order to create a wordlist for
# use with hydra or other SSH brute-force tool
print "Writing all passwords to file ssh_passwords.txt..."
for i in guesses:
	f = open("ssh_passwords.txt","a")
	f.write(initial_password + i + "\n")
	f.close()

print "Done!"
</code>

This code is pretty simple, but the idea is to generate all of the possible 2-character permutations based on the character set I provided and eventually prepend the known part of the password to each of the permutations. Rather than try to implement some kind of SSH brute-forcing directly in Python, I decided to just write out all of the possible passwords to a file and then use a Hydra, a brute-forcing tool, to read the wordlist I'd created. 

<h2>Exploitation</h2>

After generating the wordlist, I ran the following command to start brute-forcing:
<code>hydra -l guest -P ssh_passwords.txt ssh://192.168.56.102</code>

This tries to log in with the username "guest" and iterates through all the possible passwords in the ssh_passwords wordlist. After a few moments, I was presented with this output:
![Alt text](/images/matrix_8.png?raw=true "Hydra output")



We can log in with the username <b>guest</b> and the password <b>k1ll0r7n</b>.  Upon doing so, trying to issue some commands shows the following output:

guest@porteus:~$ id
-rbash: id: command not found
guest@porteus:~$ 

If you're not familiar with rbash, it's a restricted shell environment, designed to allow users to issue only specific commands. There are quite a few potential methods of escaping the restricted shell that administrators should be aware of, however. An excellent overview of rbash escape techniques (and techniques for escaping restricted shells in general) can be <a href="https://speakerdeck.com/knaps/escape-from-shellcatraz-breaking-out-of-restricted-unix-shells">found here</a>. 

In this case, the technique I originally used to escape the shell was to run the <code>vi</code> command. Vi can actually be used to execute shell commands. After launching vi, type <code>:!/bin/bash</code> and vi will spawn a bash shell. (This can also be done with other tools, including the text editors <b>less</b> and <b>more</b>). The bash shell spawned by vi will be free of the restrictions imposed by rbash. 

However, a cleaner way that I tried while working on this writeup is to SSH to the target with this command:
<code>ssh guest@192.168.56.102 -t "bash --noprofile"</code>

This executes a command immediately upon connecting, bypassing rbash. I prefer this method because the PATH environment variable is set up properly; if you use the method of escaping by executing a shell command within vi, your PATH won't be configured properly and you'll have to manually reset it (which isn't difficult, but it's one extra unnecessary step).

<h2>Privilege Escalation</h2>

Now that we've successfully gained access and escaped the restricted shell, we'll want to do the typical system enumeration to search for potential privilege escalation vulnerabilities. One of the first things to check is if our current user has any sudo privileges. This can be checked by running <code>sudo -l</code> and then providing a password if prompted. In this case, the output is:
<i>
guest@porteus:~$ sudo -l
User guest may run the following commands on porteus:
    (ALL) ALL
    (root) NOPASSWD: /usr/lib64/xfce4/session/xfsm-shutdown-helper
    (trinity) NOPASSWD: /bin/cp

</i>

So it looks like the guest user could either (presumably) run a shutdown utility as root, or can run the <b>cp</b> command as the trinity user. One thing to look for when checking sudo for privilege escalation vectors is whether the full path of the binary or script that can be run via sudo is provided; if not, it's possible to simply create a custom file with the same name and modify the PATH environment variable to point to that file first. In this case, the full path, /bin/cp, is provided, so we can't do something so simple.

Finding a way to abuse the permission to run cp as another user took me a little while, and was by far my favorite part of this whole box. At first glance, this doesn't seem that useful; we can copy files that the trinity user owns and place them elsewhere, for example, but it's important to note that <i>they'll still be owned by trinity and therefore not useful to the guest user</i>. We won't be able to read anything sensitive this way. 

What if we worked the other way around, though? Instead of copying stuff only trinity has access to, which doesn't get us anywhere, what if we copied a file we created to somewhere that only trinity can write to? How could we use this to gain access? The answer is to generate an SSH keypair on our attacking machine and copy the public key to a file on the target. We can then make that public key world-readable and use sudo to copy it to /home/trinity/.ssh/authorized_keys. We would then be able to use the private key on our attacking machine to connect as trinity!

To do this, I issued these commands:
<code>ssh-keygen -t rsa -b 4096 -C "trinity key"</code>
(I didn't provide a passphrase and saved the key to my current working directory as id_rsa)

<code>chmod 600 id_rsa</code>

I then copied the text in id_rsa.pub and pasted it into a file of the same name on the target machine in /tmp. I made it world-readable and then ran this command to copy it to trinity's authorized_keys file:
<code>sudo -u trinity /bin/cp /tmp/id_rsa.pub /home/trinity/.ssh/authorized_keys</code>

This ran successfully. To see if we now have access as trinity, we can run:
<code>ssh trinity@192.168.56.102 -i id_rsa</code>
![Alt text](/images/matrix_9.png?raw=true "trinity privesc")



Our next step is to see what new permissions we have as trinity. Let's check our sudo permissions again:
<i>
trinity@porteus:~$ sudo -l
User trinity may run the following commands on porteus:
    (root) NOPASSWD: /home/trinity/oracle

</i>

Interestingly, the file /home/trinity/oracle doesn't appear to exist. How can we exploit this? Well, since we have write access to trinity's home directory, let's just create our own file called oracle and make it whatever we want. In my case, I made it this tiny bash script that simply spawns a new shell:
<code>
#!/bin/bash
/bin/bash
</code>

I made this file executable and then ran this command to run it with root privileges:
<code>sudo /home/trinity/oracle</code>
![Alt text](/images/matrix_10.png?raw=true "root privesc")



With that, we've gained root and can view the flag at /root/flag.txt.

Thanks to Ajay Verma (@unknowndevice64) for creating this enjoyable box, and thanks for VulnHub for continuing to host so many learning resources!
