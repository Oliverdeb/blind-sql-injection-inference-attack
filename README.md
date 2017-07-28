# Blind SQL Injection script to automate an inference attack
  This script was creating during a two week internship. The goal was to dump all user names and password hashes from a database by inferring the data based on certain responses from the server.
  
This script supports both **time** based and **boolean** based inference attacks:
* Time based works by having the server sleep when the SQL injection was sucessful, otherwise don't sleep. The response time from the server can then be measured to determine whether the query was succesful.  
    + Query used: <code> select * from users where username like ' <b> guess%' and sleep(1) -- -</b> </code> where the bold is the injected SQL. I measure the time taken for the query to execute and if it is longer than the "sleep" time then the guess was correct else the server would have not taken that long to recover.
* Boolean based works by either successfully logging in or not  
    + Query used: <code> select * from users where username like ' <b> guess%' -- -</b> </code> where the bold is the injected SQL, so for this there is no sleeping. I examine the body of the HTTP repsonse returned by the server to determine if the log in was succesful or not. If the log in was successful the guess would have been correct.
