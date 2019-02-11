We're now halfway through the six main phases on the binary bomb, and things are starting to escalate in difficulty. As a relative newcomer to reverse engineering, I found that I started to rely more and more on dynamic analysis rather than combing through disassembly. I found it much easier to mess around with inputs and observe various changes for some of these later challenges. This is probably not the ideal way to approach these challenges, but ultimately this strategy did allow me to build up enough of an understanding of a phase's behavior to determine the defusal code, so I suppose it does have some merit.

As we jump into phase 4, keep your defusal codes for the previous phases handy:
<i>Phase 1</i>: Public speaking is very easy.<br>
<i>Phase 2</i>: 1 2 6 24 120 720<br>
<i>Phase 3</i>: 7 b 524

<b>Static analysis</b>

Just like always, seek to the phase_4 function in radare2 and disassemble it.

<code>
s sym.phase_4  <br/>
pdf <br/>

</code>

![Alt text](/images/phase4_1.png?raw=true "Disassembled phase_4")


At a quick glance, this instruction closely following the stack prologue looks interesting:  <br/>
 <code>0x08048cf0      6808980408     push 0x8049808              ; "%d"</code>  <br/>

Since there's a single %d pushed onto the stack (the C format string for a signed integer), we can assume that our input for this phase probably only needs to be a single signed integer. It's worth noting that we might be able to just brute-force the defusal code with this information, but this is discouraged; in the original version of this assignment, the binary was stored on a server that deducted points from the final assignment score every time the bomb exploded. Since we're not doing this for a school assignment, there are no penalties for trying this approach, but it's definitely possible to do this through actual reverse engineering, and that's what we're trying to learn here.

Take a moment to look through the rest of the disassembly yourself. What sticks out to you? Hopefully, you should notice that this function doesn't really seem to be doing much. The most interesting line is this one:  <br/>
<code>0x08048d15      e886ffffff     call sym.func4</code>  <br/>

Looks like another function is getting called. Probably, that one contains most of the actual logic of this phase. Before we check that out, though, I'll introduce another feature of radare2 that we haven't tried yet. At your radare2 prompt, type the following to get a visual execution flow graph of the function you're currently examining:  <br/>

<code>VV</code>  <br/>  

![Alt text](/images/phase4_2.png?raw=true "Graph mode in radare2")


This shows different blocks of code and where various jump-type instructions will take the execution flow. A "t" indicates that a jump WAS taken (true), and an "f" indicates that a jump WAS NOT taken (false). You can use the arrow keys to navigate around and take a look at the full graph. This feature is extremely handy for getting a high-level overview of more complex functions, and it can really help demystify tricky loops or other control flow structures.

When you're ready to leave this graph and go back to your prompt, you can double-tap the <b>esc</b> key twice.

The final important aspect of this function for us to notice is this chunk of instructions:  <br/>  
```assembly
0x08048d1d      83f837         cmp eax, 0x37               ; '7' ; '7' 
 
0x08048d20      7405           je 0x8048d27 

0x08048d22      e8d5070000     call sym.explode_bomb      ; long double expl(long double x);

```

These are the last instructions before the stack epilogue takes place. Looks like that <i>cmp eax,0x37</i> instruction is responsible for determining whether the explode_bomb function gets jumped over or not. If that comparison doesn't return equal, then the bomb explodes. 0x37 is 55 in decimal, in case that becomes relevant later.


Next, let's go ahead and take a look at that func4 function:  <br/>  

<code>
s sym.func4  <br/>  
 
pdf  <br/>  

</code>

![Alt text](/images/phase4_3.png?raw=true "Disassembled func4")


Notice that func4 has several <i>call sym.func4</i> functions? Evidently, this is a recursive function. Check out this function in the execution flow graph to gain a better understanding of it. Ultimately, it looks like the cmp ebx,1 needs to return "less than or equal to" for that jump to take place, skipping over the recursive function calls. At this point, I decided that dynamic analysis might prove to be the path of least resistance, so let's move on to that phase.

<b>Dynamic analysis</b>  <br/>  

Go ahead and open the bomb in GDB, setting a breakpoint at phase_4:  <br/>  

<code>
gdb ./bomb  <br/>  
 
break phase_4  <br/>  

</code>

Now go ahead and start running the binary, providing the first three defusal codes:  <br/>  

<code>
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

</code>

For phase 4, we know we need to submit a single integer. Let's try 5. After entering that, you should hit the breakpoint at phase_4.

What's our plan of attack for this one? We saw that func4 is recursive, which could make it tricky to analyze. We might still need to, but first, let's try another technique. Remeber that these three instructions near the end of the phase_4 function seemed critical:  <br/>  

```assembly
   0x08048d1d <+61>:	cmp    eax,0x37
 
   0x08048d20 <+64>:	je     0x8048d27 <phase_4+71>
   
   0x08048d22 <+66>:	call   0x80494fc <explode_bomb>
   
```

Since EAX is being compared with a fixed value, and this is at the end of the function, we might be able to figure out if the func4 function is mutating our input in some way by just setting a breakpoint at that comparison (phase_4+61) and then trying different inputs to see what ends up in EAX. This way, we circumvent having to do so much analysis of func4 itself. 

<code>
gdb-peda$ break *phase_4+61  <br/>  
 
Breakpoint 2 at 0x8048d1d  <br/>  

</code>

Now go ahead and continue execution, which should bring you to the breakpoint you just set. 

![Alt text](/images/phase4_4.png?raw=true "GDB view of phase 4")

In this case, EAX is currently equal to 0x8. Not even close to the 0x37 we need to be equal to. However, this does give us an important piece of information, which is that <i>our input has been modified somehow</i>. Don't forget, our input was 5, but EAX is now 0x8, so somewhere along the line, our input has probably increased in value. Let's see if this is true by re-running the program, this time providing 6 as out integer input instead of 5. Continue program execution until you hit this second breakpoint again.

This time, EAX is equal to 0xd. It's still not clear how our input is being modified, since this isn't a consistent increase from our previous input (5 + 3 == 0x8, so if we were just adding 0x3 to our input, this time we'd expect to see 0x9). However, 0xd is closer to that 0x37 goal, so let's just keep incrementing our input for a while longer and see if a pattern emerges. Repeat the process of running the program and reaching this second breakpoint, this time providing 7 as input.

EAX should be equal to 0x15 this time. We're still inching closer to the value we need, so let's just keep going with this approach. Re-run the program again with 8 as the argument this time.

EAX is now 0x22. We're still making progress. How about we try 9 this time?

![Alt text](/images/phase4_5.png?raw=true "Correct EAX value")


Aha! Now EAX is finally 0x37. Go ahead and continue program execution, and we'll see this response:  <br/>  
<code>So you got that one.  Try this one.</code>  <br/>  

So the defusal code for this phase is "9". There's some trade-off with the method we just employed; the advantage of approaching the challenge this way is that we found the answer pretty quickly, without wasting a lot of time digging through recursive function calls. Even though it wasn't obvious how our input was being modified, it was clear that we were making progress toward the value we wanted, so it was pretty simple to just stay on that path, mess with inputs and see what happened.

The downside, of course, is that we haven't actually determined what func4 is really doing with our input. If the challenge had required more than one piece of input, then this approach wouldn't have worked as well, since there would've been a lot more values to try; it probably would have become more efficient to actually understand more of the underlying logic. Later phases in the binary bomb will require us to scrutinze the function logic more, so we may as well enjoy this quick win. On to phase 5!
