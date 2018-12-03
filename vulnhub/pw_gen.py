#!/usr/bin/python

import itertools
import time

initial_password = "k1ll0r"

charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_-+=}{[]';:?/><,."

# generate all 2-byte permutations of the charset
guesses = [''.join(i) for i in itertools.permutations(charset, 2)]

# append the guesses to the password and
# write to a file in order to create a wordlist for
# use with hydra or other SSH brute-force tool
print "Writing all passwords to file ssh_passwords.txt..."
for i in guesses:
	f = open("ssh_passwords.txt","a")
	f.write(initial_password + i + "\n")
	f.close()

print "Done!"
