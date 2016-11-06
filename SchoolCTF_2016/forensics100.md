The description for this challenge reads:
"Johny Droptables went on the trail of hackers _xXx_-=BoStOnSkIe_Pu$$ies_1337=-_xXx_. You can get the login of one of them.

The flag is the login of the hacker."

There's a link to a .zip file. As usual, I began by examining the file to see if there's any hidden content or anything else to be aware of:
![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/schoolCTF_forensics100_1.png "Running binwalk")

Upon seeing nothing unsual, I went ahead and extracted content with binwalk and navigated to the new directory. There, we've got a new file called <strong>malware.exe</strong>,
which is indeed a normal Windows executable. 
![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/schoolCTF_forensics100_2.png "Extraction")

Before doing anything else with the file, I called <code>strings</code> on it to see if there was anything useful there. While digging through the output,
I saw a reference to the creator's directory structure, which contained his name:
![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/schoolCTF_forensics100_3.png "strings")

Since we need the hacker's name, making that into the flag <code>SchoolCTF{b05t0n_n491b4t0r_133}</code> is the solution!
