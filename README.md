# 3CU
A small organizational tool: categorizes files in folders, combines folder content, cleans up folder content.

The software has been built in Python 3.5 , on Windows 32-bit machine. The distribution covers this combination.

Now, a surface description of 3CU.

The "Categorize" function iterates through the files of a directory, checks which categories of files are present (video, audio, etc.), creates the corresponding category folders inside the target directory, and moves each file to the corresponding category folder.

The "Combine" function takes two or more directories and combines their content.

The "Clean Up" function checks through the content of a directory and eliminates: empty files and folders, duplicate files, and redundant folders. 

The program interface includes the description of each of these functions, along with the description of all the available special modes and methods, the exceptions, the limitations, etc. 

Aditionally, a descriptional video will be available on Youtube shortly. Also, I plan to make an illustrated guide to using 3CU.

PyQT has been used to develop the GUI part of the application, and PyInstaller has been used to build the executable.

A small tool, because I haven't covered multithreading yet (planning to do so in the future). So the application may freeze when dealing with large quantities of data, but if it isn't prematurely closed, it generally gets the job done. 
