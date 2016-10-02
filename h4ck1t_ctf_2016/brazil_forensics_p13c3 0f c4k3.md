This is a 100-point forensics challenge. The description reads 
`There is a suspicion that one of the data center agents concealing part of the information. Find out what kind of data Agent is hiding.
h4ck1t{}`

The challenge provides a .zip file. Let's start by running foremost, a forensics tool, on the file and seeing what data we can extract:

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_brazil_forensics1.png "Running foremost")

Now we can navigate to the output directory that foremost creates when it extract data. In this case, foremost placed all the extracted data in another .zip file, so let's unzip that and see what's there.

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_brazil_forensics2.png "Directory")

Unzipping the file gave us some .jpg files, a few documents, a couple of directories, and some interesting files called Thumbs.db and Thumbs.db:encryptable:$DATA. I tried examining the .jpg files first, just in case there was some obvious clue in them, but they mostly seemed to be assorted photos of aircraft. I decided to move on to the Thumbs.db files; I'd never heard of them before and trying to open them gave me an error. Similarly, attempting to extract data by running strings on them gave me no useful information. 

It turns out that Thumbs.db files are created by Windows in order to quickly display thumbnails of images. They're saved in a database upon first generation so that they don't have to be remade every time. If you want a high-level overview, you can read more here:
http://www.howtogeek.com/237091/what-are-the-thumbs.db-desktop.ini-and-.ds_store-files/

I thought that perhaps there'd be a thumbnail with the flag hidden inside the Thumbs.db file, so I located a utility to extract data from it called vinetto. First, create a directory for the thumbnails to be extracted to, and then run vinetto with the following syntax (taken from the manpage):
`vinetto [OPTION] [-o DIR] file`

So let's try that on our file. 

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_brazil_forensics3.png "Flag")

In the list of files we extract, there's one called h4ck1t{75943a3ca2223076e997fe30e17597d4}.jpg. That turns out to be our flag!
