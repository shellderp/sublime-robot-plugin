sublime-robot-plugin
====================
This project is a plugin for Sublime Text 2 that provides some conveniences for working with Robot Framework test files (.txt only).

Installation
------------

The easiest way to install is to use [Package Control](http://wbond.net/sublime_packages/package_control) and search for 'Robot Framework'.

Otherwise, open Sublime Text 2 and click `Preferences -> Browse Packages` to open the packages directory. Then create a directory named `Robot Framework` containing the contents of this repository.

Features
--------

* Syntax highlighting for Robot txt files, plus automatic detection/activation
* alt+enter or alt+click to:
    * go to resource file at caret
    * go to user keyword at caret
    * go to builtin keyword at caret (opens browser)
* ctrl+space to auto complete user keywords (must start on first word of keyword since sublime will break on spaces)
* search for keywords in all project robot files (open folders)
* run script from Cmd+B
* Toggle Comments with Cmd+/

Screenshots
-----------
<img src="http://i.imgur.com/LrEbNr9.png" />
