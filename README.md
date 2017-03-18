# README #

[TOC]

## Introduction
This is about a script I use to gather and decode serial data from my Tektronix TDS2014B (two channel) Digital Oscilloscope.
The oscilloscope is connected to gather TWI, SPI or RS232 data and the script acquires and decodes to a human readable format.

The output provided is:

* ASCII decode on command line
* CSV file to check on Excel or any other compatible tool
* Recently added VCD format to use with GTKWave

This is a command line tool, without any GUI.


## What is this repository for? ##

Quick Summary
This is the development repository of the script with all sources needed to run or modify the tool.
In addition the modules of this script were developed with TDD methodology.

Version
Check repo for latest version

Tutorials
NA

### How do I get set up? ###

* Summary of set up

Go ahead and try:

```
$ hg clone https://ialexo@bitbucket.org/ialexo/cofilos-linux-dev cofilos
```

This will clone this repository to cofilos folder in your system.
Note that you have to use your own user name and password.

Also make sure that gcc (or min-gw) are properly installed and in your path.

### CppUTest Framework Compilation ###

This step is done once. You do not need to do it again afterwards.

#### For CppUTest Framework 3.8 under Windows/Linux: ####

 1. Open an MSYS shell. (Not applicable for linux, ignore this statement)
 2. cd down to cofilos folder

```
cd CppUTest
chmod u+x configure (if needed)
./configure "CFLAGS=-m32" "CXXFLAGS=-m32" "LDFLAGS=-m32"
make
```

This will create the CppUTest Libraries under CppUTest/lib.
For Windows you do not need MSYS prompt anymore. Compile COFILOS as usual (through Command Prompt and mingw).


#### For CppUTest Framework 2.3 under Windows/Linux: ####

Next cd into the folder and dive into the CppUTest framework.
We need to build the libraries for the TDD framework.
(Windows use Command prompt)

```
$ cd cofilos/CppUTest
$ make test
$ make extensions
```

The framework will compile and then run its own test cases.
The first make creates the basic functions, the second provides the extensions.

### COFILOS development and test ###
(Windows use Command prompt)

Next go to the root folder and build COFILOS.
```
$ cd ..
$ make BUILD=OS
```

or you can use:
```
$ cd ..
$ make cofilos
```

The system will build and run its test cases. Normally no test case errors should occcur.

* Configuration

## Dependencies: ##

### Target (ColdFire): ###
* CodeWarrior Eclipse 10.4 (FreeScale, Coldfire)
* FunkOS R3 (included) with ColdFire port

### TDD Environment: ###
* Eclipse (LUNA, MARS.2)
* min-gw (Windows)
* gcc (Linux)
* [CppUTest](http://cpputest.github.io/)
* [Hg (Mercurial)](https://www.mercurial-scm.org/)
* [Doxygen](http://www.stack.nl/~dimitri/doxygen/) 
* [MSCGen](http://www.mcternan.me.uk/mscgen/) 

### Eclipse Plugins ###

* [Doxygen Plugin](doxygen: http://download.gna.org/eclox/update/)
* [Myln Plugin](http://download.eclipse.org/mylyn/incubator/4.4)
* [AnyEdit Tools](AnyEdit Tools: http://andrei.gmxhome.de/eclipse/)
* [BitBucket](http://babelserver.org/mylyn-bitbucket/)

### Documentation ###
In Eclipse, go to Windows-Preferences.
In the filter on the top write 'doxygen'.

Clicking on Doxygen you should see the doxygen version installed (you must install doxygen).

On the editor The workspace default should be doxygen. Thus Eclipse will help you with the doxygen formated comments.

![Eclipse-Doxygen.jpg](https://bitbucket.org/repo/XBXBMo/images/1194398750-Eclipse-Doxygen.jpg)


### How to run tests ###
**Command Line:**

Open a Shell or Command Prompt inside CoFILOS-Linux-Dev
Write:

```
$ make BUILD=OS
```
or
```
$ make cofilos
```

**Eclipse Run:**

Through Eclipse/gdb you may run and debug the code (as usual).

If a test fails, press YES on the prompt to proceed albeit the errors (make failed on Tests not on compilation).

Through C++ Unit Testing, 

 * go to Debug->C/C++ Testing
 * New configuration
 * Set TestExe
 * Set Test Framework to CppUTest
 * Debug



## Contribution guidelines ##

Please see the WiKi pages.

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
[Ilias](https://bitbucket.org/ialexo/)

* Other community or team contact
[Apostolis](https://bitbucket.org/akatran/)