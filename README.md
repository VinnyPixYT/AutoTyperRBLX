# AutoTyperRBLX
This is a script where you can type any words that are outputted via audio really fast with a macro!

<details>
  <summary>DISCLAIMER</summary>

  - DO NOT USE THIS SCRIPT IN GAMES WITH MACRO DETECTION (eg. Spelling Bee by Bean's Can). THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM “AS IS” WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. This is for educational purposes only, and has been tested in Scary Spelling.
</details>

## Setup Instructions
#1: Click the green "Code" box on the repo, then "Download ZIP."
#2. Extract the zip. Our most important files for now will be "autotyper.py" and "requirements.txt"
#3. Download Virtual Cable if you haven't already: https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack45.zip
#4. Once that's successfully installed, press Windows + R, and type cmd. Click Enter.
ENSURE YOU HAVE PYTHON INSTALLED FOR THE ENTIRETY REST OF THE PROCESS!
#5. Type cd /d "extracted folder destination" (don't include these things ("))
#6: Type "pip install -r requirements.txt". Keep the command prompt window open, feel free to close it when the process successfully finishes.
#7. Open the "autotyper.py" file in any code editor, whether it be IDLE, Virtual Studio Code, etc.
#8. Replace the Tesseract-OCE location in line 66 with your actual Tesseract-OCE.exe location. You may need to do some exploring around your C:\ files.
#9. Replace the "save_dir" location in line 39 to a folder directory of your choosing.
#10. Save the code, and exit your coding software.
#11. Join a Google Meet on your browser.
#12. Copy the link from the meet, and paste it into another tab, or browser, and on that other instance, join with another account.
#13. Choose an account to mainly use the script for. Enable it's microphone ONLY. Make it's microphone VB Cable Input.
#14. On the other account, disable EVERYTHING. Make the microphone something that isn't transmitting audio just in case, and make the speakers your TV, speakers, or headphones.
#15. On the second instance, open a new tab. A popup containg the Meet should appear. If there is a duplicate or more than one, close it until you have one.
#16. On the popup, click the hamburger menu (3 lines), scroll down, and enable "Turn on Captions."
#17. On your operating system, make your audio output device your VB Cable Output.
#18. Open a site to test the audio (eg. https://translate.google.com). Type a word, then hit the speakers icon near the bottom of the left box. It should output audio back to you.
#19. Make the Google Meet popup near the top-middle quadrant of the screen. Make it's window wide, but small so there's only, always, one line of captions. Zoom in it or out using Control and +/- if needed.
#20. Open the script in IDLE or your programming software, and run it.
#21. With the test you did on a site, press Windows + R to open a test run dialog bux, then press F1 or Fn + 1, dpeending on your keyboard. It should output it on ~850 WPM pace. This variable may be changed if the user has enough "coding experience."
#22. If you somehow manged to follow through correctly, it should type normally. If it didn't, or only typed a part of the word, go to your image destination folder and check to see if the full word is there, or if it's incorrectly cropped. Keep in mind that this script can only output one word at a time for reasons that are too complicated and long to explain casually. This script will sometimes forget the letter at the start/end of words. That's an issue we're aware about.
#23. Launch a game like Scary Spelling, press F1 when the full word is apparent in the captions, and destory the competition. Be careful to read the disclaimer, as it states to not use this script in games that have moderate or expertise macro detection. I'm using Scary Spelling as an example, because that game has literally NO macro detection.
