For this phase, we'll once again place a heavier emphasis on dynamic analysis. I found that this was also a phase that seemed easiest to solve by experimenting with inputs and observing changes in behavior. As these phases increase in complexity, such experimentation seems to more and more become a necessary part of the reverse engineering process. Before we get started, grab your defusal codes for the previous four phases:

<i>Phase 1</i>: Public speaking is very easy.<br>
<i>Phase 2</i>: 1 2 6 24 120 720<br>
<i>Phase 3</i>: 7 b 524<br>
<i>Phase 4</i>: 9<br>

<b>Static analysis</b>

Just like always, we'll kick things off by disassembling the relevant phase function. Seek to phase 5 and disassemble it:

<code>
s sym.phase_5  <br/>
pdf  <br/>
</code>

![Alt text](/images/phase5_1.png?raw=true "Disassembled phase_5")

There are a few interesting sections here. The first is the call to string_length, followed shortly after by a <i>cmp eax,6</i> instruction and a <i>je</i> instruction that will circumvent a call to explode_bomb. That tells us that probably our input is expected to be 6 bytes in length. 

Next, we've got this:  <br/>

<code>
0x08048d52      be20b20408     mov esi, str.isrveawhobpnutfg ; "isrveawhobpnutfg.." @ 0x804b220  <br/>
</code>

So some odd string is being placed in the ESI register, followed by some instructions that make up most of the middle of phase_5. That might be something to investigate further. 

Lastly, there's this whole chunk:  <br/>
<code>
0x08048d72      680b980408     push str.giants ; str.giants ; "giants" @ 0x804980b  <br/>
   
0x08048d77      8d45f8         lea eax, dword [ebp - local_8h]  <br/>

0x08048d7a      50             push eax                    ; long double x  <br/>

0x08048d7b      e8b0020000     call sym.strings_not_equal  <br/>

0x08048d80      83c410         add esp, 0x10  <br/>

0x08048d83      85c0           test eax, eax  <br/>

</code>

So the string "giants" is pushed onto the stack, and then a function called strings_not_equal is called. After that, there's a <i>test eax,eax</i> instruction. Right after this chunk there's a <i>je</i> instruction; if it's taken, then a second explode_bomb call is circumvented, and the phase_5 function should return successfully. If it's not taken, then the bomb will explode. At a guess, perhaps user input is being compared against the string "giants" by calling the strings_not_equal function? The results are then placed in EAX, and if EAX is 0 (don't forget that <i>test eax,eax</i> is equivalent to <i>cmp eax,0</i>, then the <i>je</i> will be taken. EAX is probably set to 0 if the strings compared are equal, then, and it's probably set to 1 if they aren't.

Now that we've performed cursory static analysis, we can make some reasonable educated guesses about what the phase expects from the user and how we might be able to complete it. However, we haven't reversed everything in this function -- remember that middle section we skipped over? The rest of this phase will probably be easier to reverse via dynamic analysis, so let's jump into that.

<b>Dynamic analysis</b>

Go ahead and launch the bomb in GDB, setting a breakpoint at phase_5. Run the bomb and provide the defusal answers until prompted for the phase_5 input:  <br/>

![Alt text](/images/phase5_2.png?raw=true "Running the bomb")

<code>
gdb-peda$ break phase_5  <br/>
Breakpoint 1 at 0x8048d34  <br/>
gdb-peda$ r  <br/>
Starting program: /home/reverse/reversing/binary_bomb/bomb   <br/>
Welcome to my fiendish little bomb. You have 6 phases with  <br/>
which to blow yourself up. Have a nice day!  <br/>  
Public speaking is very easy.  <br/>  
Phase 1 defused. How about the next one?  <br/>  
1 2 6 24 120 720  <br/>  
That's number 2.  Keep going!  <br/>  
7 b 524  <br/>  
Halfway there!  <br/>  
9  <br/>  
So you got that one.  Try this one.  <br/>  
</code>

For our input for phase_5, let's try "giants". We know that the program expects a 6-byte string, and that "giants" is eventually pushed onto the stack, so probably that's what our input needs to match. 

After providing input and hitting enter, execution should continue until hitting our breakpoint at phase_5. There are a couple of things we might want to check out; we'll want a breakpoint here:  <br/>
<code>
   0x08048d43 <+23>:	cmp    eax,0x6
</code>

We'll want to confirm that the string_length function did convert our input to its length and store the result in EAX. That seems very likely, but it can't hurt to be sure.   <br/>

<code>
   0x08048d7b <+79>:	call   0x8049030 <strings_not_equal>
</code>

It will be helpful to see our input right before strings_not_equal places a return value into EAX. Lastly, we'll want a breakpoint here:  <br/>

<code>
   0x08048d69 <+61>:	jle    0x8048d57 <phase_5+43>
</code>

This is part of what appears to be a loop in that middle chunk of instructions that we haven't investigated much. How do we know this is a loop? The <i>jle</i> instruction will keep going back to a certain part of the phase_5 function (phase_5+43, specifically) until a specific condition is met. We'll be single-stepping through that middle section to understand what's going on there, but having a breakpoint set at that instruction will remind us how many iterations of the loop have occurred. Go ahead and set those breakpoints:  <br/>

<code>
gdb-peda$ break *phase_5+23  <br/>  
Breakpoint 2 at 0x8048d43  <br/>  
gdb-peda$ break *phase_5+79  <br/>   
Breakpoint 3 at 0x8048d7b  <br/>  
gdb-peda$ break *phase_5+61  <br/>   
Breakpoint 4 at 0x8048d69  <br/>   
</code>

Now continue execution, landing on our next breakpoint.

![Alt text](/images/phase5_3.png?raw=true "cmp eax,6")


Notice that EAX now contains 0x6. Our guess was correct; a 6-byte string is expected, so we've found the correct length. Take two single-steps to take the jump and arrive here:  <br/>

<code>
0x8048d4d <phase_5+33>:	xor    edx,edx
</code>

This is the beginning of the section we're most interested in. For context, here's the whole block we want to investigate:  <br/>

<code>
0x08048d4d <+33>:	xor    edx,edx  <br/>
   0x08048d4f <+35>:	lea    ecx,[ebp-0x8]  <br/>
   0x08048d52 <+38>:	mov    esi,0x804b220  <br/>
   0x08048d57 <+43>:	mov    al,BYTE PTR [edx+ebx*1]  <br/>
   0x08048d5a <+46>:	and    al,0xf  <br/>
   0x08048d5c <+48>:	movsx  eax,al  <br/>
   0x08048d5f <+51>:	mov    al,BYTE PTR [eax+esi*1]  <br/>
   0x08048d62 <+54>:	mov    BYTE PTR [edx+ecx*1],al  <br/>
   0x08048d65 <+57>:	inc    edx  <br/>
   0x08048d66 <+58>:	cmp    edx,0x5  <br/>
   0x08048d69 <+61>:	jle    0x8048d57 <phase_5+43>  <br/>
</code>

Let's just single-step through that up to the <i>jle</i> instruction and look for anything interesting.

![Alt text](/images/phase5_4.png?raw=true "Start of loop")

Upon reaching phase_5+43, notice that the unusual string we noticed is now held in ESI; specifically, its contents are now <i>ESI: 0x804b220 ("isrveawhobpnutfg\260\001")</i>.


On the very next instruction, notice what's held in EAX:  <br/>

<code>
EAX: 0x67 ('g')
</code>

Also important is the fact that our full input string is being held in EBX. Since only the first letter of our input is currently in EAX, perhaps this loop does something to our input letter-by-letter? Single-step again to find that EAX changes to 0x7. Single-step twice more to reach this instruction:  <br/>  

<code>
0x8048d62 <phase_5+54>:	mov    BYTE PTR [edx+ecx*1],a
</code>

![Alt text](/images/phase5_5.png?raw=true "Letter value conversion")

Notice that EAX now holds "h". Hang on - where is "h" coming from? That's not found anywhere in our input. Could it be possible that each letter in our input is being converted to a different letter? Single-step three more times to reach the <i>jle</i> instruction (which is taken). EDX is currently equal to 0x1, and we need it to be 0x5 before the jump won't be taken and execution will move beyond the loop. That reinforces our theory that this loop iterates over each letter we provided. Let's single-step two more times, reaching this:  <br/>

<code>
0x8048d5a <phase_5+46>:	and    al,0xf
</code>

Notice that EAX now holds "i"? That tracks with what we think is going on; it's the second letter we provided. To confirm our theory that each letter is confirmed to something else, go ahead and just provide the "c" command to continue execution until a breakpoint is hit. This will reach the <i>jle</i> instruction again, allowing us to inspect the letter held in EAX.

![Alt text](/images/phase5_6.png?raw=true "Next loop iteration")

EAX now holds "b". Now that we've got a good idea of what's going on, keep continuing execution, hitting this breakpoint each time, until the loop is complete and execution hits our breakpoint here:  <br/>

<code>
0x8048d7b <phase_5+79>:	call   0x8049030 <strings_not_equal>
</code>

![Alt text](/images/phase5_7.png?raw=true "Final register values")


Now look at the EAX and EBX registers:  <br/>

<code>
EAX: 0xbffff2c0 ("hbsfev")  <br/>
EBX: 0x804b7c0 ("giants")  <br/>  
</code>

Here we see what each letter of our input was ultimately converted to; obviously, the upcoming comparison with the literal string "giants" is going to fail. However, what if we were to try other 6-letter inputs until we found the letters that convert to the ones we want to use? For example, we've already got one: the "a" in "giants" ended up being converted to "s", as we can see in EAX. Our final input will need to feature an "a" as the final character, since it'll be converted to the character we want for the comparison.

This process is slow and painstaking, but your goal should be to try other letters in your input and observe what they're converted to. Create a chart of the original letters and their converted values. For this first run, here's what the chart would look like:

g: h  <br/>
i: b  <br/>
a: s  <br/>
n: f  <br/>
t: e  <br/>
s: v  <br/>

Becuase the rest of this is just trial and error, I'll leave it as an exercise for the reader. However, below you can find the final defusal code to finish this phase:  <br/>

<code>
opekma
</code>

![Alt text](/images/phase5_8.png?raw=true "Completing phase 5")


Great! Just one "main" phase left (though there's still an extra surprise in store). Let's head to phase 6!
