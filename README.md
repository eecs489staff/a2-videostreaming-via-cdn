# Assignment 2: Video Streaming via CDN


### Due: October 11th, 2024 at 11:59 PM

## Table of contents
* [Overview](#overview)
* [Clarifications](#clarifications)
* [Environment Setup](#environment)
* [Part 1](#part1): Bitrate Adaptation in HTTP Proxy
* [Part 2](#part2): DNS Load Balancing
* [Submission Instructions](#submission-instr)
* [Autograder](#autograder)

<a name="overview"></a>
## Overview

Video traffic dominates the Internet. In this project, you will explore how video content distribution networks (CDNs) work. In particular, you will implement adaptive bitrate selection, DNS load balancing, and an HTTP proxy server to stream video at high bit rates from the closest server to a given client.

This project is divided into Part 1 and Part 2. We recommend that you work on them simultaneously (both of them can be independently tested), and finally integrate both parts together.

<img src="github_assets/real-CDN.png" title="Video CDN in the wild" alt="" width="350" height="256"/>

### Video CDNs in the Real World
The figure above depicts a high level view of what this system looks like in the real world. Clients trying to stream a video first issue a DNS query to resolve the service's domain name to an IP address for one of the CDN's content servers. The CDN's authoritative DNS server selects the “best” content server for each particular client based on
(1) the client's IP address (from which it learns the client's geographic location) and
(2) current load on the content servers (which the servers periodically report to the DNS server).

Once the client has the IP address for one of the content servers, it begins requesting chunks of the video the user requested. The video is encoded at multiple bitrates. As the client player receives video data, it calculates the throughput of the transfer and it requests the highest bitrate the connection can support.

### Video CDN in this Assignment
Implementing an entire CDN is difficult; instead, you'll focus on a simplified version. First, your entire system will run on one host and rely on mininet to run several processes with arbitrary IP addresses on one machine. Mininet will also allow you to assign arbitrary link characteristics (bandwidth and latency) to each pair of “end hosts” (processes).

<img src="github_assets/our-CDN.png" title="Video CDN in assignment 2" alt="" width="330" height="111"/>

You'll write the gray-shaded components (i.e. the DNS Server and Proxy) in the figure above.

**Video Viewer.** You can use an off-the-shelf Video Viewer like a web browser (Firefox, Chrome, etc.) to play videos served by your CDN (via your proxy).

**Proxy.** Rather than modify the video player itself, you will implement adaptive bitrate selection in an HTTP proxy. The player requests chunks with standard HTTP GET requests; your proxy will intercept these and modify them to retrieve whichever bitrate your algorithm deems appropriate.

**Web Server.** Video content will be served from an off-the-shelf web server. As with the proxy, you will run multiple instances of the web server on different IP addresses to simulate a CDN with several content servers.

**DNS Server.** You will implement a simple DNS that supports only a small portion of actual DNS's functionality. Your server will respond to each request with the “best” server for that particular client.

To summarize, this assignment has the following components:

* [Part 1](#part1): Bitrate Adaptation in HTTP Proxy
* [Part 2](#part2): DNS Load Balancing

## Learning Outcomes

After completing this programming assignment, students should be able to:

* Explain how HTTP proxies, DNS servers, and video CDNs work
* Create topologies and change network characteristics in Mininet to test networked systems

<a name="clarifications"></a>
## Clarifications

* For the proxy you implement in part 1, you will need to parse some HTTP traffic. To make your life easier for this project, you **do not** need to be concerned about parsing all the information in these HTTP messages. There are only two things that you need to care about searching for: `\r\n\r\n` and `Content-Length`. The former is used to denote the end of an HTTP header, and the latter is used to signify the size of the HTTP body in bytes.

* The proxy should be able to support multiple browsers playing videos simultaneously. This means you should test with multiple browsers all connecting to the same proxy. In addition you should also test with multiple proxies each serve some number of browser(s), in order to make sure that each proxy instance does not interfere with others. 

* While testing the proxy you implement in part 1, you may notice that one browser may sometimes open multiple connections to your proxy server. Your proxy should still continue to function as expected in this case. In order to account for these multiple connections, you may use the browser IP address to uniquely identify each connection. This implies that while testing your proxy server, each browser will have a unique IP address. (For example, only one browser will have an IP address of 10.0.0.2)

* Throughput should be measured on each fragment. For example, throughput should be calculated separately for both Seg-1 and Seg-2.

<a name="environment"></a>

## Environment Setup
You will use AWS academy's Learing lab similar to project 1 as your development environment. Please make sure you create an instance based on the shared AMI `EECS489p2` and select **_t3-medium_** for instance type. 

Once you have logged into your instance, you can get the starter files by cloning the assignment github repository:

```bash
git clone https://github.com/eecs489staff/a2-videostreaming-via-cdn.git
```

Then, make sure you unzip `vod.tar`, which contains the video content files, and place it in the same directory as `webserver.py`:

```bash
   mv web/vod.tar .
   tar -xvf vod.tar
```

In your project, you will have to run code on **multiple hosts** simultaneously in Mininet. Furthermore, you will need access to a GUI in order to test your code more easily, as we are interested in streaming video. To accomplish this, please refer to the [setup instructions](#instruction-sheet-using-the-aws-ami-for-mininet-with-vnc-and-starter-files) to set up a VNC client that will enable you to set up a GUI for your EC2 instance. 

There are 4 main components in this project, each of which requires its own Mininet host:
1. CDNs/Web servers(at least 1): At least 1 host should run the start server script and start serving video/html content. These are the "CDN"s in this project. They provide our proxy with video content. To start the webserver on a host in mininet, simply run the python script we provide using the following command:

```bash
   h(n) sudo ./launch_webserver
```

Here `h(n)` is the host on mininet on which you are running the webserver. The webserver expects the content of the website to be in a folder called ```vod```. This folder should be in the same directory from which you are executing the web server, and can be unzipped from the starter files (see above). 

Like any HTTP web server (not HTTPS) these instances of the server will be reachable on TCP port `80`. For simplicity, all of our web traffic for this assignment will be unencrypted and be done over HTTP.

2. Browser/Client(at least 1): At least 1 host should run the Chrome browser script and launch the browser. This is the client that negotiates with the proxy. Since Chrome uses a Graphical User Interface, please refer to [setup instructions](#instruction-sheet-using-the-aws-ami-for-mininet-with-vnc-and-starter-files) on how to login to your aws instance remotely with a Graphical interface.

3. Proxy(exactly 1): Exactly 1 host should run the proxy. The proxy acts as a load balancer and is the "middleman" between clients and CDNs. It forwards client requests to one of the web servers, and forwards web server responses to the client.

4. DNS/name server(exactly 1): Exactly 1 host should run the name server. The name server will tell the proxy which web server it should forward client request to when it receives a response from the server.
In summary, at least 4 hosts should be running in Mininet for fully testing the project!. 

We're leaving it up to you to write your own Mininet topology script for testing the package as a whole. A simple Starfish topology (all hosts connected to one switch in the middle) should suffice for testing. 

You may find it helpful to install xterm
```bash
sudo apt install xterm`
```

If xterm or ./chrome are not launching windows from within Mininet, run
```bash
xhost +
```
**outside** of your mininet environment.

### Setup Tips 
> **How do I verify a web server is running?**
1. Use `curl <host_ip>/index.html` and see if it prints out a bunch of html
2. Go to `<host_ip>/index.html` in your Chrome browser
3. Use `netstat -tulpn | grep :80` to see if there's anything running on port 80 
> **How do I shut down a web server?**
1. sudo kill -9 <pid of the process using port 80> 


<a name="part1"></a>
## Part 1: Bitrate Adaptation in HTTP Proxy

**TL;DR:** Your miProxy should: 
1. Accepting connections from **multiple clients** (think server in p1) 
2. Be able to connect to one of the CDN web servers
3. Forward HTTP requests from clients
4. Wait and forward HTTP responses from CDNs
5. Measure the throughput of each video segment
6. Capture video manifest file HTTP requests, send a manifest request to web server, and send another request to return a no list manifest file to client 
7. Capture video segment HTTP requests and modify the request according to measured throughputs 
8. Be able to connect to name server and get DNS response 
Read on for more details. 

Many video players monitor how quickly they receive data from the server and use this throughput value to request better or lower quality encodings of the video, aiming to stream the highest quality encoding that the connection can handle. Instead of modifying an existing video client to perform bitrate adaptation, you will implement this functionality in an HTTP proxy through which your browser will direct requests.

You are to implement a simple HTTP proxy, `miProxy`. It accepts connections from web browsers, modifies video chunk requests as described below, resolves the web server's DNS name, opens a connection with the resulting IP address, and forwards the modified request to the server. Any data (the video chunks) returned by the server should be forwarded, *unmodified*, to the browser.

`miProxy` should listen for browser connections on `INADDR_ANY` on the port specified on the command line. It should then connect to a web server either specified on the command line or issue a DNS query to find out the IP address of the server to contact (this is covered in part 2).

<img src="github_assets/proxy-overview.png" title="Video CDN in the wild" alt="" width="534" height="171"/>

`(assign ephemeral)` is referring to the fact that the kernel will pick the proxy's TCP port when it connects to the web server's port `80`. Nothing more than the proxy calling `connect()` is happening here.

`miProxy` should accept multiple concurrent connections from clients (Chrome web browsers) using `select()` and be able to handle the required HTTP 1.1 requests for this assignment (e.g., HTTP `GET`).

The picture above shows `miProxy` connected to multiple web servers, which would be the case if `miProxy` issued a DNS request for each new client connection received (e.g each new connection from an instance of Chrome). This is one approach for utilizing the DNS `nameserver` you will write in part 2. Another approach would be to issue a DNS request **once** when `miProxy` starts up, and direct all client requests to one web server for the entire runtime of `miProxy`. Either approach is acceptable for grading purposes, but the former is preferred because it provides more efficient load balancing, and it is closer to the behavior of an actual load balancing proxy.

We will cover the basic usage of `select()` in the discussion.

> *Note: A good resource for socket programming is [Beej's Guide to Network Programming Using Internet Sockets](https://beej.us/guide/bgnet/html/).*

### Throughput Calculation

Your proxy measure the the throughput between the server and itself to determine the bitrate. Your proxy should estimate each stream's throughput once per chunk. Make sure to note the start time of each chunk when your proxy started receiving the chunk from the server, and save another timestamp when you have finished receiving the chunk from the server. Given the size of the chunk, you can now compute the throughput by dividing chunk size by the time window.


Each video is a sequence of chunks. To smooth your throughput estimation, you should use an exponentially-weighted moving average (EWMA). Every time you make a new measurement (as outlined above), update your current throughput estimate as follows:

`T_cur = alpha * T_new + (1 - alpha) * T_cur`

The constant `0 ≤ alpha ≤ 1` controls the tradeoff between a smooth throughput estimate (`alpha` closer to 0) and one that reacts quickly to changes (`alpha` closer to 1). You will control `alpha` via a command line argument. **_When a new stream starts, set `T_cur` to the *lowest* available bitrate for that video_**.


### Choosing a Bitrate

Once your proxy has calculated the connection's current throughput, it should select the highest offered bitrate the connection can support. For this project, we say a connection can support a bitrate if the average throughput is at least 1.5 times the bitrate. For example, before your proxy should request chunks encoded at 1000 Kbps, its current throughput estimate should be at least 1500 Kbps (1.5 Mbps).

Your proxy should learn which bitrates are available for a given video by parsing the manifest file (the ".mpd" initially requested at the beginning of the stream). The manifest is encoded in XML; each encoding of the video is described by a `<media>` element, whose bitrate attribute you should find.

Your proxy will replace each chunk request with a request for the same chunk at the selected bitrate (in Kbps) by modifying the HTTP request’s `Request-URI`. Video chunk URIs are structured as follows:

`/path/to/video/vid-<bitrate>-seg-<num>.m4s`

For example, suppose the player requests chunk 2 of the video `tears-of-steel.mp4` at 500 Kbps:

`/path/to/video/vid-500-seg-2.m4s`

To switch to a higher bitrate, e.g., 1000 Kbps, the proxy should modify the URI like this:

`/path/to/video/vid-1000-seg-2.m4s`

> **IMPORTANT:** When the video player requests `tears-of-steel.mpd`, you should instead return `tears-of-steel-no-list.mpd` to the video player. This file does not list the available bitrates, preventing the video player from attempting its own bitrate adaptation. Your proxy should, however, fetch `tears_-of-steel.mpd` for itself (i.e., don’t return it to the client) so you can parse the list of available encodings as described above. Your proxy should keep this list of available bitrates for each video in a global container (not on a connection by connection basis).

### Running `miProxy`
To operate `miProxy`, it should be invoked in one of two ways

**Method 1** - No DNS `nameserver` functionality, hard coded web server IP:

This mode of operation will be for testing your proxy without a working DNS server from part 2.

`./miProxy --nodns <listen-port> <www-ip> <alpha> <log>`

* `--nodns` This flag indicates the proxy won't use DNS to get the web server IP.
* `listen-port` The TCP port your proxy should listen on for accepting connections from your browser.
* `www-ip` Argument specifying the IP address of the web server from which the proxy should request video chunks. Again, this web server is reachable at port TCP port `80`.
* `alpha` A float in the range [0, 1]. Uses this as the coefficient in your EWMA throughput estimate.
* `log` The file path to which you should log the messages as described below.

**Method 2** - Full and final functionality (after part 2 is implemented):

In this mode of operation your proxy should obtain the web server's IP address by querying your DNS server for the name `video.cse.umich.edu`.

`./miProxy --dns <listen-port> <dns-ip> <dns-port> <alpha> <log>`

* `--dns` This flag indicates the proxy will use DNS to obtain the web server IP.
* `listen-port` The TCP port your proxy should listen on for accepting connections from your browser.
* `dns-ip` IP address of the DNS server.
* `dns-port` Port number DNS server listens on.
* `alpha` A float in the range [0, 1]. Uses this as the coefficient in your EWMA throughput estimate.
* `log` The file path to which you should log the messages as described below.

> *Note: for simplicity, arguments will appear exactly as shown above (for both modes) during testing and grading. Error handling with the arguments is not explicitly tested but is highly recommended. At least printing the correct usage if something went wrong is worthwhile.*

> *Also note: we are using our own implementation of DNS on top of TCP, not UDP.*

### miProxy Logging
`miProxy` must create a log of its activity in a very particular format. If the log file, specified via a command line argument, already exists, `miProxy` overwrites the log. *After each chunk-file response from the web server*, it should append the following line to the log:

`<browser-ip> <chunkname> <server-ip> <duration> <tput> <avg-tput> <bitrate>`

* `broswer-ip` IP address of the browser issuing the request to the proxy.
* `chunkname` The name of the file your proxy requested from the web server (that is, the modified file name in the modified HTTP GET message).
* `server-ip` The IP address of the server to which the proxy forwarded this request.
* `duration` A floating point number representing the number of seconds it took to download this chunk from the web server to the proxy.
* `tput` The throughput you measured for the current chunk in Kbps.
* `avg-tput` Your current EWMA throughput estimate in Kbps.
* `bitrate` The bitrate your proxy requested for this chunk in Kbps.

### Testing
To play a video through your proxy, you launch an instance of the web server, launch Chrome, and point the browser on the URL `http://<proxy_ip_addr>:<listen-port>/index.html`.

### Tips 
#### Miscellaneous 
- You can copy the mininet python script from p1 and use it directly in this project. 
- `miProxy` should **run forever**, unlike server in p1 which closes after sending ACK
- You should have 1 sockfd listening incoming connections and multiple other sockfds for all connected clients (1 each)
- Be careful with char arrays in DNS structs. They have fixed lengths of 100 but usually the actual content is much shorter. Directly converting them into `string` can cause very weird issues. Take out the actual content before converting them into strings.
- You **MUST** use different <host_num> for using `start_server.py` and different <profile> for `Chrome` 

#### Testing 
> 1. Accepting connections from **multiple clients** (think server in p1) 
> 2. Be able to connect to one of the CDN web servers
> 3. Forward HTTP requests from clients
> 4. Wait and forward HTTP responses from CDNs
> 5. Measure the throughput of each video segment
> 6. Capture video manifest file HTTP requests, send a manifest request to web server, and send another request to return a no list manifest file to client 
> 7. Capture video segment HTTP requests and modify the request according to measured throughputs 
> 8. Be able to connect to name server and get DNS response 
It is recommended to incrementally test your project in this order. Verify the previous step works before proceeding to the next.

When testing `miProxy` as a whole, you should test it under these scenarios progressively: 
1. No DNS, single client
2. No DNS, multiple clients 
3. DNS, single client
4. DNS, multiple clients

#### Design 
This project can be very overwhelming without a thoughtful class design choice. 
Some design choices we recommend (not required) are: 
- `get_server_ip()`: This function returns a fixed value on `--nodns`, and queries nameserver on `--dns`
- `get_request_type()`: This function returns the type of the client's request. This can be  1. Video Manifest Request  2. Video Segment Request  3. Other requests. You should handle these 3 types of requests differently.
- `handle_new_connection()`: This function handles new connection from the listen sockfd and add it to the existing connection fd set.
- `handle_client_reqeust()`: This function handles new requests from existing connections.


<a name="part2"></a>
## Part 2: DNS Load Balancing

To spread the load of serving videos among a group of servers, most CDNs perform some kind of load balancing. A common technique is to configure the CDN's authoritative DNS server to resolve a single domain name to one out of a set of IP addresses belonging to replicated content servers. The DNS server can use various strategies to spread the load, e.g., round-robin, shortest geographic distance, or current server load (which requires servers to periodically report their statuses to the DNS server). 

In this part, you will write a simple DNS server that implements load balancing in two different ways: round-robin and geographic distance. 

### Message Format for Our DNS Implemetation
In order for your proxy to be able to query your DNS server, you must also write an accompanying DNS resolution library. The two pieces should communicate using the DNS classes we provide (`DNSHeader.h`, `DNSQuestion.h`, and `DNSRecord.h`). You can read more about what each of the fields in these classes represents [here](https://datatracker.ietf.org/doc/html/rfc1035#section-4.1.1). To make your life easier:

* `AA` Set this to 0 in requests, 1 in responses.

* `RD` Set this to 0 in all messages.

* `RA` Set this to 0 in all messages.

* `Z` Set this to 0 in all messages.

* `NSCOUNT` Set this to 0 in all messages.

* `ARCOUNT` Set this to 0 in all messages.

* `QTYPE` Set this to 1 in all requests (asking for an A record).

* `QCLASS` Set this to 1 in all requests (asking for an IP address).

* `TYPE` Set this to 1 in all responses (returning an A record).

* `CLASS` Set this to 1 in all responses (returning an IP address).

* `TTL` Set this to 0 in all responses (no caching).

We are also providing encoding and decoding functions to serialize and deserialize your DNS query and response. Be sure to use the functions we provide so that your DNS server can be properly tested by autograder. In our implementation of DNS, the query consists of a DNS header and a question, and the response consists of a DNS header and a record.

**There are some slight nuances in the format of our DNS messages**. The main difference between what we do and what the RFC specifies is that the response should contain header + question + record, whereas our response is only header + record. Also, the size of each **encoded** object (represented as a 4-byte integer) is sent before sending the contents of the object. The overall procedure is outlined below:

1. `miProxy` sends integer designating the size of DNS header -> `miProxy` sends DNS header via encode() -> `miProxy` sends integer designating the size of DNS Question -> `miProxy` sends DNS Question via encode()

2. `nameserver` recvs() integer designating size of DNS Header -> `nameserver` recvs() DNS header via decode() -> `nameserver` recvs() integer designating size of DNS Question -> `nameserver` recvs() DNS Question via decode()

3. `nameserver` sends integer designating size of DNS Header -> `nameserver` sends DNS Header via encode() -> `nameserver` sends integer designating size of DNS Record -> `nameserver` sends DNS Record via encode()

4. `miProxy` recvs() integer designating size of DNS Header -> `miProxy` recvs() DNS header via decode() -> `miProxy` recvs() integer designating size of DNS Record -> `miProxy` recvs() DNS Record via decode()

**IMPORTANT: Remember to use `htonl` and `ntohl` when sending/receiving integers over the network!**

### Round-Robin Load Balancer
One of the ways you will implement `nameserver` is as a simple round-robin based DNS load balancer. It should take as input a list of video server IP addresses on the command line; it responds to each request to resolve the name `video.cse.umich.edu` by returning the next IP address in the list, cycling back to the beginning when the list is exhausted.

`nameserver` will bind to an IP address and port specified as command line arguments. It responds **only** to requests for `video.cse.umich.edu`; any other requests should generate a response with `RCODE` 3.

Example text file format in `sample_round_robin.txt`:
```
10.0.0.1
10.0.0.2
10.0.0.3
```

> Hint: You should return `10.0.0.1` if you last response was `10.0.0.3` here. What technique can you use for accessing the list in a **circular** manner? 

### Geographic Distance Load Balancer
Next you’ll make your DNS server somewhat more sophisticated. Your load balancer must return the closest video server to the client based on the proxy’s IP address. In the real world, this would be done by querying a database mapping IP prefixes to geographic locations. For your implementation, however, you will be given information in a text file about the entire state of the network, and your server will have to return to a given client its closest geographic server.

The text file will be represented in the following way:
```
NUM_NODES: <number of hosts and switches in the network>
<host_id> <CLIENT|SWITCH|SERVER> <IP address|NO_IP>
(repeats NUM_NODES - 1 times)
NUM_LINKS: <number of links in the network>
<origin_id> <destination_id> <cost>
(repeats NUM_LINKS - 1 times)
```

<img src="github_assets/link-cost.PNG" title="Video CDN in the wild" alt="" width="400" height="155"/>

As an example, the network shown above will have the following text file, `sample_geography.txt`:
```
NUM_NODES: 6
0 CLIENT 10.0.0.1
1 CLIENT 10.0.0.2
2 SWITCH NO_IP
3 SWITCH NO_IP
4 SERVER 10.0.0.3
5 SERVER 10.0.0.4
NUM_LINKS: 5
0 2 1
1 2 1
2 3 1
3 4 6
3 5 1
```
> Hint: This is graph structure. Recall from 281, what algorithm can you use for finding the **shortest path** from client to any server? 

To operate `nameserver`, it should be invoked as follows:

`./nameserver [--geo|--rr] <port> <servers> <log>`

* `--geo` This flag specifies that `nameserver` will operate in the geography/distance based load balancing scheme.
* `--rr` This flag specifies that `nameserver` will operate in the round-robin based load balancing scheme.
* `port` The port on which your server should listen.
* `servers` A text file containing a list of IP addresses, one per line, belonging to content servers if `--rr` is specified. Otherwise, if `--geo` is specified, it will be a text file describing the network topology as explained above.
* `log` The file path to which you should log the messages as described below.

**Exactly one of `--rr` or `--geo` will be specified.**

> *Note: for simplicity, arguments will appear exactly as shown above (for both modes) during testing and grading. Error handling with the arguments is not explicitly tested but is highly recommended. At the very least, printing the correct usage if something went wrong is worthwhile.*

### nameserver Logging
Your DNS server must log its activity in a specific format. If the log specified by the user already exists, your DNS server overwrites the log. *After each* valid DNS query it services, it should append the following line to the log:

`<client-ip> <query-name> <response-ip>`

* `client-ip` The IP address of the client who sent the query.
* `query-name` The hostname the client is trying to resolve.
* `response-ip` The IP address you return in response.

### queryDNS utility
 `queryDNS` (in the starter_code directory) sends a DNS query to `nameserver` (just like a `miProxy` does), and outputs the reponse from DNS server. So you can test your `nameserver` using `queryDNS` without `miProxy`.

 The autograder uses queryDNS for the `nameserver` only test cases, so make sure your code is compatible.

 The command line to use `queryDNS` is:
 ```
$ <path to the binary>/queryDNS <IP of nameserver> <port of nameserver>
 ```

 If everything goes well, you should get responses like `10.0.0.1`, `10.0.0.2` and `10.0.0.3`.

<a name="submission-instr"></a>
## Submission Instructions
Submission to the autograder will be done [here](https://g489.eecs.umich.edu/). You will have 3 submissions per day (once the autograder is released).

To submit:
1. Submit all the files that you are using in your code, including any starter code. All the files should be configured to work in a flat directory structure
2. Submit a Makefile with two rules:
    - make miProxy -> this should produce an executable called miProxxy
    - make nameserver -> this should produce an executable called nameserver


<a name="autograder"></a>
## Autograder
The autograder will be released roughly halfway through the assignment. You are encouraged to design tests by yourselves to fully test your proxy server and DNS server. You should *NEVER* rely on the autograder to debug your code. Clarifications on the autograder will be added in this section.


## Instruction Sheet: Using the AWS AMI for Mininet with VNC and Starter Files

This instruction sheet will guide you through the setup and use of the AWS AMI provided for your Mininet project. You will learn how to access the virtual machine using a VNC client, understand what VNC is, and work with the starter files provided. Follow each step carefully to ensure everything runs smoothly.



### What is VNC?

VNC (Virtual Network Computing) is a system that allows you to remotely control another computer’s desktop environment over a network. It transmits keyboard and mouse input from your local machine to a remote machine and displays the screen of the remote machine on your local machine. In this project, you will use VNC to access the graphical interface of your AWS AMI instance, so you can work with the provided tools, including Mininet.



### Step 1: Launch the AWS AMI Instance
Once you’ve launched the AWS AMI instance from your console, you will need to access its desktop environment using a VNC client.



### Step 2: Launching the VNC Server

1. **Connect to Your AWS Instance:**
   First, SSH into your AWS instance. Open a terminal on your local machine and use the following SSH command to log in:

   ```bash
   ssh -i /path/to/your-key.pem username@your-aws-instance-public-ip
   ```

   - **`ssh`**: This command initiates a Secure Shell session.
   - **`-i /path/to/your-key.pem`**: The `-i` flag specifies the private key to use for authentication.
   - **`username@your-aws-instance-public-ip`**: Replace `username` with the username provided for the AMI and `your-aws-instance-public-ip` with the public IP of your AWS instance.

2. **Start the VNC Server:**
   Once connected to your AWS instance, start the VNC server by running:

   ```bash
   vncserver
   ```

   **Explanation**: The `vncserver` command launches the VNC server. When you run this command as a non-root user (i.e., without `sudo`), it creates a VNC session that runs on a specific display, typically `:1`, which corresponds to port 5901.

   - The password to the VNC server will be set to **eecs489** by default.


### Step 3: SSH Tunneling for VNC Access

Since VNC uses port 5901 (by default for display `:1`), we will create an SSH tunnel to securely forward traffic from your local machine to this port on the AWS instance.

1. **Create an SSH Tunnel:**

   Run the following command in a new terminal window on your local machine:

   ```bash
   ssh -i /path/to/your-key.pem -L 5901:localhost:5901 username@your-aws-instance-public-ip
   ```

   **Explanation**:
   - **`-L 5901:localhost:5901`**: This forwards port 5901 on your local machine to port 5901 on the AWS instance (where the VNC server is running).
   - The `username` and `your-aws-instance-public-ip` should match what you used in Step 2.

   **Expected Output**: After running the SSH tunnel command, you should see no errors and be connected to your AWS instance. It will appear similar to a regular SSH session.



### Step 4: Accessing the VNC Server Using a VNC Client

1. **Open Your VNC Client**:
   Install and launch a VNC client such as **RealVNC** or **TigerVNC**. 
   
   Note: MacOS has a [native VNC client](https://support.apple.com/guide/remote-desktop/virtual-network-computing-access-and-control-apde0dd523e/mac). 

2. **Connect to Your AWS Instance**:
   In the VNC client, connect to `localhost:5901`.

   - **`localhost`**: Refers to your local machine.
   - **`:5901`**: Refers to the port where VNC traffic is being forwarded via the SSH tunnel.

3. **Enter Your VNC Password**:
   When prompted, enter the password you set when starting the VNC server (this will be **eecs489** by default.)


### Step 5: Working with the Starter Files

Once connected via VNC, you will find several starter files, including `chrome` and `webserver.py`. Below is an explanation of each file and how to work with them. 

**NOTE: When testing your project, make sure to run these commands on Mininet hosts rather than directly as the user! ** 

#### 1. Making `chrome` Executable

The `chrome` file is an executable that needs to be made runnable before it can be used. Follow these steps:

1. **Run `chmod +x` to Make `chrome` Executable:**

   ```bash
   chmod +x chrome
   ```

   **Explanation**:
   - **`chmod +x chrome`**: The `chmod` command changes the permissions of the file. The `+x` flag makes the file executable, meaning it can be run as a program.
   - Once this is done, you’ll be able to run `chrome` using `sudo` as shown in the next step.

2. **Run `chrome` as `sudo`:**

   ```bash
   sudo ./chrome
   ```

   **Explanation**:
   - **`sudo`**: This command runs the `chrome` executable with superuser (admin) privileges. Some programs may need elevated permissions to function correctly.
   - **`./chrome`**: The `./` specifies that the program is located in the current directory.



#### 2. Running the `webserver`

Another file in your starter pack is `webserver.py`, a Python script that launches a web server using the Flask framework. This server serves files over a persistent connection.

1. **Run the Web Server:**

   First, run
   
   ```bash
   chmod +x ./launch_webserver
   ```

   to make the webserver script executable.

   Then,
   
   ```bash
   ./launch_webserver
   ```

   **Explanation**:
   - Once the server is running, it will listen on port 80 and serve files over HTTP.
   - Make sure that the directory ```vod``` is in the same folder where you are running the webserver.

   You can access the web server by navigating to `http://10.0.0.x/index.html` (where `x` is the host number) in the chrome web browser from the previous step.



### Step 6: Summary of Commands

- **SSH into AWS**: 
  ```bash
  ssh -i /path/to/your-key.pem username@your-aws-instance-public-ip
  ```
- **Start VNC Server**: 
  ```bash
  vncserver
  ```
- **Create SSH Tunnel**: 
  ```bash
  ssh -i /path/to/your-key.pem -L 5901:localhost:5901 username@your-aws-instance-public-ip
  ```
- **Make `chrome` Executable**:
  ```bash
  chmod +x chrome
  ```
- **Run `chrome` as `sudo`**: 
  ```bash
  sudo ./chrome
  ```
- **Run `webserver`**:
  ```bash
  ./launch_webserver
  ```



## Acknowledgements
This programming assignment is based on Peter Steenkiste's Project 3 from CMU CS 15-441: Computer Networks.
