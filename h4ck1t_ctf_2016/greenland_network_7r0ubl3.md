This is a 200-point network challenge. The description reads
<br>
`"Our network has been compromised! Find out what information hackers might gain access."`

We're given a .pcap file. A good starting point is to filter for traffic that's known for sending sensitive information in the clear, like FTP or Telnet. Sure enough, there's some FTP traffic.

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_greenland_network1.png "FTP traffic")

The section that caught my eye was near the end, where we see that the attacker made a RETR request for a file called secret.zip. As we can see from the screenshot, it looks like that file is successfully transferred and then the connection is closed. Because FTP transfers everything in clear text, it's possible to reassemble transferred files from the bytes we see in the .pcap file. First, let's find the section we want to reassemble by filtering for ftp-data:

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_greenland_network2.png "FTP filter")

We only see two packets. A brief once-over of each will reveal that one looks like a directory listing over FTP, and the other, containing 296 bytes, is the data from the RETR request. Great! Now all that's left is reassembling the file. To do this, first right-click the packet we want and follow the TCP stream.

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_greenland_network3.png "TCP stream")

Next, change the "Show data as" option from ASCII to raw. Now go ahead and select "save as" and save it as your_filename.raw. It's important to save it in .raw format so we can extract the data we want from it in the next step.

Now that we've got the raw file saved, let's run a forensics tool called foremost on it. In this case, we don't need any special flags, and can simply run <code>foremost file.raw</code>.

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_greenland_network4.png "foremost")

Foremost will create a directory called "output" where it stores the extracted data. Upon navigating there, we can see it's created a directory for extracted zip files. Inside we have a single zip file, so let's unzip it.

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_greenland_network5.png "unzip")

Unzipping it gives us a .tar file called "secret.tar". Running an untar command on that file provides a single secret.txt file. When we read the file, we get...

68 34 63 6b 31 74 7b 73 30 5f 33 34 73 59 5f 46 6c 34 67 5f 68 75 68 7d

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/h4ck1t_greenland_network6.png "Flag")

This is hex, so let's convert that to ASCII. When we do, we get:
<br>
`h4ck1t{s0_34sY_Fl4g_huh}`
