If you carefully combed through all of the functions that r2 found during analysis of the binary, you might have noticed that there's a function called secret_phase. As far as I could tell, this phase was never called during a normal run of the program. Therefore, solving this phase isn't required to complete the bomb; however, we've got a chance for extra credit here, so let's give it a shot! 

Before we get started, there's the obvious question: how do we go about solving a phase function that's never actually called? The static analysis portion will be exactly the same as all of the previous phases -- r2 can analyze this function just as easily as any other, whether it's called or not. However, when the time comes for dynamic analysis, the phase isn't going to be called during a normal run. We have two options to work around this: we can either use GDB to jump execution to the secret_phase function and continue from there, or we can use a new technique that we haven't needed for any of these other phases, which is patching the binary itself. I opted for the patching option to get a bit more practice with r2's patching capabilities. After we finish up with static analysis, we'll patch the binary and then move on to our standard dynamic analysis. Let's get to work!


<b>Static analysis</b>

In radare2, seek to the secret_phase function and disassemble it.

![Alt text](/images/secrephase_1.png?raw=true "Disassembled secret_phase")


First off, we notice that this phase is calling the read_line function. Normally, that function was called outside of the phase functions, but since the secret phase isn't normally called, all of the functions necessary to construct a full phase will need to be self-contained. Similarly, at the end of the secret phase, the phase_defused function is called. This is good news, since it means that when we get around to patching the binary, we won't have to patch several different function calls in to get the phase to work properly.

As far as the actual function logic, early on there's a <i>call sym.imp.__strtol_internal</i> instruction. That's an unusual function name, and it's not something we've seen before. That could be something to investigate further.

Then there are these two instructions:<br>

<code>
0x08048f08      3de8030000     cmp eax, 0x3e8<br>

0x08048f0d      7605           jbe 0x8048f14<br>
</code>

EAX is compared with 0x3e8, which is 1000 in decimal. If EAX is below or equal to 1000, then a jump is taken. Otherwise, explode_bomb is called. This indicates that our input will probably need to be a number that is less than or equal to 1000. This chunk of instructions found slightly later in the function also sticks out:<br>

<code>
0x08048f1d      e872ffffff     call sym.fun7<br>

0x08048f22      83c410         add esp, 0x10<br>

0x08048f25      83f807         cmp eax, 7<br>

0x08048f28      7405           je 0x8048f2f<br>
</code>

A function called fun7 is called. 0x10 is added to ESP, and then EAX is compared with 7. If it's equal, a call to explode_bomb is circumvented, and the phase should be defused. If it's not equal to 7, then the bomb explodes. This should indicate that some kind of modification is being performed on the input we provided, probably during the fun7 function. Let's take a quick look at the fun7 function in r2 and see what stands out.

<code>
s sym.fun7<br>

pdf<br>
</code>

![Alt text](/images/secretphase_2.png?raw=true "Disassembled fun7")

This function is a little trickier to understand by performing purely static analysis, but it's clear that some operations are being performed on the EAX register that will probably change its value. The rest might be easier to figure out during dynamic analysis, so we'll move on to that. Before we do, though, we'll patch the binary to make dynamic analysis simpler.


<b>Patching the binary to call the secret_phase function</b>

Ordinarily, patching is discouraged in reverse engineering challenges, but keep in mind that we're only going to patch the binary in such a way that allows the function to be called; we're not going to patch the function itself to let us defuse the phase without having to actually solve it. (However, that's also something you might want to mess with on your own; it can be helpful to know how to do things like that!)

First, you'll want to copy the original bomb file and give it a new name:<br>

<code>
cp bomb bomb_patched<br>
</code>

Next, you'll want to open this new copied version in r2, and you'll want to include the "-w" flag (for write mode):<br>

<code>
r2 -w bomb_patched<br>
</code>

Since this is technically a new binary as far as r2 is concerned, go ahead and run full analysis on it again:

<code>
aaaa<br>
</code>

After a few seconds, that should complete. So, where are we going to patch in a call to secret_phase? We'll obviously want to place it somewhere in main(), so go ahead and seek to there and print the disassembly:<br>

<code>
s sym.main<br>

pdf<br>
</code>

![Alt text](/images/secretphase_3.png?raw=true "Disassembled main")


We'll want to call this phase after the bomb initialization steps and initial printed output, but probably before any of the main 6 bomb phases (after all, we've already solved those, so there's no real point dealing with them now). A good candidate for the instruction to patch is here:<br>

<code>
0x08048a52      e8a5070000     call sym.read_line<br>
</code>

This is the first occurrence of read_line, and was previously used to get input for phase_1. However, we don't need to get input for phase_1 anymore, since we're not solving it. We also know from our static analysis that secret_phase includes its own self-contained call to read_line, so this call isn't necessary for getting input for that function. Therefore, we can probably safely patch over this instruction. To begin this process, first seek to the address of the instruction we'll be overwriting with our patch:<br>

<code>
s 0x08048a52<br>
</code>

Next, enter visual mode by typing "Vp" and hitting enter:<br>

<code>
Vp<br>
</code>

![Alt text](/images/secretphase_4.png?raw=true "Visual mode")


Now you can enter assembler mode by typing "A" and hitting enter:<br>

<code>
A<br>
</code>

Now we can type a valid assembly instruction to replace the one at our current address. Since we just want to call the secret_phase function, enter this:<br>

<code>
call sym.secret_phase<br>
</code>

![Alt text](/images/secretphase_5.png?raw=true "Patching in a call to secret_phase")


Once you've finished typing a valid instruction (but before hitting enter), you can see that the instruction at our current address has been replaced with the one we typed. Hit "enter" twice to commit the changes. Then type "q" and hit enter to quit:<br>

<code>
q<br>
</code>

<b>Dynamic analysis</b>

Great! Now you'll need to exit r2 to run the bomb. Once you've closed it, go ahead and open the bomb in GDB, set a breakpoint at secret_phase, and try running the bomb. If all went well, execution should reach that breakpoint and pause, indicating that we successfully patched the binary to call the secret_phase function.

![Alt text](/images/secretphase_6.png?raw=true "Executing secret_phase")

Great! Now, what input should we try? Since we know that EAX needs to be equal to or less than 1000, let's just try 1000. Before we continue execution, though, we'll want to set up some breakpoints. Let's set three.We'll want one here:<br>

<code>
0x08048f08 <+32>:	cmp    eax,0x3e8<br>
</code>

This will let us look at the current value of EAX right before the cmp instruction. The second breakpoint will be here:<br>

<code>
0x08048f18 <+48>:	push   0x804b320<br>
</code>

This is the instruction that occurs immediately before the call to fun7, so it'll be good to pause here and see the state of the registers. Finally, we'll place a breakpoint here:<br>

<code>
0x08048f22 <+58>:	add    esp,0x10<br>
</code>

This is the instruction immediately <i>after</i> fun7. We should be able to see the results of any changes made by fun7. The rest of the function we can just single-step through. Go ahead and set all of those breakpoints:<br>

<code>
gdb-peda$ break *secret_phase+32<br>

Breakpoint 2 at 0x8048f08<br>

gdb-peda$ break *secret_phase+48<br>

Breakpoint 3 at 0x8048f18<br>

gdb-peda$ break *secret_phase+58<br>

Breakpoint 4 at 0x8048f22<br>
</code>

Now go ahead and continue execution, providing "1000" as input.

![Alt text](/images/secretphase_7.png?raw=true "Input")


We can see at the <i>cmp eax,0x3e8</i> instruction that EAX is currently equal to 0x3e7, which is 999 in decimal. Hmm...EAX must be getting decremented by that instruction right before this one:<br>

<code>
0x8048f05 <secret_phase+29>:	lea    eax,[ebx-0x1]<br>
</code>

This means that we could actually enter up to 1001 safely, since our input will be decremented by 1. Go ahead and continue execution. At the next breakpoint right before the call to fun7, EAX and EBX should be in this state:<br>

<code>
EAX: 0x3e7 <br>

EBX: 0x3e8 <br>
</code>

Continue execution again to see what state the registers are in after fun7 has been called and has returned.

![Alt text](/images/secretphase_8.png?raw=true "Registers after fun7 call")

EAX is now set to 0xfffffff7, which is 4294967287 in decimal. Why is EAX suddenly equal to this huge number? We can go through fun7 step-by-step if necessary, but it's obvious that our input has somehow been modified, perhaps by adding another large number to it. Before we go through the process of trying to understand fun7, though, let's see if we can get any quick wins by experimenting with our input a bit. Try re-running the binary, and this time choose an input of 10 instead of 1000. 

EAX will be decremented by one to reach 0x9. When you reach the breakpoint right before the <i>cmp eax,0x7</i> instruction, you'll see that EAX is equal to 0xfffffff2 this time. That's equivalent to 4294967282 in decimal. Hmm...the difference ebtween that and our original number is only 5, even though our inputs were very different numbers. However, providing a smaller number as input did ultimately end up with a smaller final value in EAX, so at least that behavior is as we'd expect. 

If you're familiar with some typical exploitation concepts or programmer errors, you might already have an idea of what's coming. Even if you're not, though, one thing you might want to check out is what happens when we choose the largest number available to us for input. Don't forget that, because EAX is decremented by 1 before it's checked to see if it's less than or equal to 1000, we can actually provide 1001 as input. How much will EAX change? Go ahead and re-run the binary one more time, providing 1001 as input.

![Alt text](/images/secretphase_9.png?raw=true "Input of 1001")

Hang on -- EAX is now equal to 0x7! How did that happen? This is due to a bug called an <b>integer overflow</b>, and you can read more about that here:<br>

https://en.wikipedia.org/wiki/Integer_overflow

One you've read that (especially the origin section, which explains the "wrapping" behavior integer overflows can exhibit), this solution should start to make more sense. Our input (an unsigned integer) was increased in size to be a massive number. The maximum size of an unsigned integer is 4294967295 (0xffffffff) (source: https://msdn.microsoft.com/en-us/library/296az74e.aspx). The final numbers we saw in EAX were very, very close to that limit. In fact, depending on how the math in the fun7 function worked out, increasing the size of our input integer by just a small amount could result in a large enough final number to trigger an integer overflow. 

As we know, an integer overflow can cause a "wrapping" effect, where a very large number will hit its limit and wrap around to very small values again, basically starting over. Our input was just large enough to cause this wrapping behavior, going from a giant number back to 0 and a little more, bringing up the final value in EAX to 7, which is enough to pass the comparison. Speaking of which, let's go ahead and try that input outside GDB and see what happens:<br>

![Alt text](/images/secretphase_10.png?raw=true "Completing secret_phase")

<code>
reverse@debian:~/reversing/binary_bomb$ ./bomb_patched <br>

Welcome to my fiendish little bomb. You have 6 phases with <br>

which to blow yourself up. Have a nice day!<br>

1001 <br>
Wow! You've defused the secret stage!<br>

Segmentation fault<br>
</code>

We did it! We've now completely solved the binary bomb. The segfault is caused by the fact that we patched the binary to call the function, but didn't do any work to ensure that the secret_phase function would gracefully return execution to main and keep the other phases running. That's fine, since we made a copy of the binary and only wanted to solve this secret phase. 

If you worked through all these challenges, congratulations! If you just stopped in for a quick look at the writeup, I hope you found it to be interesting and helpful. Either way, hopefully you learned something and enjoyed yourself. Thanks for reading!
