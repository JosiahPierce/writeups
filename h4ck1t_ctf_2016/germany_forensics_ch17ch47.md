This is a 200-point forensics challenge. The description reads
<br>
`"Find out who is the recipient of the information from the agent."`

We have a .zip file to examine.

I did most of my initial analysis by using the tool foremost. After getting stuck, I eventually ended up using binwalk and extracted lots of data foremost didn't catch. I'll just jump straight to what binwalk uncovered, since it's how I solved the problem, but an important takeaway is that different forensics tools will uncover different things, and it's often necessary to use several to find what you're looking for.

First, extract data from the zip file with binwalk by running <code>binwalk -e CorpUser.zip</code>. binwalk provides a lot of output about the data it's extracted. The data near the end is rather interesting:

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_germany_forensics1.png "Extraction")

binwalk extracted some Skype data. I figured this would be a good area to examine, since we're supposed to find a recipient of information and Skype is a communication tool. There's plenty of other data to examine, but first I skipped past some of it and went to the _CorpUser.zip.extracted/CorpUser directory. Inside, there's an AppData directory. That was the area binwalk referenced when it extracted Skype data, so we should probably check there. Skype stores a lot of information in the roaming app data area in Windows, so we can begin with the roaming section here. Within, we can change to the Skype directory, and then we're met with a few options:

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_germany_forensics2.png "Skype directory")

I wasn't sure exactly where I'd find what I wanted, but the live#3aames.aldrich directory looked unusual, so I went there first. Inside, we see some .db files. Those can be parsed with something like sqlitebrowser. The file main.db seemed like a good starting point, so let's view that:

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_germany_forensics3.png "main.db")

There's a lot of useful-looking information there. Let's select the Browse Data tab and look around. See we're supposed to find out who the recipient of the information is, the contacts table is probably a good place to check. In that table, undercontacts, we find this:

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_germany_forensics4.png "Flag")

Our flag is there!
<br>
`h4ck1t{87e2bc9573392d5f4458393375328cf2}`
