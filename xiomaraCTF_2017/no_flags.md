This is a 50-point web challenge. The description reads "What would you do if we tell you there are no flags for this question? Go on, solve it. That reminds me, Nothing is impossible.

http://139.59.61.220:23467/ "

Navigating to the server reveals this page:
![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/xiomara_noflags_1.png "Page")

robots.txt is a good page to check to find hidden directories, so I started there. This revealed the following entry:

User-agent:*
Disallow: /flags/
Disallow: /more_flags/
Disallow: /more_and_more_flags/
Disallow: /no_flag/

Cool, so now I've got some directories to start checking. Each page loads an iframe with some Mr Robot-inspired ASCII art. Aside from being pretty neat art, there's nothing useful until the last directory, /no_flag. Checking the source on this page reveals an interesting piece of JavaScript:

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/xiomara_noflags_2.png "JavaScript code chunk")

The function grabs some specific strings and replaces them. When I searched the /no_flag page for the replaced versions, I noticed that the center of the image contained a suspicious string:

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/xiomara_noflags_3.png "String")

I wrote a brief Python script to perform the reverse action of the JavaScript code and then plugged in that string. The raw code is below in really ugly formatting (and can also be found with nice formatting in a separate file in this writeup directory):

import string


user_string = str(raw_input("Enter the string: "))

if "^^^" in user_string:
    user_string = user_string.replace("^^^", "http:")

if "*^$#!" in user_string:
    user_string = user_string.replace("*^$#!", "bin")

if "*%=_()" in user_string:
    user_string = user_string.replace("*%=_()", "com")

if "\~~@;;" in user_string:
    user_string = user_string.replace("~~@;;", "paste")


print user_string


(I removed the slashes and the /g from the beginning and end of each string because it's used for JS regular expressions, as far as I know. It made the decoded string messier if I left it in.)

The script spat out my string:
http://pastebin.com/SwzEKazp

Great, so now all I had to do was go to that page and I'd have the...wait, what?

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/xiomara_noflags_4.png "Pastebin")

So apparently the entry has been removed. I banged my head against the wall for a while after this, and eventually just searched the URL I'd been given. I located a Way Back Machine archive of the page and opened it, revealing a base64-encoded string.

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/xiomara_noflags_5.png "Flag")

The string decodes to <code>xiomara{1_4m_mr_r0b07}</code>, and that's the flag!
