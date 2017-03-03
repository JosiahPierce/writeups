**Note: As mentioned in the readme for this directory, if you're interested in working through the Virginia Cyber Range problems yourself, 
you shouldn't use these writeups as guides unless you're REALLY stuck or have no idea what to do. Don't rob yourself of the 
chance to learn on your own! Look at these after you've solved the problems to see if you missed anything or if there was an
alternate solution.**

This is a 50-point forensics challenge. The description for the challenge reads: " Who knew Jane had a SID?!? What is it?"

There's a .vmem file to investigate. .vmem is a memory dump, and can be part of a snapshot of a virtual machine. Since the file has "WindowsVista" in the name, it's safe to assume it's a memory dump from a Windows system. That means I'm looking for a Security Identifier, or SID. SIDs are unique strings used to identifier users, and function similarly to session tokens. 

An example SID might look like this: S-1-5-21-1085031214-1563985344-725345543
(Example source: https://en.wikipedia.org/wiki/Security_Identifier)

With that example in mind, I tried just running <code>strings WindowsVista_0401.vmem | grep S-1</code> with the goal of isolating any SIDs. This probably isn't the most efficient or accurate way of going about the challenge, but it does yield results:

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/cyber_cup_jane_smith_1.png "Strings")

The SID string <code>S-1-5-21-3357474304-2915131210-3987339850-1000</code> frequently appears in the output from <code>strings</code>, so it might be the one we're looking for. It's worth noting that a few other SIDs appear in the output, so I just made my judgment based on the which ones appeared most frequently. The output is still limited enough that it'd be possible to just try submitting them all if necessary. Submitting it earns the points and confirms that it's the flag! 
