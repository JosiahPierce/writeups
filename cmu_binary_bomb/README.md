This is a writeup on CMU's binary bomb assignment. The user is given the task of reverse engineering a binary in order to solve a series of "bomb phases", which are functions that expect specific input from the user. The user has to determine the expected input for every phase to defuse the bomb.

This guide covers the 32-bit version of this challenge; it is mirrored by Open Security Training and can be downloaded here:
http://opensecuritytraining.info/IntroX86_files/bomb.tar

As a relative newcomer to reverse engeering, I really enjoyed this challenge, and wanted to provide a writeup primarily targeted at other beginners. Hopefully, this will help highlight some lessons I learned while working through the challenge; perhaps those lessons will be useful to others as well.

The writeup is broken down by each phase of the bomb. If you're totally new to reverse engineering, I strongly recommend reading from the beginning, as the phases escalate in difficulty. I also recommend working along on your own machine as you read the writeup; hands-on work helps make the knowledge you acquire stick with you. Additionally, the tools we'll use will be discussed in the phase 1 section.
