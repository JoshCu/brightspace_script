# brightspace_script

 1) Download all from brightspace into a zip file

2) Put the sorter script into the same folder as the zip downloaded straight from brightspace

3) python3 sorter.py

This will extract the brightspace folder into a new folder named automatically after the assignment / lab.

Recursively unzip and zip files the students might have uploaded.

Automatically search for the latest cpp file and compile it

Write the results to a file called results.csv and an easier to read result.html table, within the folder for the assignment / lab

Then move the main zips to a folder called "zips" for archiving


## Just auto compiling
To just run the auto compiliation, copy auto-compiler.py into the folder with all the student submissions and run it in there.