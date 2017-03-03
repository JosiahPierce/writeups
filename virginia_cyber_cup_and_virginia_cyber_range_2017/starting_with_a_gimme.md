**Note: As mentioned in the readme for this directory, if you're interested in working through the Virginia Cyber Range problems yourself, 
you shouldn't use these writeups as guides unless you're REALLY stuck or have no idea what to do. Don't rob yourself of the 
chance to learn on your own! Look at these after you've solved the problems to see if you missed anything or if there was an
alternate solution.**

This is a 10-point reverse engineering challenge. There's no description for this challenge; we're simply given a binary to download. Because this is a simple challenge, I'm going to showcase two different ways to solve it. First I'll illustrate the method I used, and then I'll show the "true" method that actually involves reverse engineering.

Either way, the first step is to try running the binary. 

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/cyber_cup_starting_with_a_gimme_1.png "Running binary")

The binary prompts for a password; after receiving a (presumably) incorrect response, the program stops. Now it's time to consider our two different approaches:

**Approach 1: Strings**

Just like with forensics challenges, running <code>strings</code> on a binary can help reveal useful information. Calling it on the binary yields the following results:

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/cyber_cup_starting_with_a_gimme_2.png "Strings")

The most interesting line, of course, is <code>flag:wheredowegofromhere</code>, which is our flag! Also helpful is the fact that the password for the binary is revealed, though it appears that it's not actually used for solving the challenge. Nonetheless, this should provide an idea of how helpful <code>strings</code> can be for these challenges.

**Approach 2: Reversing the binary**

To begin reverse engineering the binary, I ran <code>objdump -D find_the_flag</code> to view its disassembled version. After a moment of digging, I noticed the following function:

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/cyber_cup_starting_with_a_gimme_3.png "Disassembly")

The "printFlag" function occurs right before main(). That's something to investigate further. Based on the run of the binary earlier, it doesn't seem that printFlag is called on a normal run. The next step is to try to jump to that function with a debugger.

![alt text](https://github.com/JosiahPierce/writeups/blob/master/images/cyber_cup_starting_with_a_gimme_4.png "Debugger")

After setting a break point at main and running the program, it's possible to jump into the printFlag function and continue the program execution, which once again reveals the flag!
