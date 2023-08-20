# Description
Ceknet is a simple tool for managing network adapters on your Windows local machine. Native for cmd and cygwin only. Requires netsh and psutil module to work properly.

# Background
Linux, especially Kali or Parrot, is like the ultimate cybersecurity superhero, catering to a multitude of security needs and packed with a lot of powerful commands, including all that network magic you can work with through the CLI commmand-line. On the other hand, unlike Linux, Windows boasts a ton of flashy GUI features but falls short on lightweight and straightforward CLI programs. Python is a lifesaver, making ceknet here to fill those gaps as I use it to learn more about networking.

# Used to:
1. Enable or disable network adapters.
2. Check your public IP address.
3. List all network adapters.
4. Display data usage statistics in real-time.
5. Display established network connection in real-time.

# Installation
1. Install python.
2. Install psutil module in cmd terminal:
   ```bash
   pip install psutil
   ```
4. You may create a directory named 'Ceknet' for easy organizing. However, you can basically place it anywhere in the directory you like.
5. Copy the 'ceknet.py' file into the folder. You only need 'ceknet.py'. File with a .lang extension is for translation purposes. If you want it in English, you can ignore or delete the .lang file."
6. Head over to the folder you use and see if ceknet is working:
   ```bash
   python ceknet.py -v
   ```

# How to use:
You can add argument --help for more information.

![Help](images/png1.png)

# Credit
Special thanks to CSbyGB for her amazing pentest research, and to many cybersecurity experts whose blogs I encountered along the way for this amazing journey.

# References:
1. https://docs.python.org/3/library/index.html
2. https://psutil.readthedocs.io/en/latest/
3. https://docs.python.org/3/library/subprocess.html
4. https://learn.microsoft.com/en-us/windows-server/networking/technologies/netsh/netsh-contexts
5. https://csbygb.github.io/
