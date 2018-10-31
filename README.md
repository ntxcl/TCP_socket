# TCP_socket
In Project 1 you wrote a UDP server allowing a file to be transferred to clients in 32 KiB sections. 
While files should be transferred successfully when running on localhost or across a local area network, 
packets may be lost when the network is heavily loaded or the connection requires several hops. 
To address the possibility of packet loss, we will switch to the TCP protocol.

Reliability
Unfortunately, while the transport protocol may be reliable, the hosts claiming to implement the application protocol may not be. 
While responses to LIST requests can be trusted, requests to download sections may not always succeed. Your client should recover 
from these failures.
Test Environment
You may use any platform for development, but note that per the Syllabus the test environment for projects in this course is a Tuffix VM 
with Python 3.6.x.
Tips
Read the Socket Programming HOWTO.
 When you’re ready to start testing your code, consider setting UNRELIABLE to False.
When you’re sure you can download a file successfully, don’t forget to change it back to True.
SectionServer.py can run on more than one port. Consider what that might mean for Project 3.
