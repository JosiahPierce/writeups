Time to move on to phase 3. As a reminder, these are the defusal codes for phases 1 and 2:<br>
<i>Phase 1</i>: Public speaking is very easy. <br>
<i>Phase 2</i>: 1 2 6 24 120 720 <br>

<b>Static analysis</b>

You know the drill by now; let's first begin by taking a look at the disassembled phase_3 function. Go ahead and seek to phase_3 and print the disassembled function.

<code>
s sym.phase_3 <br>
pdf <br>
</code>

![Alt text](/images/phase3_1.png?raw=true "Disassembled phase_3")

The first line that appears to be of major significance to us is this one:

<code>
|           0x08048bb1      68de970408     push str._d__c__d ; str._d__c__d ; "%d %c %d" @ 0x80497de
</code>

Notice what's being pushed onto the stack: "%d %c %d"

After completing the last phase, you should recognize these as C format strings. We've seen %d before -- recall that it represents an integer. %c represents a single character. This is different from %s, which could be more than one character and instead represents a null-terminated string. (You can read more about this here: https://stackoverflow.com/questions/10846024/why-does-cs-printf-format-string-have-both-c-and-s)

This instruction gives us some helpful information about our expected input; specifically, we now know that we should submit an integer, single character, and second integer, with spaces separating each piece of input.

After that, this small chunk of assembly makes up the remaining interesting portion of the phase_3 function:

<code>
           0x08048bbf      83f802         cmp eax, 2 <br>
       ,=< 0x08048bc2      7f05           jg 0x8048bc9 <br>
       |   0x08048bc4      e833090000     call sym.explode_bomb      ; long double expl(long double x); <br>
       `-> 0x08048bc9      837df407       cmp dword [ebp - local_ch], 7 ; [0x7:4]=0 <br>
       ,=< 0x08048bcd      0f87b5000000   ja 0x8048c88 <br>
       |   0x08048bd3      8b45f4         mov eax, dword [ebp - local_ch] <br>
       |   0x08048bd6      ff2485e89704.  jmp dword [eax*4 + 0x80497e8] <br>
        |   0x08048bdd      8d7600         lea esi, dword [esi] <br>
        |   ; UNKNOWN XREF from 0x080497e8 (unk) <br>
        |   0x08048be0      b371           mov bl, 0x71                ; 'q' <br>
        |   0x08048be2      817dfc090300.  cmp dword [ebp - 4], 0x309  ; [0x309:4]=0x21000000 <br>
       ,==< 0x08048be9      0f84a0000000   je 0x8048c8f                ; sym.phase_3+0xf7 <br>
       |   0x08048bef      e808090000     call sym.explode_bomb      ; long double expl(long double x); <br>
</code>

A high-level overview is that a <i>cmp eax, 2</i> instruction occurs, and then a <i>jg</i> (jump if greater) instruction immediately follows it. If the jump fails, the explode_bomb function is called. If it succeeds, then we'll have a <i>cmp dword [ebp - local_ch], 7</i> instruction. This is immediately followed by a <i>ja</i> (jump if above) instruction. It looks like that jump will take us out of the function altogether if it happens, which is odd. It may be that there's more we'd see if we ran this program in a debugger. Since we've already gotten a reasonable amount of information, let's move on to dynamic analysis and play around with our input some.

<b>Dynamic analysis</b>

Go ahead and fire up the bomb binary in GDB and set a breakpoint at phase_3. Then go ahead and run the bomb and submit the first two defusal codes. 

<code>
reverse@debian:~/reversing/binary_bomb$ gdb ./bomb <br>
gdb-peda$ break phase_3  <br>
Breakpoint 1 at 0x8048b9f  <br>
gdb-peda$ r  <br>
Starting program: /home/reverse/reversing/binary_bomb/bomb   <br>
Welcome to my fiendish little bomb. You have 6 phases with  <br>
which to blow yourself up. Have a nice day!  <br>
Public speaking is very easy.  <br>
Phase 1 defused. How about the next one?  <br>
1 2 6 24 120 720  <br>
That's number 2.  Keep going!  <br>
</code>

At this point, the binary is waiting for us to provide input for the third phase. Remember how two of the instructions we saw in close proximity were <i>cmp eax, 2</i> and <i>cmp dword [ebp - local_ch], 7</i>? We know that the input should be greater than 0x2, and a moment later we see a cmp with 0x7. Based on that, let's just try 7 for our first piece of input. However, we'll also need a single character and a second integer. We don't have as much information to inform a guess for those two, so let's just try this input:<br>
<code>7 a 2</code>

After submitting this input, GDB should hit the breakpoint at phase_3.

![Alt text](/images/phase3_2.png?raw=true "phase_3 first breakpoint")

We're mostly interested in instructions that occur a bit further down in this function, so let's go ahead and set a breakpoint at:
0x08048bbc <+36>:	add    esp,0x20

(Don't forget that you can disassemble this function in GDB with <code>disassemble phase_3</code> to find various function offsets when setting breakpoints.)

<code>
break *phase_3+36 <br>
c <br>
</code>

Continuing execution will bring us to the second breakpoint. Single step to:<br>
<code>0x8048bbf <phase_3+39>:	cmp    eax,0x2</code>

Currently, EAX is equal to 0x3, so the jump should be taken, avoiding the first bomb explosion. Single step twice more and you'll find that this is the case, arriving at: <br>
<code>0x8048bc9 <phase_3+49>:	cmp    DWORD PTR [ebp-0xc],0x7</code>

Let's check out what the register arithmetic ends up being equal to: <br>
<code>
gdb-peda$ x/x $ebp-0xc<br>
0xbffff2bc:	0x00000007
</code>

Probably that 0x7 is the first value in our input. Single step forward once and you'll see that the <i>ja</i> is NOT taken, becuase the values being compared are equal. Go ahead and keep single stepping. Notice that when you reach this instruction: <br>
<code>0x8048bd6 <phase_3+62>:	jmp    DWORD PTR [eax*4+0x80497e8]</code>

The jump is taken. Stop single stepping when you reach this instruction: <br>
<code>0x8048c78 <phase_3+224>:	cmp    DWORD PTR [ebp-0x4],0x20c</code>

Let's take a look at that register arithmetic and see what's held at that pointer: <br>
<code>
gdb-peda$ x/x $ebp-0x4
0xbffff2c4:	0x00000002
</code>

![Alt text](/images/phase3_3.png?raw=true "Checking pointer value")

Remember that 0x2 was the last piece of input we submitted. It's being compared against 0x20c, which equates to 524 in decimal. These values aren't equal, so the upcoming jump (visible in GDB-PEDA or the disassembled function) isn't going to be taken, and the explode_bomb function is going to be called. Interestingly, the function doesn't seem to have inspected our middle piece of input (the single character, 'a') yet. Based on this behavior, we can safely assume that we need to get the two integer portions correct before the single character gets checked. 

Since 0x20c is 524 in decimal, maybe that should be our final piece of input. Before restarting the program, though, let's go ahead and set a breakpoint at our current instruction, phase_3+224. Since we've already passed the other checks before, there's not much point seeing that section again.

<code>
gdb-peda$ break *phase_3+224<br>
Breakpoint 3 at 0x8048c78
</code>

Go ahead and restart the binary with:<br>
<code>r</code>

This time, when prompted for input for phase_3, let's try using our newfound final integer, along with the other two pieces we tried before:<br>
<code>7 a 524</code>

When you hit the first breakpoint, go ahead and continue execution (using the "c" or "continue" command) to reach the second breakpoint; do the same thing again to reach the third. Now, go ahead and inspect the pointer being comapred again: <br>

<code>
gdb-peda$ x/x $ebp-0x4 <br>
0xbffff2c4:	0x0000020c
</code>

![Alt text](/images/phase3_4.png?raw=true "Second check of pointer with new input")

Aha! This time, the dereferenced pointer is equal to 0x20c, which is exactly what we wanted. Issue a single step to discover that now the jump will be taken. Single step again to reach this instruction:<br>
<code>0x8048c8f <phase_3+247>:	cmp    bl,BYTE PTR [ebp-0x5]</code>

Okay, so let's check out the BL register and the pointer:<br>
<code>
gdb-peda$ x/x $bl <br>
0x62:	Cannot access memory at address 0x62 <br>
gdb-peda$ x/x $ebp-0x5 <br>
0xbffff2c3:	0x00020c61 <br>
</code>

So BL is equal to 0x62. However, the value for that pointer isn't a valid address, but also doesn't cleanly convert to any character we're likely to have entered. Let's inspect the adress listed for the pointer, 0xbffff2c3:<br>
<code>
gdb-peda$ x/x 0xbffff2c3 <br>
0xbffff2c3:	0x61 <br>
</code>

Ah, that makes more sense! 0x61 converts to ASCII as "a", which was our input. 0x62 converts to "b", the very next character in the ASCII table. These two characters obviously aren't equal, and if you single step one more time, you'll find that the <i>je</i> instruction is therefore not taken. However, based on the trend of the previous <i>cmp</i> instructions, it's very likely that "b" is the character we need to submit in our defusal code. Therefore, the final defusal code might be: <br>
<code>
7 b 524
</code>

Let's go ahead and re-run the program with that code and see what happens!<br>

<code>
reverse@debian:~/reversing/binary_bomb$ ./bomb  <br>
Welcome to my fiendish little bomb. You have 6 phases with<br>
which to blow yourself up. Have a nice day!<br>
Public speaking is very easy.<br>
Phase 1 defused. How about the next one?<br>
1 2 6 24 120 720<br>
That's number 2.  Keep going!<br>
7 b 524<br>
Halfway there!<br>
</code>

And with that, we're on to phase 4!
