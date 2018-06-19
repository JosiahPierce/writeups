<h3>Tools:</h3>

For this challenge, we'll primarily be making use of two tools:

<i>Radare2</i>

https://github.com/radare/radare2

This is a reverse engineering framework that provides lots features we'll find invaluable, including disassembly, execution flow graphing, function and string analysis, and more. You can either install the most current version by cloning the git repo, or you can use a package manager (keep in mind that the version in the apt repository is quite a bit older than the git repo version; however, I used the apt repo's version for this challenge and had no issues).

<i>GDB-PEDA</i>

https://github.com/longld/peda

This is a plugin for GDB that makes reverse engineering and exploit development a much smoother experience than you might have with vanilla GDB. Of particular note is the fact that PEDA displays the state of the registers and stack after every step, and displays the recent and soon-to-be-executed assembly instructions.


<h3>Setup and getting started:</h3>

After downloading the 32-bit version of the binary bomb (which you can grab here: http://opensecuritytraining.info/IntroX86_files/bomb.tar), we can go ahead and untar it:

<code>
tar xvf bomb.tar
</code>

This should extract a single file, the bomb binary. Let's check it out:

<code>
reverse@debian:~/reversing/binary_bomb$ file bomb
bomb: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.0.0, not stripped
</code>


This tells us that it's a 32-bit binary and that it hasn't had its debugging symbols stripped out. This means that, when debugging the program, we should be able to see function names and other debugging information that might be helpful to us.

Next, let's go ahead and just run the bomb. Since we're not doing this assignment for a grade, and there's no server to log any failures, there's no punishment for causing the bomb to explode, so it won't hurt to see how it behaves.

<code>
reverse@debian:~/reversing/binary_bomb$ ./bomb 
Welcome to my fiendish little bomb. You have 6 phases with
which to blow yourself up. Have a nice day!
hello

BOOM!!!
The bomb has blown up.
</code>

![Alt text](/images/phase1_1.png?raw=true "First run of the bomb")


So the bomb runs, then waits for input. When I typed "hello", it then printed a message indicating that the bomb had exploded. Clearly, that wasn't the input the bomb was expecting. Now that we have a feel for the way the program behaves, let's start trying to reverse it.

<h3>Basic analysis with radare2:</h3>

To start analyzing this binary, let's open it up with radare2. To do that, type:

<code>
r2 bomb
</code>

After opening the program, we've got a command-line interface waiting for input. Our next step is to let r2 analyze the binary to find functions and strings, among other things. r2 has different levels of analysis depth; because this is a small binary, we'll analyze absolutely everything, which you can do with this command:

<code>
aaaa
</code>

<i>Tip: If you're ever unsure what commands you've got available, you can enter a "?" symbol. You can also do this partway through a command to see all the options; for example, if you wanted to see analysis options, you could enter "a?" to get a list of every command that begins with a.</i>


![Alt text](/images/phase1_2.png?raw=true "Analysis with r2")


After a brief moment, r2 finishes its analysis. It's worth noting that this analysis can take a very long time on larger binaries, and you might want to choose a more conservative level of analysis accordingly. However, this program is small enough that even a complete analysis like this only takes a few seconds.

Now that we've analyzed the binary, a sensible next step is to examine all of the functions that r2 uncovered. This can be done with the command:

<code>
afl
</code>

![Alt text](/images/phase1_3.png?raw=true "Function list from r2")

The output will contain lots of functions names with "sym." prepended to them. (The "sym." is something r2 automatically prepends; later, when we use a debugger, that won't be part of any of the function names.) Look through your output and take note of functions with interesting names. A few that stand out are various "phase_" functions, the "explode_bomb" function, and the main() function. To continue our analysis, let's take a look at the main function. To do this, r2 needs to seek to that function. You can seek to a function or address with the syntax "s function_name_or_address". So to go to main, type:

<code>
s sym.main
</code>

The address shown in your command-line should change to be 0x080489b0, the load address of main(). Now that we're in main(), let's disassemble it. The syntax to disassemble the current function is:

<code>
pdf
</code>

![Alt text](/images/phase1_4.png?raw=true "Disassembled main function")


We've now got a nice view of the assembly code that makes up the main() function. One helpful feature of r2 is that it draws arrows to indicate exactly where various jump instructions end up, which makes the code easier to follow. It'll also show strings that are being used and sometimes convert values being used in comparisons and such. Take some time to read over the assembly and get a feel for it. Even if you haven't looked at much assembly before, the names of the functions called should give you an idea of what's going on. I won't replicate all the assembly here, but consider this chunk:

<blockquote>
|     ``--> 0x08048a30      e82b070000     call sym.initialize_bomb  <br/>
|           0x08048a35      83c4f4         add esp, -0xc  <br/>
|           0x08048a38      6860960408     push str.Welcome_to_my_fiendish_little_bomb._You_have_6_phases_with_n ;  <br/> str.Welcome_to_my_fiendish_little_bomb._You_have_6_phases_with_n ; "Welcome to my fiendish little bomb. You have 6 phases with."   @ 0x8049660 ; size_t nbyte  <br/>
|           0x08048a3d      e8cefdffff     call sym.imp.printf        ; int printf(const char *format);  <br/>
|           0x08048a42      83c4f4         add esp, -0xc  <br/>
|           0x08048a45      68a0960408     push str.which_to_blow_yourself_up._Have_a_nice_day__n ;  <br/> str.which_to_blow_yourself_up._Have_a_nice_day__n ; "which to blow yourself up. Have a nice day!." @ 0x80496a0 ; int fildes  <br/>
|           0x08048a4a      e8c1fdffff     call sym.imp.printf        ; int printf(const char *format);  <br/>
|           0x08048a4f      83c420         add esp, 0x20  <br/>
|           0x08048a52      e8a5070000     call sym.read_line         ; ssize_t read(int fildes, void *buf, size_t nbyte);  <br/>
|           0x08048a57      83c4f4         add esp, -0xc  <br/>
|           0x08048a5a      50             push eax                    ; size_t nbyte  <br/>
|           0x08048a5b      e8c0000000     call sym.phase_1  <br/>
|           0x08048a60      e8c70a0000     call sym.phase_defused  <br/>
</blockquote>


We've got a call to initialize_bomb, and then the string we saw when we started the bomb gets pushed onto the stack. Then there's a call to printf(), which is probably printing that string on the stack. The same process happens a second time with a new string, and then there's a call to read_line(). Remember how the program waited for our input after printing its greeting? That's probably the function that processed our input. 

Then, most interesting of all, there's a call to phase_1. Immediately afterward, there's a call to phase_defused. Based on this, we can make an educated guess that the phase_1 function expects a particular type of input from the user, and if the function returns successfully, the very next instruction will show that we defused that phase. If the function doesn't return successfully, we've already seen what happens -- the bomb explodes.

The next logical step, then, is to check out what's going on in the phase_1 function. Let's seek to that.

<code>
s sym.phase_1
</code>

Now we can print the disassembled function; once again, the syntax is:

<code>
pdf
</code>

![Alt text](/images/phase1_5.png?raw=true "Disassembled phase_1 function")


This function isn't particularly large. After the stack prologue, these lines look most interesting:

<blockquote>
|           0x08048b2c      68c0970408     push str.Public_speaking_is_very_easy. ; str.Public_speaking_is_very_easy. ; "Public speaking is very easy." @ 0x80497c0 <br/>
|           0x08048b31      50             push eax                    ; long double x <br/>
|           0x08048b32      e8f9040000     call sym.strings_not_equal <br/>
|           0x08048b37      83c410         add esp, 0x10 <br/>
|           0x08048b3a      85c0           test eax, eax <br/>
|       ,=< 0x08048b3c      7405           je 0x8048b43 <br/>
|       |   0x08048b3e      e8b9090000     call sym.explode_bomb      ; long double expl(long double x); <br/>
|       `-> 0x08048b43      89ec           mov esp, ebp <br/>
</blockquote>


It looks like the string "Public speaking is very easy." is pushed onto the stack, then placed in EAX on the next line. Next, a function called strings_not_equal gets called. The next interesting line is the <i>test eax, eax</i> instruction. This instruction basically is the equivalent of <i>cmp eax,0</i> and is to determine if EAX now has a zero value. If it does, a jump is taken; otherwise, the explode_bomb function is called.

Even if you're not totally clear on what some of these instructions are doing, at a high level, it appears that a specific string is being used for something, then a strings_not_equal function is being called, and then there's a condition that needs to be met in order to jump over the explode_bomb function. Obviously, we want to avoid having that function get called, since if the bomb explodes we have the wrong answer and will have to try again. Armed with this knowledge, let's move on from static analysis and try some simple dynamic analysis -- that is, let's check out what's going on with a debugger.

<h3>Dynamic analysis using GDB-PEDA:</h3>

The advantage of using a debugger is that we can inspect exactly what the program is doing, line by line, pausing execution whenever we want to inspect the state of registers. As with radare2, it's possible to disassemble functions and view the assembly instructions as they're executed, and it's possible to find out exactly what values are held in memory addresses at various points in time. 

For this first phase, we're mostly interested in inspecting a few specific instructions and viewing the contents of registers at some specific points in time. To begin debugging the bomb, run the following command:

<code>
gdb ./bomb
</code>

This will open the program in a debugger, but won't begin running it. This is because we'll want to place breakpoints (points at which program execution is paused and the debugger waits for user interaction before continuing) before we start running the program. Since we're interested in checking out phase_1, let's set a breakpoint there with the following syntax:

<code>
break phase_1
</code>

![Alt text](/images/phase1_6.png?raw=true "Setting a breakpoint")


Now that we have a breakpoint set, we can begin execution. To do this, simply type "run" or "r" at the GDB prompt.

<code>
run
</code>

Your output should look like this:
<code>
gdb-peda$ run
Starting program: /home/reverse/reversing/binary_bomb/bomb 
Welcome to my fiendish little bomb. You have 6 phases with
which to blow yourself up. Have a nice day!
</code>


The program should just sit there now. We haven't actually hit a breakpoint yet; this is the first occurrence of the program calling the read_line function. This function is probably using scanf() or a similar C function to read in our input. We could reverse the read_line function and find out for sure, but for now let's just choose some input to provide. How about "Public speaking is very easy.", which was the string we saw in r2 when disassembling the phase_1 function? Clearly that string was important for some reason. So let's enter that:

<code>
Public speaking is very easy.
</code>

Immediately after entering this and hitting enter, the program should encounter the breakpoint we set.


![Alt text](/images/phase1_7.png?raw=true "Reaching the breakpoint")

We can see the current state of the registers at the top of the screen, the current assembly instruction being executed in the center (as well as a few of the upcoming and previous instructions), and the stack at the bottom. Of note is the fact that the EAX register currently holds the value "Public speaking is very easy.", which is the input we just provided. EAX is used to hold the return values of functions, so if the read_line function returns user input, that's how the string ended up there.

Next, let's single-step through the function. This will continue the program's exeuction by one instruction at a time, allowing us to inspect the registers and stack after every step. The instruction highlighted in bright green is the one where execution has been paused; when a single step is issued, the highlighted instruction will be executed. To issue a single step, type:

<code>
s
</code>

Doing this should move from this instruction:
0x8048b26 <phase_1+6>:	mov    eax,DWORD PTR [ebp+0x8]

To this one:
0x8048b29 <phase_1+9>:	add    esp,0xfffffff8

Let's step forward again to reach this:
0x8048b2c <phase_1+12>:	push   0x80497c0

From the r2 analysis, we know that this pushes a string onto the stack. Single-step again to the next instruction and we should see the results of the <i>push 0x80497c0</i> instruction:

![Alt text](/images/phase1_8.png?raw=true "String push")

As you can see in the stack display, the string "Public speaking is very easy." now resides in the stack in two different places; one of them is the same one that held the string previously, because it's where our input during the read_line function was placed. The second occurrence appears at the address at the top of the stack display, 0xbffff2b4. Single-step again to execute the <i>push eax</i> instruction and reach (but not execute) this instruction:
0x8048b32 <phase_1+18>:	call   0x8049030 <strings_not_equal>

The next single step we issue will cause the function to call the strings_not_equal function, which means we'll jump into that and step through it until it returns. When it does return, we'll arrive at phase_1+23, or:
0x8048b37 <phase_1+23>:	add    esp,0x10

We could step through the strings_not_equal function and try to reverse it as well, but before we go to such lengths, let's just see what the state of the program is after that function returns. To do this, we'll make use of another breakpoint. We're going to set the breakpoint at phase_1+23 (the instruction immediately after the strings_not_equal function returns), then tell GDB to continue execution. This means that the program will just run as normal until it hits our next breakpoint. This is a useful way of pausing execution right before and after function calls without having to manually step through everything in every called function.

To set our new breakpoint, type:
break *phase_1+23

<i>Tip: If you're not setting a breakpoint directly at the start of a named function (like phase_1 or main), you need to use an asterisk (*) right before your breakpoint location. Basically, if you're setting a breakpoint at a specific offset within a function or if you're breaking at a specific memory address, you need to use an asterisk.</i>

With a new breakpoint set, type "continue" or just "c" to continue execution:

<code>
c
</code>

<i>Tip: The "continue" and "run" commands are NOT the same! "Continue" resumes execution from your current location. "Run" starts the program over from the very beginning. If you have several breakpoints set up and don't want to single step through everything between them, make sure you use "continue", not "run".</i>

![Alt text](/images/phase1_9.png?raw=true "Continuing execution")

As you can see in the screenshot, we've now reached our breakpoint. Interestingly, the value in EAX is no longer our input; now it's just 0x0. Probably the strings_not_equal function compares the string we provided with something one byte at a time, and if each byte matches, that byte gets removed from the register. If every byte matched, then all of the string bytes would've been removed from EAX, leaving nothing, aka 0x0. This is a routine we'll observe more of in later phases, so if that's confusing to you right now, don't worry. You could also inspect the strings_not_equal function yourself to see if this theory is correct, since it's just a guess right now. 

For now, let's keep single-stepping through the phase_1 function. We're nearly done with it. Issue a single step to move through the <i>add esp,0x10</i> instruction and reach <i>test eax,eax</i>. Recall that earlier I said that this check is equivalent to <i>cmp eax,0</i>, and is just a little bit trickier to read. In other words, this compares the value in EAX with the value 0x0. Looking at the current state of EAX in GDB, we can see this:

EAX: 0x0

So EAX is equal to 0. What happens next? First, single step through this instruction to reach the <i>je 0x8048b43 <phase_1+35></i> instruction. 

![Alt text](/images/phase1_10.png?raw=true "phase_1+35")


Here we see another wonderful feature of PEDA, which is the text near the bottom of the middle "panel" (the code section) that says "JUMP is taken". Whenever a jmp-type instruction is encountered, we'll know if it'll be taken or not before single stepping, which can be nice to get at-a-glance information without having to do as much calculation ourselves.

In case you're not familiar, the instruction "je" means "jump if equal" and is based on the previous instruction's results. In this case, the je instruction is looking at the results of test eax,eax and saying "if the results of <i>test eax,eax</i> (aka <i>cmp eax,0</i>) were equal (so if EAX was equal to 0), then go ahead and perform this jump. Otherwise, just keep moving on to the next instruction like normal". If the jump didn't get taken, the very next instruction would be a call to the explode_bomb function, which is obviously bad. However, the jump is being taken!

That means that we'll circumvent the bomb explosion and the phase_1 function will return successfully. You can probably already guess what this means, but let's go ahead and step through the rest of this function anyway. Keep stepping until you've reached and executed the ret instruction, which ends the function and returns to the calling function, which in this case is main(). 

Notice what the next instruction in main() to be executed is? 
0x8048a60 <main+176>:	call   0x804952c <phase_defused>

That must mean we've defused this phase! Go ahead and continue execution of the program with "c" to see what happens.

<code>
gdb-peda$ c
Continuing.
Phase 1 defused. How about the next one?
</code>

We did it! The defusal key for the first phase is the string "Public speaking is very easy." (without quotes). 

<h3>Conclusion:</h3>

The writeup for this phase could've basically been boiled down to "We see a string get pushed onto the stack and then some stuff gets compared. Let's try punching in that string and see what happens. Oh, it worked!" However, I wanted to delve a little more into the process and tools we'll be using throughout the remaining phases. The writeups for the other phases will probably be less verbose and more focused only on the salient steps to solving the challenge.
