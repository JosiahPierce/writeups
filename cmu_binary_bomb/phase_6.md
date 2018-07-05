We've finally made it to the sixth and final main phase of the binary bomb. As you'd expect, this phase is the most complex and can involve quite a bit of trial and error. Therefore, we'll focus mostly on the steps needed to actually solve this phase, rather than cover all the experimentation that might take place to eventually get to the answer. As always, be sure to have the previous defusal codes handy:

<i>Phase 1</i>: Public speaking is very easy.<br>
<i>Phase 2</i>: 1 2 6 24 120 720<br>
<i>Phase 3</i>: 7 b 524<br>
<i>Phase 4</i>: 9<br>
<i>Phase 5</i>: opekma<br>

<b>Static analysis</b>

In radare2, seek to phase_6 and disassemble it:<br>

<code>
s sym.phase_6<br>
pdf<br>
</code>

![Alt text](/images/phase6_1.png?raw=true "Disassembled phase_6")


Wow! This phase contains a lot more instructions than anything we've looked at previously. What useful information can we see here? Well, very early on in the phase, there's this function call:<br>

<code>
0x08048db3      e820020000     call sym.read_six_numbers  ; ssize_t read(int fildes, void *buf, size_t nbyte);
</code>


As a reminder, we've seen this read_six_numbers function before in a previous phase. This function expects six integers separated by spaces. That's what our input should be for this phase. What else can we analyze? This chunk is interesting:<br>

<code>
0x08048dc6      48             dec eax<br>
  
0x08048dc7      83f805         cmp eax, 5<br>

0x08048dca      7605           jbe 0x8048dd1<br>

0x08048dcc      e82b070000     call sym.explode_bomb<br>
</code>


Looks like the value of EAX is being decremented (<i>dec eax</i> instruction), and then EAX is being compared to 5. Then there's a "jump if below or equal" instruction (<i>jbe 0x8048dd1</i>), and if this jump is not taken, then the explode_bomb function is called. 

What does this tell us? You're encouraged to do some experimentation with your input here during dynamic analysis and see this more in-depth, but the idea is that none of the integers we provide as input can be 0s. Why is that? Because in this case, if an integer equal to 0 is decremented, it will "wrap around" to a massive number, causing it to be far larger than 5 and fail the jump check. These instructions actually tell us a lot about the range of numbers we can provide; we can only provide integers 1 through 6 (because when 6 is decremented, it will be equal to 5, allowing the jump to still be taken). At 7, the decremented value will be 6 and therefore too large to pass the jump check, resulting in the explode_bomb function being called. That helps significantly narrow down the range of input we'll need to provide. 

The rest of the disassembly looks quite tricky to analyze statically, so now it's time to move over to dynamic analysis.

<b>Dynamic analysis</b>

Fire up GDB and set a breakpoint at phase_6. Then, run the bomb and submit the defusal codes until prompted for the input for phase_6:<br>

![Alt text](/images/phase6_2.png?raw=true "Phase_6 input")


For our initial input, let's try:<br>

<code>
1 2 3 4 5 6<br>
</code>

After entering that, we should hit our first breakpoint. Our next step is to figure out what we'd like to examine in greater detail. We can then set up some breakpoints accordingly. Here are a couple of instructions that seem like good breakpoint candidates:<br>

<code>
0x08048e34 <+156>:	cmp    ebx,eax
</code>

This instruction looks like it's part of some small loop, because there's a <i>jl</i> instruction immediately following this one, and if that jump is taken, it'll jump back to phase_6+152. That loop might be interesting to us, so we'll want a breakpoint here.<br>

<code>
0x08048e3f <+167>:	cmp    edi,0x5
</code>

This instruction also looks like it's part of another loop. We'll want a breakpoint here, too.<br>

<code>
0x08048e5b <+195>:	cmp    edi,0x5
</code>

Perhaps this instruction is part of a second loop that's similar to the one at phase_6+167? This is another good spot for a breakpoint.

<code>
0x08048e75 <+221>:	cmp    eax,DWORD PTR [edx]
</code>

This occurs before the last potential call to explode_bomb in the phase_6 function. Given that this cmp features EAX, there's a good chance that this is where the input we've provided is compared against the correct value. Therefore, this is where we'll set our final breakpoint. Now that we've got all of those figured out, let's go ahead and set them:<br>

<code>
gdb-peda$ break *phase_6+156<br>
Breakpoint 2 at 0x8048e34<br>
gdb-peda$ break *phase_6+167<br>
Breakpoint 3 at 0x8048e3f<br>
gdb-peda$ break *phase_6+195<br>
Breakpoint 4 at 0x8048e5b<br>
gdb-peda$ break *phase_6+221<br>
Breakpoint 5 at 0x8048e75<br>
</code>

Continue exeuction so that we can advance to the next breakpoint.

![Alt text](/images/phase6_3.png?raw=true "First breakpoint")



EDI is currently set to 0x1. Single-step to discover, as we'd guess, that the <i>jle</i> instruction is taken. Since that jump goes backward in the function, just continue execution again. 

![Alt text](/images/phase6_4.png?raw=true "cmp ebx,eax")


We've now reached our breakpoint at this instruction:<br>

<code>
0x8048e34 <phase_6+156>:	cmp    ebx,eax
</code>

As GDB tells us, EAX and EBX are both currently set to 0x2. Go ahead and continue execution. We'll hit phase_6+167 for the second time now; notice that this time, EDI is equal to 0x2. Looks like our initial guess was correct; this is a loop that continues jumping back until EDI is equal to 0x6. Follow the same process of continuing execution until you reach phase_6+167 and EDI is equal to 0x6. When you do this, you'll notice that there's a loop ongoing at phase_6+156 that sometimes requires a few iterations to satisfy the <i>cmp ebx,eax</i> condition. 

When you reach phase_6+167 and EDI ix equal to 0x6, single-step once to confirm that this time, the <i>jle</i> isn't taken. Then continue execution to reach:<br>

<code>
0x8048e5b <phase_6+195>:	cmp    edi,0x5
</code>

![Alt text](/images/phase6_5.png?raw=true "New EAX value")


Notice that EAX is now equal to 0x2d5. 0x2d5 converts to the decimal value 725. Clearly, that's not the input we provided; however, like we saw in the last phase, it's possible that our input has somehow been converted before reaching this stage. EDI is currently set to 0x2, so continue execution in order to loop once. EAX now contains 0x12d, which in decimal is 301. Maybe each number we provided has been converted to a different value? Let's keep going through the loop until EDI is equal to 0x6, but on each loop, record what EAX is set to. Also notice that when we hit this cmp for the first time, EDI was already 0x2. If each number we provided is converted to a new value, then there's one we won't see here (we'll only see five converted values, not all six). 

As you continue and record execution, here are each of the values you should come up with and their decimal equivalents (including the two we've already seen):<br>

0x2d5 -- 725<br>
0x12d -- 301<br>
0x3e5 -- 997<br>
0xd4 -- 212<br>
0x1b0 -- 432<br>

EDI should now be equal to 0x6. Go ahead and single-step once to confirm that the <i>jle</i> isn't taken this time. Then continue execution to hit the final breakpoint we set up:<br>

<code>
0x8048e75 <phase_6+221>:	cmp    eax,DWORD PTR [edx]
</code>

![Alt text](/images/phase6_6.png?raw=true "Final breakpoint")


First, we see that EAX is currently equal to 0xfd. We didn't see that value before; maybe that's the one we missed? 0xfd is 253 in decimal. Secondly, look at the value of EDX: it's 0x2d5, which is a value we've seen before -- it was the very first one to show up in that previous loop. That <i>cmp eax,DWORD PTR [edx]</i> instruction is comparing the values in the two registers. Immediately afterward, there's a <i>jge</i> instruction; if it's taken, then execution will continue. If not, then the explode_bomb function is called. Our EAX value is much lower than the value in EDX, so the bomb is going to explode if we continue.

What can we deduce from this? Well, it looks like each of our integers we provided as input is converted to a specific hex value. When we reach this comparison stage, the value in EAX (which contains the converted value of the integer we provided) needs to be <i>larger</i> than the value in EDX, which seems to be the converted value of the <i>next</i> integer we provided. This means that none of our integers can be repeat numbers, and our input needs to make them appear in order from greatest converted value to least converted value. Let's go back to our chart, and let's try to figure out which numbers we provided correspond to which converted values:

Input:  Converted:  Decimal:  <br>
1		0xfd		253
2		0x2d5	725
3		0x12d	301
4		0x3e5	997
5		0xd4	212
6		0x1b0	432

We can guess that 0xfd corresponds to 1, because it's the very first value in EAX during this final comparison stage. If we're right, then each of the other values we saw should correspond to our remaining five integers in the order they appeared. What's our greatest-to-least converted value order look like?

4 2 6 3 1 5

Go ahead and exit GDB and run the bomb, providing that input:<br>

![Alt text](/images/phase6_7.png?raw=true "Solving the bomb")


<code>
reverse@debian:~/reversing/binary_bomb$ ./bomb<br>
Welcome to my fiendish little bomb. You have 6 phases with<br>
which to blow yourself up. Have a nice day!<br>
Public speaking is very easy.<br>
Phase 1 defused. How about the next one?<br>
1 2 6 24 120 720<br>
That's number 2.  Keep going!<br>
7 b 524<br>
Halfway there!<br>
9<br>
So you got that one.  Try this one.<br>
opekma<br>
Good work!  On to the next...<br>
4 2 6 3 1 5<br>
Congratulations! You've defused the bomb!<br>
</code>

That's it! We've finally defused the bomb. I tried to keep this phase's writeup focused almost entirely on the steps that actually work for finding the solution; when I originally did this, I spent quite a while with trial-and-error, eventually noticing the pattern with the converted number values.

We're now officially done with all of the main phases of the bomb, but we're actually not done with the bomb itself. It just so happens that there's a secret phase for the bomb; it's optional, but it's fun and provides some more opporutnities for us to hone our reversing skills, so let's tackle that as well. We'll check it out in the next section.

