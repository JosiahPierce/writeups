#! /usr/bin/python

# this script is designed to reverse the JavaScript function found in the no_flag challenge
import string


user_string = str(raw_input("Enter the string: "))

if "^^^" in user_string:
    user_string = user_string.replace("^^^", "http:")

if "*^$#!" in user_string:
    user_string = user_string.replace("*^$#!", "bin")

if "*%=_()" in user_string:
    user_string = user_string.replace("*%=_()", "com")

if "~~@;;" in user_string:
    user_string = user_string.replace("~~@;;", "paste")


print user_string



