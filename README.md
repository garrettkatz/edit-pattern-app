# Keylogging IDE

A custom IDE that logs users' keystrokes, and automatically tests Python and JS code on several editable problems.

To run the IDE, go to https://keylogging-ide.web.app/

To replay keystrokes from a previous session, go to https://keylogging-ide.web.app/visualizer.html and enter in the appropriate Session ID.

## Project Structure

The bulk of the code for the project is contained in public/index.html.

Some code for the IDE is in public/database.js. In particular, this file includes all of the commands for reading from and writing to the firebase database.

Most of the code for the keystroke visualizer is in public/visualizer.html, except for the code that reads the firebase data, which is in public/visualizer.js.

All of the problems are contained in the public/problems folder, all of the surveys are contained in the public/surveys folder, and all of the tutorials are contained in the public/tutorials folder.

The list of problems and their order, along with several other experiment options, is contained in public/config.txt, in an easily readable and modifiable format.

## Creating New Problems, Surveys, and Tutorials

If you would like to run an instance of the IDE with different problems, surveys, tutorials, or different config options, you can clone the repository and modify a few files.

### Creating New Problems

The format for creating problem text files is explained in public/problems/template.txt, but we'll walk through it here, as well.

Each problem file contains five distinct sections, each separated by a line with three tildas (i.e. "~~~"). These sections are, from top to bottom: 
* Problem Name
  * If you want the IDE to disable external copying and pasting for this problem, add " STRICT" after the problem name.
* Problem Statement (possibly multi-line)
* Function Signature
  * Exclude the def (Python) or function/curly brackets (JS) at the start of the signature, the IDE will add this depending on which language the user has selected
* Test Cases, One per Line
  * To indicate a secret test case (not directly visible to the user, but still tested), wrap the test data in parentheses.
* Expected Output, One Per Line
  * The correct answer for each test case, in the same order as the test cases
 
All of your new problems should be saved in the public/problems folder.

### Creating New Surveys

Each survey file contains several lines, with one question per line. There are three types of questions: text box, multiple choice, and sliders.

Each line consists of several space-separated tokens.

* To create a text box question, write "TEXTBOX" as the first token, and write the question text, in quotes, as the second token.
* To create a multiple choice questions, write "MC" as the first token, write the question text, in quotes, as the second token, and make each remaining token the answer text for each answer, in quotes.
* To create a slider question, write "SLIDER" as the first token, write the question text, in quotes, as the second token, and write the lower and upper bound of the slider (not in quotes) as the third and fourth tokens, respectively.

All of your new surveys should be saved in the public/surveys folder.

### Creating New Tutorials

The existing tutorials are imported from a previous project of mine, https://coderams.net/tutorials.html

Each tutorial consists of several lines, with each line being wrapped in quotes, and having a comma at the end of the line (this is a byproduct of the formatting of the original CodeRams tutorials, since they were originally contained in a JS array, not a text file, and this may be updated in future versions)

To specify the header size of a line of the tutorial, you can preface the line with either [huge], [big], or [med], depending on which size you want.

To specify a formatted line of code in a tutorial, preface the line with [cd].

All of your new surveys should be saved in the public/tutorials folder.
 
### Updating the Config File

After you've created new problems, tutorials, or surveys, to add them to your project, you'll need to update the config file.

The first line of the config file specifies the name of the survey file to give the user before they start the experiment (without the .txt)

The last line of the config file specifies the name of the survey file to give the user after they finish the experiment (without the .txt)

All of the other lines of the config file specify a problem, in order.

Each line consists of several space-separated tokens. 
* The first token should contain name of the problem file (without the .txt)
* The second token should contain the time limit for the problem, in seconds
* The third token should contain of the name of the survey file to give the user after they finish this problem (without the .txt)
* The fourth token should contain PYTHON, JS, or BOTH, depending on if the user should be allowed to use Python only, JS only, or both languages on this problem, respectively.
* The fifth token is optional and should contain the name of the tutorial file to give the user after they finish the problem and the post-problem survey (without the .txt).

## Writing to a Different Database

If you want to modify and read from your own Firebase database instead of ours, you can do so by changing just a few lines of code.

In database.js, replace lines 10-16 with your relevant Firebase config, instead of ours

If you also want to visualize your data in the visualizer, do the same thing to lines 4-13 of visualizer.js
