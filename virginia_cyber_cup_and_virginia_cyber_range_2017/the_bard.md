This is a 15-point reverse engineering challenge. There's no description, just a file called 'datafile.txt'. 

After downloading the file, trying to read it reveals this:

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/cyber_cup_bard_1.png "Reading the file")

Hmm...that looks like binary data, not text. Is this really a text file? Running the <code>file</code> command provides the answer:

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/cyber_cup_bard_2.png "File type")

Aha! It's actually just a binary masquerading as a .txt file. This highlights the important fact that Linux doesn't actually care about file extensions; they're just ways of helping users remember what type a file is. Linux checks the actual starting bytes of a file to determine what type of file it's looking at. 

To make progress, let's make the file executable by using the command <code>chmod +x datafile.txt</code>. Then we can run it and see what happens.

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/cyber_cup_bard_3.png "File execution")

Running the binary yields <code>whatisinaname?</code>, and that's our flag.
