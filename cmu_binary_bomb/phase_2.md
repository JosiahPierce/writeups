Now that we've found the first defusal code, we can move on to solving the second phase. If you haven't already, I recommend checking out the phase 1 writeup if you want to familiarize yourself with the tools we'll be using and their basic syntax. If you already know the basics of radare2 and GDB-PEDA, then read on!

<b>Static analysis</b>

Like before, we'll start off by examining the appropriate phase function in radare2 to get a general idea of what it does. This assumes that you've already analyzed the binary with radare2, so if you haven't done that yet, you can check out the phase 1 section to learn how. To start off, let's seek to the phase_2 function and disassemble it. As a reminder, the syntax to do that is:

<code>s sym.phase_2</code>
<code>pdf</code>

![Alt text](/images/phase2_1.png?raw=true "Disassembled phase_2")

This is still a fairly short function, but it's a bit more complex than phase_1. This chunk of assembly code is probably what's most relevant to us:

|           0x08048b5b      e878040000     call sym.read_six_numbers  ; ssize_t read(int fildes, void *buf, size_t nbyte);
|           0x08048b60      83c410         add esp, 0x10
|           0x08048b63      837de801       cmp dword [ebp - local_18h], 1 ; [0x1:4]=0x1464c45
|       ,=< 0x08048b67      7405           je 0x8048b6e
|       |   0x08048b69      e88e090000     call sym.explode_bomb      ; long double expl(long double x);
|       `-> 0x08048b6e      bb01000000     mov ebx, 1
|           0x08048b73      8d75e8         lea esi, dword [ebp - local_18h]
|       .-> 0x08048b76      8d4301         lea eax, dword [ebx + 1]    ; 0x1
|       |   0x08048b79      0faf449efc     imul eax, dword [esi + ebx*4 - 4]
|       |   0x08048b7e      39049e         cmp dword [esi + ebx*4], eax ; [0x13:4]=256
|      ,==< 0x08048b81      7405           je 0x8048b88
|      ||   0x08048b83      e874090000     call sym.explode_bomb      ; long double expl(long double x);
|      `--> 0x08048b88      43             inc ebx
|       |   0x08048b89      83fb05         cmp ebx, 5
|       `=< 0x08048b8c      7ee8           jle 0x8048b76

So we call a function called read_six_numbers, and then we do some comparisons. There are two different opportunities for explode_bomb to be called, and there's also a <i>jle</i> instruction that can jump back up a bit, providing more opportunities for the second occurrence of the explode_bomb function to be called. To gain a better understanding of what input is expected, let's seek to and disassemble that read_six_numbers function:

<code>s sym.read_six_numbers</code>
<code>pdf</code>

![Alt text](/images/phase2_2.png?raw=true "Disassembled read_six_numbers")

There are only a few lines here that are especially important to notice:

|           0x08048ff9      681b9b0408     push str._d__d__d__d__d__d ; str._d__d__d__d__d__d ; "%d %d %d %d %d %d" @ 0x8049b1b
|           0x08048ffe      51             push ecx                    ; long double x
|           0x08048fff      e85cf8ffff     call sym.imp.sscanf        ; int sscanf(const char *s,
|           0x08049004      83c420         add esp, 0x20
|           0x08049007      83f805         cmp eax, 5
|       ,=< 0x0804900a      7f05           jg 0x8049011
|       |   0x0804900c      e8eb040000     call sym.explode_bomb      ; long double expl(long double x

Most important is the instruction at 0x08048ff9. Notice what's getting pushed onto the stack? 

<code>"%d %d %d %d %d %d"</code>

If you're familiar with format strings in C, you know that %d is the format string for an integer. There are also spaces in between each format string. This tells us that the function expects the user input to be six integers with spaces in between each one. 

The other important instruction to notice is <i>cmp eax, 5</i>. Immediately after this instruction is a <i>jg</i> (jump if greater) instruction. If that jump isn't taken, then the explode_bomb function is called. This is probably telling us that EAX (the register that stores return values of functions) needs to be greater than 5 for the read_six_numbers function to consider our input correct. If EAX were five or less, that would mean that we hadn't entered at least six numbers. This seems like a reasonable guess at what's going on. If you'd like, you can always run through this function with a debugger after entering your input for phase_2 and see if this guess is accurate.

<b>Dynamic analysis<b>

Now that we have some idea of what kind of input we should provide, let's check out phase_2 in GDB. We'll launch GDB, then set a breakpoint at phase_2, since we don't need to inspect the first phase anymore. 

<code>gdb ./bomb</code>
<code>break phase_2</code>

Now we can go ahead and run the bomb, keeping our defusal code for the first phase handy:

<code>
gdb-peda$ r
Starting program: /home/reverse/reversing/binary_bomb/bomb 
Welcome to my fiendish little bomb. You have 6 phases with
which to blow yourself up. Have a nice day!
Public speaking is very easy.
Phase 1 defused. How about the next one?
</code>

Time to provide some input. Since we know we need six numbers and spaces between them, let's try:
1 2 3 4 5 6

After entering this, GDB should hit the breakpoint we've set. We're not really interested in anything that happens in this function until after the read_six_numbers function is called, so let's set a second breakpoint. First, to get the instruction numbers, disassemble the function in GDB with:

<code>diassemble phase_2</code>

![Alt text](/images/phase2_3.png?raw=true "GDB disassembly")

We're interested in everything from this instruction onward:
0x08048b60 <+24>

Let's set a breakpoint at that instruction:

<code>break *phase_2+24</code>

Now we can continue execution:

<code>c</code>

Now we should have hit our second breakpoint. Single step once with:

<code>s</code>

We've now arrived at this instruction:
0x8048b63 <phase_2+27>:	cmp    DWORD PTR [ebp-0x18],0x1

GDB allows us to perform register arithmetic. To find out the value of EBP-0x18, run:

<code>x/x $ebp-0x18</code>

<i>Tip: x/x is an "examine" command. The first x tells us to examine something at a specific address. After the slash, a variety of characters can be inserted; the x we chose indicates that we'd like to examine the content in hexadecimal format.<i>

<code>
gdb-peda$ x/x $ebp-0x18
0xbffff2b0:	0x00000001
</code>

So $ebp-0x18 is currently equal to 1. Let's keep stepping and see what happens. The <i>je</i> jump is taken, so we avoid the first bomb explosion. We then jump to this instruction:
0x8048b6e <phase_2+38>:	mov    ebx,0x1

We're coming to an interesting chunk of instructions:

|       `-> 0x08048b6e      bb01000000     mov ebx, 1
|           0x08048b73      8d75e8         lea esi, dword [ebp - local_18h]
|       .-> 0x08048b76      8d4301         lea eax, dword [ebx + 1]    ; 0x1
|       |   0x08048b79      0faf449efc     imul eax, dword [esi + ebx*4 - 4]
|       |   0x08048b7e      39049e         cmp dword [esi + ebx*4], eax ; [0x13:4]=256
|      ,==< 0x08048b81      7405           je 0x8048b88
|      ||   0x08048b83      e874090000     call sym.explode_bomb      ; long double expl(long double x);

In particular, that <i>cmp<i> instruction looks important; it looks like we'll want eax to be equal to the expression on the left side of the comparison. Let's just single step until we reach that instruction.

![Alt text](/images/phase2_4.png?raw=true "CMP instruction")

We can see that EAX is currently equal to 0x2. How about the other half of the comparison?

<code>
gdb-peda$ x/x $esi+$ebx*4
0xbffff2b4:	0x00000002
</code>

Looks like that is equal to 0x2 as well! Before we move on from this, recall that 2 was our second input number. Great, but what about the first input value we provided? Remember that check earlier to see if $ebp-0x18 was equal to 1? Maybe that checked to see if our first digit was equal to 1. If so, then we got to move on to checking the other five. Now it looks like our second digit is going to pass this comparison. To be sure, let's continue on. With a single step, we discover that the <i>je</i>instruction allows us to take the jump, skipping over the explode_bomb call.

That means that probably our first two input numbers were correct. Let's jot down our partial defusal code. So far we've got:
1 2

After the jump, notice our next few instructions:

|      `--> 0x08048b88      43             inc ebx
|       |   0x08048b89      83fb05         cmp ebx, 5
|       `=< 0x08048b8c      7ee8           jle 0x8048b76

EBX gets incremented, then checked to see if it's equal to 5. If not, we jump back to this:

|       .-> 0x08048b76      8d4301         lea eax, dword [ebx + 1]    ; 0x1
|       |   0x08048b79      0faf449efc     imul eax, dword [esi + ebx*4 - 4]
|       |   0x08048b7e      39049e         cmp dword [esi + ebx*4], eax ; [0x13:4]=256
|      ,==< 0x08048b81      7405           je 0x8048b88

So this looks like a loop, doesn't it? Keep repeating the same set of instructions, checking something each time, until a specific condition is met, then stop and continue on with execution. From this, we can deduce that <i>the program is going to keep checking each number we provided in our input, one at a time, until it's read them all<i>. But how do we figure out what the other numbers should be?

Remember how we checked out the register values in this comparison?
0x8048b7e <phase_2+54>:	cmp    DWORD PTR [esi+ebx*4],eax

That will disclose the value of each expected piece of input. To see this for yourself, single step until you reach that comparison for the second time. Now, inspect the values in those registers:

<code>
gdb-peda$ x/x $esi+$ebx*4
0xbffff2b8:	0x00000003

gdb-peda$ x/x $eax
0x6:	Cannot access memory at address 0x6
</code>

Hmm...0x3 is equal to the third number we provided, but 0x6 certainly isn't. This comparison is going to fail, and the bomb is going to explode. Since our argument resides in $esi+$ebx*4, the expected value must be the one in EAX. Therefore, the third expected value is 6. 

As an exercise for the reader, I recommend working through the loop this way, each time learning one new correct piece of input. You now have everything you need to learn the correct sequence. The final sequence is provided below; make sure that you got the same thing, and then you're done with this phase!

Final sequence:
1 2 6 24 120 720
