Vape Nation is listed as a 50-point Stego challenge. There's not much in the way of description; 
just the phrase "Go Green!" and a link to an image. Let's go ahead and download it. 

Before we actually look at the image itself, let's get some information about the file:

![Alt text](/images/vape_nation_screen1.png?raw=true "Screen 1")

Looks like a standard PNG image. Next, let's try running binwalk on the image to see if there's anything sneaky:

![Alt text](/images/vape_nation_screen2.png?raw=true "Screen 2")

So there's some Zlib compressed data, but this is normal for PNG images. You can read more about that here:
http://www.libpng.org/pub/png/spec/1.2/PNG-Compression.html

Lastly, we can try running strings on the image to see if we can grab anything useful. 
Grepping for a few different terms doesn't turn up anything. Even though we didn't find anything useful, it's 
always smart to perform these checks first before analyzing the image. Now we can move on to inspecting the image itself.

![Alt text](/images/vape_nation_screen3.png?raw=true "Screen 3")

A good starting point would be to try changing the color map of the image and examining different color planes. 
To help with this, let's try a useful tool for steganography problems called Stegsolve. Stegsolve can be 
used for image analysis and data extraction, among other things. You can obtain it here:
https://www.wechall.net/forum-t527/Stegsolve_1_3.html

In order to run it, place the .jar in a directory and navigate there. Then run the following command:
java -jar Stegsolve.jar

Open the image with Stegsolve. Since the decription mentioned "Go Green!", perhaps we should try 
investigating the green color planes? 

![Alt text](/images/vape_nation_screen4.png?raw=true "Screen 4")

And there it is! The flag is under the green plane zero.
