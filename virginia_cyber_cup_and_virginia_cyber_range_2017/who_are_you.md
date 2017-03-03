**Note: As mentioned in the readme for this directory, if you're interested in working through the Cyber Range problems yourself, 
you shouldn't use these writeups as guides unless you're REALLY stuck or have no idea what to do. Don't rob yourself of the 
chance to learn on your own! Look at these after you've solved the problems to see if you missed anything or if there was an
alternate solution.**

This is a 25-point network challenge. The description reads: "Who logged in?"

The attached file is entitled "ftp_packets" and is a .pcap file, so FTP traffic is probably the area to examine first.

After opening the .pcap file, I tried filtering by FTP traffic first. Even when there's not an obvious hint that FTP is important to the challenge, FTP and HTTP are good starting points because they're in plaintext and are easy to parse for credentials or file transfers. 

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/cyber_fusion_who_are_you_1.png "FTP traffic")

Looks like there's a login and then some actions over FTP. This is worth investgating, so I checked the TCP stream (from the first packet listed in the FTP filter).

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/cyber_fusion_who_are_you_2.png "TCP stream")

The name of the user who logged in is "anonymous." Since we're supposed to find out who logged in, that's our flag!
