This is a 300-point forensics challenge. The description reads
<br>
`"Tommy wrote a program. It seems he has hidden from us important information. Find out what Tommy hides."`

As expected, we're given a .zip file to investigate.

This challenge was a strange one. It took me a very short time to solve, but I'm quite confident I didn't solve it the intended way, and I wasn't really expecting my technique to work. It seemed to be set up for something more complicated, and it was worth a lot of points, so I don't think it should have been so simple. That said, everyone loves finding unintended solutions to hacking problems, and I'll be curious to see if anyone else took this route.

First, let's extract data from the .zip file. I decided to start with binwalk rather than foremost this time.

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_canada_forensics1.png "Extracting files")

Navigating to the directory binwalk created, we can see that we've extracted a .zip file and a fresh nested directory. Let's check out the directory first. Inside is a file called "out.txt" and a file called "parse". out.txt proved to be a list of domain names. I wasn't sure of what to make of that, so I moved on to parse.

The parse file turned out to be an executable, but I couldn't seem to run it. I also couldn't get objdump to pull anything from it. However, running strings on the file did produce a lot of readable text. It was far too much to read over quickly, so I tried grepping for some common terms first. 

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_canada_forensics2.png "Flag grep")

Grepping for flag does give us results, but it doesn't look like it's giving us the kind of flag we want. How about if we grep for h4ck1t, since that precedes every flag?

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_canada_forensics3.png "Flag")

Innocently placed in the middle of a wall of text, we see our flag! 

`h4ck1t{T0mmy_g0t_h1s_Gun}`
