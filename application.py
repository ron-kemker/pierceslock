# -*- coding: utf-8 -*-
"""
application.py
By Ronald Kemker
18 Jun 2021

Description: This is the main GUI application for the "Pierce's Lock" 
             Encryption/Decryption Software.

"""

import glob, binascii, os
import tkinter as tk
from tkinter import Frame, Button, Label, Menu, Entry, StringVar, Listbox, \
    Scrollbar
from tkinter.filedialog import askopenfilename,asksaveasfilename,askdirectory
from PIL import ImageTk, Image

from AESCipher import AESCipher, AuthenticationFailed,\
    DecryptionFailed, UnpaddingError, TTLError

from password_manager import PasswordManager

class Application(object):
    
    def __init__(self):
        '''
        The GUI application for Pierce's Lock

        Attributes
        ----------
        window_height : int 
           Pixel height of base application 
        window_width : int 
           Pixel width of base application 
        key_dir : string ('keys/')
           The directory location where the .key files are stored
        version : string 
           The version number of the current software
        last_update : string
           The Date that the last update took place
        window : Tkinter object
           The main application window
        pwm : PasswordManager object
            This is used to add the PasswordManager to the main application
            
        Returns
        -------
        None.        
        '''
        
        self.window_height = 400
        self.window_width = 400
        self.key_dir = os.path.abspath('keys')
        self.version = "0.1.4"
        self.last_update = '21 Nov 2021'

        if os.path.exists('.profile'):
            with open('.profile' , 'r') as f:
                self.key_dir = f.read().split(" ", 1)[-1]
            
            if not os.path.exists(self.key_dir):
                self.key_dir = os.path.abspath('keys')
                
        else:
            with open('.profile', 'w') as f:
                f.write('key_dir '+ self.key_dir)
                
        # Initialize Window
        self.window = tk.Tk()
        self.window.title("Pierce's Lock %s" % self.version)
        self.window.geometry("%dx%d" % (self.window_width, 
                                        self.window_height))        
        
        self.pwm = PasswordManager(self)
        # Draw the menu
        self.draw_main()
        
        # Run the application till closed
        self.window.mainloop()
        
    def draw_menu(self):
        '''
        Draws the main menu (default view)

        Attributes
        ----------
        menu : tkinter Menu object 
           The menu toolbar 
           
        Returns
        -------
        None.
        '''
        
        if hasattr(self, 'menu'):
            self.menu.destroy()
        
        # Build the menu
        self.menu = Menu(self.window)
        self.window.config(menu=self.menu)
        
        fileMenu = Menu(self.menu)
        self.menu.add_cascade(label='File', menu=fileMenu)
        fileMenu.add_command(label='Quit', command=self.quit_prompt)
        
        toolMenu = Menu(self.menu)
        self.menu.add_cascade(label='Tools', menu=toolMenu)
        toolMenu.add_command(label='Main Menu', 
                             command=self.draw_main)        
        toolMenu.add_command(label='Encrypt File', 
                             command=self.encryption_window)
        toolMenu.add_command(label='Decrypt File', 
                             command=self.decryption_window)
        toolMenu.add_command(label='Key Manager', 
                             command=self.key_manager_window)
        
        toolMenu.add_command(label='Password Manager', 
                              command=self.pwm.password_manager_window)        
        
        helpMenu = Menu(self.menu)
        self.menu.add_cascade(label='Help', menu=helpMenu)
        helpMenu.add_command(label='About', command=self.about_window)

    def draw_main(self):
        '''
        Draws the main GUI

        Attributes
        ----------
        window_height : int 
           Pixel height of base application 
        window_width : int 
           Pixel width of base application 
        background_frame : Tkinter Frame object
           The space to draw the app content 
           
        Returns
        -------
        None.
        '''    
        self.window_height = 400
        self.window_width = 400
        self.window.geometry("%dx%d" % (self.window_width, 
                                        self.window_height))
        
        if hasattr(self, 'popup_window'):
            self.popup_window.destroy()
        if hasattr(self, 'background_frame'):
            self.background_frame.destroy()        
        self.draw_menu()
        
        self.background_frame = Frame(self.window, 
                                 width=self.window_width,
                                 height=self.window_height)
        self.background_frame.pack()
        
        label = Label(self.background_frame, 
                      text='Pierce\'s Lock', 
                      font=('Helvetica', 18,'bold'))
        label.place(x=50, y=49, width=300, height=50)
        
        button1 = Button(self.background_frame,
                         text='Encrypt File',
                         command=self.encryption_window)
        button1.place(x=140, y=100, width=120, height=50)

        button2 = Button(self.background_frame,
                         text='Decrypt File',
                         command=self.decryption_window)
        button2.place(x=140, y=151, width=120, height=50)

        button3 = Button(self.background_frame,
                         text='Key Manager',
                         command=self.key_manager_window)
        button3.place(x=140, y=202, width=120, height=50)
        
        button4 = Button(self.background_frame,
                          text='Password Manager',
                          command=self.pwm.password_manager_window)
        button4.place(x=140, y=253, width=120, height=50)

        button5 = Button(self.background_frame,
                         text='Exit',
                         command=self.quit_prompt)
        button5.place(x=140, y=304, width=120, height=50)

    def quit_prompt(self):
        '''
        Helper function for draw_menu function.  Displays a prompt to quit the
        application.
        
        Returns
        -------
        None.
        '''        
        popup_window = tk.Toplevel()
        popup_window.geometry("300x100") 
        popup_window.wm_title("Quit?")
        
        # Background of the popup window
        bkgd_frame = Frame(popup_window, width=300, height=100)
        bkgd_frame.pack()
        
        # Label that displays the prompt
        prompt_txt = "Are you sure you want to quit?"
        prompt = Label(bkgd_frame, text=prompt_txt)
        prompt.place(x=50, y=20, width=200)
        
        # Buttons to save and quit, just quit, and cancel the "quit" 
        # command
        button1 = Button(bkgd_frame, text="Quit", 
                           command=self.window.destroy)
        button1.place(x=49, y=50, width=100, height=30 )        
        
        cancel_button = Button(bkgd_frame, text="Cancel", 
                               command=popup_window.destroy)
        cancel_button.place(x=151, y=50, width=100, height=30)

    def about_window(self):
        '''
        Pop-up window with brief description of the application.
        
        Returns
        -------
        None.
        '''
        popup_window = tk.Toplevel()
        popup_window.geometry("300x500") 
        popup_window.wm_title("About")
        
        # Background of the popup window
        bkgd_frame = Frame(popup_window, width=300, height=500)
        bkgd_frame.pack()
        
        # Label that displays the 
        with open('about.txt' , 'r') as f:
            about_text = f.read()
        
        about_text = about_text % (self.version, self.last_update)
        
        prompt = Label(bkgd_frame, text=about_text, wraplength=200, 
                       justify=tk.LEFT)
        prompt.place(x=50, y=20, width=200)
        
        # Buttons to save and quit, just quit, and cancel the "quit" 
        # command
        button1 = Button(bkgd_frame, text="Close", 
                           command=popup_window.destroy)
        button1.place(x=100, y=450, width=100, height=30 )        


    def encryption_window_new(self):
        '''
        This generates a window to encrypt files

        Attributes:
        -----------
        window_height : int
            The heights of the window
        window_width : int
            The width of the window
        background_frame : tkinter Frame object
            The drawing canvas for the window
        key_path_var : StringVar object
            The entry for the key file
        left_pane : tkinter Listbox object
            The list of possible keys

        Returns
        -------
        None.

        '''
        self.window_height = 600
        self.window_width = 801
        
        self.window.geometry("%dx%d" % (self.window_width, 
                                        self.window_height))
        
        if hasattr(self, 'popup_window'):
            self.popup_window.destroy()
        if hasattr(self, 'background_frame'):
            self.background_frame.destroy()        
        
        self.background_frame = Frame(self.window, 
                                 width=self.window_width,
                                 height=self.window_height)
        self.background_frame.pack()        
        self.draw_menu()
        
        label = Label(self.background_frame,
                      text='File(s) to Encrypt: ')
        label.place(x=0, y=0, width=100, height=30)
        
        self.key_path_var = StringVar()
        path_pane = Entry(self.background_frame, 
                          textvariable=self.key_path_var)
        self.key_path_var.set(self.key_dir)
        path_pane.bind('<Return>', self.update_key_dir)
        path_pane.place(x=100, y=0, width=self.window_width-250, height=30)
        
        button = Button(self.background_frame,
                        text='Browse',
                        command=self.change_key_dir)
        button.place(x=self.window_width-150, y=0, width=150, height=30)
        
        self.left_pane = Listbox(self.background_frame)
        self.left_pane.bind('<<ListboxSelect>>', self.select_key)
        
        self.left_pane.place(x=0, y=31, 
                        width=300, 
                        height=self.window_height)


        for i, key_file in enumerate(glob.glob(self.key_dir + '/*.key')):
            self.left_pane.insert(i, key_file.split('\\')[-1][:-4])
        
        scrollbar = Scrollbar(self.left_pane)
        scrollbar.pack(side = tk.RIGHT, fill = tk.BOTH)
        self.left_pane.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command = self.left_pane.yview)
        
        label = Label(self.background_frame, 
                      text='Encryption Key:', 
                      font=('Helvetica', 12,'bold')
                      )
        label.place(x=355, y=50, width=460, height=30)
        
    
    def encryption_window(self):
        '''
        Loads the encryption menu in the application

        Attributes
        ----------
        window_height : int 
           Pixel height of base application 
        window_width : int 
           Pixel width of base application 
        filepath : string
            The location of the file to be encrypted
        keyfile : string
            The location of the encryption key to be used
        background_frame :Tkinter Frame object
           The space to draw the app content 
        label_status_1 : tkinter Label object
            The label for the status for step 1, i.e., select file to encrypt
        label_status_2 : tkinter Label object
            The label for the status for step 2, i.e., select key file
            
        Returns
        -------
        None.
        '''
        
        self.window_height = 400
        self.window_width = 801
        self.filepath = None
        self.keyfile = None
        
        col2 = int(self.window_width / 3)
        col3 = col2 * 2
        
        row1 = 50
        row2 = 100
        row3 = 150
        
        if hasattr(self, 'background_frame'):
            self.background_frame.destroy()  
        if hasattr(self, 'popup_window'):
            self.popup_window.destroy()            
        self.draw_menu()
        
        self.window.geometry("%dx%d" % (self.window_width, 
                                        self.window_height))
        
        self.background_frame = Frame(self.window, 
                                 width=self.window_width,
                                 height=self.window_height)
        self.background_frame.pack()
        
        label1 = Label(self.background_frame,
                       text='Step 1: Pick file to encrypt', 
                      font=('Helvetica', 12,'bold'))
        label1.place(x=25, y=row1, width=col2 - 50)

        browse_button = Button(self.background_frame, 
                                text='Browse for file',
                                command=self.find_file)
        
        img = Image.open('img/red_x.png')
        img = ImageTk.PhotoImage(img.resize((col2-100, col2-100), 
                                            Image.ANTIALIAS))

        self.label_status_1 = Label(self.background_frame,
                                    image=img)
        self.label_status_1.image = img
        self.label_status_1.place(x=50, 
                                  y=row3, 
                                  width=col2-100, 
                                  height=col2-100)

        browse_button.place(x=25, 
                            y=row2, 
                            width=col2 - 50,
                            height=30)

        label2 = Label(self.background_frame,
                       text='Step 2: Select encryption key', 
                      font=('Helvetica', 12,'bold'))
        label2.place(x=col2 + 20, y=row1, width=col2 - 40)
        
        browse_button = Button(self.background_frame, 
                                text='Browse for key',
                                command=self.find_key)
        
        browse_button.place(x=col2 + 25, 
                            y=row2, 
                            width=col2 - 50,
                            height=30)

        self.label_status_2 = Label(self.background_frame,
                                    image=img)
        self.label_status_2.image = img
        self.label_status_2.place(x=col2+50, 
                                  y=row3, 
                                  width=col2-100, 
                                  height=col2-100)
        
        label3 = Label(self.background_frame,
                       text='Step 3: Encrypt File', 
                      font=('Helvetica', 12,'bold'))
        label3.place(x=col3+25, y=row1, width=col2 - 50)
        
        button = Button(self.background_frame, 
                                text='Encrypt',
                                command=self.encrypt)
        
        button.place(x=col3 + 25, 
                    y=row2, 
                    width=col2 - 50,
                    height=30)
        
        button = Button(self.background_frame,
                             text='<<< Back to Main Menu',
                             command=self.draw_main)
        
        button.place(x=5, y=self.window_height - 35, width=150, height=30)

    def encrypt(self):
        '''
        Helper function for encryption_window.  This function uses 
        AESCipher.py to encrypt the file.
        
        Attributes
        ----------
        popup_window : tkinter TopLevel object 
           This popup window is the prompt once encryption is complete
           
        Returns
        -------
        None.              
        '''
        
        if self.filepath and self.keypath:
            
            savepath = asksaveasfilename(filetypes=(("CMF File", 
                                                         ['.cmf']),),
                                             initialdir = '', 
                                             title = "Save encrypted file")
            
            if not savepath:
                return
            
            cipher = AESCipher()
            
            with open(self.keypath, "r") as f:
                key = f.read()
            
            key = binascii.unhexlify(key)
            ciphertext, signing_key = cipher.encrypt_file(self.filepath, key)
            
            file_ext = self.filepath.split('.')[-1].upper()

            if savepath[-4:] != '.cmf':
                savepath = savepath+'_'+ file_ext + '.cmf'
                
            else:
                savepath = savepath[:-4] + '_' + file_ext + '.cmf'
                
            with open(savepath , "wb") as f:
                f.write(signing_key + ciphertext)
       
            self.popup_window = tk.Toplevel()
            self.popup_window.geometry("300x100") 
            self.popup_window.wm_title("Encryption Successful")
            
            # Background of the popup window
            bkgd_frame = Frame(self.popup_window, width=300, height=100)
            bkgd_frame.pack()
            
            # Label that displays the prompt
            prompt_txt = "Encryption successful.  Encrypt another file?"
            prompt = Label(bkgd_frame, text=prompt_txt)
            prompt.place(x=25, y=20, width=250)
            
            # Buttons to save and quit, just quit, and cancel the "quit" 
            # command
            button = Button(bkgd_frame, text="Yes", 
                               command=self.encryption_window)
            button.place(x=49, y=50, width=100, height=30 )        
            
            button = Button(bkgd_frame, text="No", 
                                   command=self.draw_main)
            button.place(x=151, y=50, width=100, height=30)

    def find_file(self):
        '''
        Helper function for encryption_window.  This function finds the file 
        (Step 1) to be encrypted.  If a file is selected, it changes the 
        label_status_1 to a green check mark.
        
        Attributes
        ----------
        filepath : string 
           This is the path to the file that will be encrypted.
        label_status_1 : tkinter Label object
            The label for the status for step 1, i.e., select file to encrypt
        
        Returns
        -------
        None.
        '''
        
        self.filepath = askopenfilename(initialdir = '', 
                                title = "Select file")
        
        if self.filepath:
            col2 = int(self.window_width / 3)

            img = Image.open('img/green_check.png')
            img = ImageTk.PhotoImage(img.resize((col2-100, col2-100), 
                                                Image.ANTIALIAS))
            
            self.label_status_1.destroy()
            self.label_status_1 = Label(self.background_frame,
                                        image=img)
            self.label_status_1.img = img
            self.label_status_1.place(x=50, 
                                  y=150, 
                                  width=col2-100, 
                                  height=col2-100)
            
    def find_key(self):
        '''
        Helper function for encryption_ and decryption_window.  This function 
        finds the .key file (Step 2) to be used.  If a file is selected, it 
        changes the label_status_2 to a green check mark.
        
        Attributes
        ----------
        keypath : string 
           This is the path to the key file
        label_status_2 : tkinter Label object
           The label for the status for step 2, i.e., select key file
           
        Returns
        -------
        None.
        '''
        
        self.keypath = askopenfilename(filetypes=(("KEY File", ['.key']),),
                                initialdir = self.key_dir, 
                                title = "Select encrpytion key")

        if self.keypath:
            col2 = int(self.window_width / 3)

            img = Image.open('img/green_check.png')
            img = ImageTk.PhotoImage(img.resize((col2-100, col2-100), 
                                                Image.ANTIALIAS))
            
            self.label_status_2.destroy()
            self.label_status_2 = Label(self.background_frame,
                                        image=img)
            self.label_status_2.img = img
            self.label_status_2.place(x=col2+50, 
                                  y=150, 
                                  width=col2-100, 
                                  height=col2-100)
    
    def decryption_window(self):
        '''
        Loads the decryption menu in the application

        Attributes
        ----------
        window_height : int 
           Pixel height of base application 
        window_width : int 
           Pixel width of base application 
        filepath : string
            The location of the file to be decrypted
        keyfile : string
            The location of the decryption key to be used
        background_frame : Tkinter Frame object
           The space to draw the app content 
        label_status_1 : tkinter Label object
            The label for the status for step 1, i.e., select file to decrypt
        label_status_2 : tkinter Label object
            The label for the status for step 2, i.e., select key file
            
        Returns
        -------
        None.
        '''        
        self.window_height = 400
        self.window_width = 801
        self.filepath = None
        self.keyfile = None
        
        col2 = int(self.window_width / 3)
        col3 = col2 * 2
        
        row1 = 50
        row2 = 100
        row3 = 150
        
        if hasattr(self, 'background_frame'):
            self.background_frame.destroy()  
        if hasattr(self, 'popup_window'):
            self.popup_window.destroy()            
        self.draw_menu()
        
        self.window.geometry("%dx%d" % (self.window_width, 
                                        self.window_height))
        
        self.background_frame = Frame(self.window, 
                                 width=self.window_width,
                                 height=self.window_height)
        self.background_frame.pack()
        
        label1 = Label(self.background_frame,
                       text='Step 1: Select file to decrypt', 
                      font=('Helvetica', 12,'bold'))
        label1.place(x=25, y=row1, width=col2 - 50)

        browse_button = Button(self.background_frame, 
                                text='Browse for file',
                                command=self.find_cmf_file)
        
        img = Image.open('img/red_x.png')
        img = ImageTk.PhotoImage(img.resize((col2-100, col2-100), 
                                            Image.ANTIALIAS))

        self.label_status_1 = Label(self.background_frame,
                                    image=img)
        self.label_status_1.image = img
        self.label_status_1.place(x=50, 
                                  y=row3, 
                                  width=col2-100, 
                                  height=col2-100)

        browse_button.place(x=25, 
                            y=row2, 
                            width=col2 - 50,
                            height=30)

        label2 = Label(self.background_frame,
                       text='Step 2: Select encryption key', 
                      font=('Helvetica', 12,'bold'))
        label2.place(x=col2 + 20, y=row1, width=col2 - 40)
        
        browse_button = Button(self.background_frame, 
                                text='Browse for key',
                                command=self.find_key)
        
        browse_button.place(x=col2 + 25, 
                            y=row2, 
                            width=col2 - 50,
                            height=30)

        self.label_status_2 = Label(self.background_frame,
                                    image=img)
        self.label_status_2.image = img
        self.label_status_2.place(x=col2+50, 
                                  y=row3, 
                                  width=col2-100, 
                                  height=col2-100)
        
        label3 = Label(self.background_frame,
                       text='Step 3: Decrypt File', 
                      font=('Helvetica', 12,'bold'))
        label3.place(x=col3+25, y=row1, width=col2 - 50)
        
        button = Button(self.background_frame, 
                                text='Decrypt',
                                command=self.decrypt)
        
        button.place(x=col3 + 25, 
                    y=row2, 
                    width=col2 - 50,
                    height=30)
        
        button = Button(self.background_frame,
                             text='<<< Back to Main Menu',
                             command=self.draw_main)
        
        button.place(x=5, y=self.window_height - 35, width=150, height=30)  
        
    def decrypt(self):
        '''
        Helper function for decryption_window.  This function uses AESCipher.py
        to decrypt the file.
        
        Attributes
        ----------
        popup_window : tkinter TopLevel object 
           This popup window is the prompt once decryption is complete
           
        Returns
        -------
        None.              
        '''
        if self.filepath and self.keypath:
            
            savepath = asksaveasfilename(initialdir = '', 
                                             title = "Save decrypted file")
            
            if not savepath:
                return
            
            cipher = AESCipher()
            
            with open(self.keypath, "r") as f:
                key = f.read()
            
            key = binascii.unhexlify(key)
            
            with open(self.filepath, "rb") as f:
                msg = f.read()
                signing_key = msg[:16]
                ciphertext = msg[16:]
                                 
            try:
                ciphertext, iv = cipher.authenticate(ciphertext, signing_key)
            except TTLError:
                self.one_button_popup("TTL Failure",
                            "The message's time-to-live (TTL) has expired.")
                return
            except AuthenticationFailed:
                self.one_button_popup("Authentication Failed",
                                      "Message Authentication has Failed")                
                return
            
            try:
                deciphertext = cipher.decrypt(ciphertext, key, iv)
            except DecryptionFailed:
                self.one_button_popup("Decryption Failed",
                                      "Message Decryption has Failed")                
                return                
            except UnpaddingError:
                self.one_button_popup("Unpadding Failed",
                            "Message unpadding after decryption has failed.")                
                return              
            
            file_ext = self.filepath.split('_')[-1].split('.')[0].lower()
            with open(savepath + '.' + file_ext, 'wb') as f:
                f.write(deciphertext)
            
            self.popup_window = tk.Toplevel()
            self.popup_window.geometry("300x100") 
            self.popup_window.wm_title("Decryption Successful")
            
            # Background of the popup window
            bkgd_frame = Frame(self.popup_window, width=300, height=100)
            bkgd_frame.pack()
            
            # Label that displays the prompt
            prompt_txt = "Decryption successful.  Decrypt another file?"
            prompt = Label(bkgd_frame, text=prompt_txt)
            prompt.place(x=25, y=20, width=250)
            
            # Buttons to save and quit, just quit, and cancel the "quit" 
            # command
            button = Button(bkgd_frame, text="Yes", 
                               command=self.encryption_window)
            button.place(x=49, y=50, width=100, height=30 )        
            
            button = Button(bkgd_frame, text="No", 
                                   command=self.draw_main)
            button.place(x=151, y=50, width=100, height=30)    

    def find_cmf_file(self):
        '''
        Helper function for decryption_menu.  This function finds the .cmf file 
        (Step 1) to be decrypted.  If a file is selected, it changes the 
        label_status_1 to a green check mark.
        
        Attributes
        ----------
        filepath : string 
           This is the path to the file that will be decrypted.
        label_status_1 : tkinter Label object
           The label for the status for step 1, i.e., select file to decrypt
           
        Returns
        -------
        None.
        '''
        self.filepath = askopenfilename(filetypes=(("CMF File", ['.cmf']),),
                                        initialdir = '', 
                                title = "Select file")
        
        if self.filepath:
            col2 = int(self.window_width / 3)

            img = Image.open('img/green_check.png')
            img = ImageTk.PhotoImage(img.resize((col2-100, col2-100), 
                                                Image.ANTIALIAS))
            
            self.label_status_1.destroy()
            self.label_status_1 = Label(self.background_frame,
                                        image=img)
            self.label_status_1.img = img
            self.label_status_1.place(x=50, 
                                  y=150, 
                                  width=col2-100, 
                                  height=col2-100)
     
    def key_manager_window(self):
        '''
        Opens the key management window in the application

        Attributes
        ----------
        window_height : int 
           Pixel height of base application 
        window_width : int 
           Pixel width of base application 
        background_frame : Tkinter Frame object
           The space to draw the app content
        left_pane : tkinter Frame object
           The frame that shows the list of keys in the directory of choice
        key_var : tkinter StringVar object
            The variable that contains what is present in the entry text box
            
        Returns
        -------
        None.
        '''
        self.window_height = 600
        self.window_width = 1000
        self.window.geometry("%dx%d" % (self.window_width, 
                                        self.window_height))
        
        if hasattr(self, 'popup_window'):
            self.popup_window.destroy()
        if hasattr(self, 'background_frame'):
            self.background_frame.destroy()        
        self.draw_menu()
        
        self.background_frame = Frame(self.window, 
                                 width=self.window_width,
                                 height=self.window_height)
        self.background_frame.pack()
        
        
        label = Label(self.background_frame,
                      text='Key Directory: ')
        label.place(x=0, y=0, width=100, height=30)
        
        self.key_path_var = StringVar()
        path_pane = Entry(self.background_frame, 
                          textvariable=self.key_path_var)
        self.key_path_var.set(self.key_dir)
        path_pane.bind('<Return>', self.update_key_dir)
        path_pane.place(x=100, y=0, width=self.window_width-250, height=30)
        
        button = Button(self.background_frame,
                        text='Browse Working Directory',
                        command=self.change_key_dir)
        button.place(x=self.window_width-150, y=0, width=150, height=30)
        
        self.left_pane = Listbox(self.background_frame)
        self.left_pane.bind('<<ListboxSelect>>', self.select_key)
        
        self.left_pane.place(x=0, y=31, 
                        width=300, 
                        height=self.window_height)


        for i, key_file in enumerate(glob.glob(self.key_dir + '\\*.key')):
            self.left_pane.insert(i, key_file.split('\\')[-1][:-4])
        
        scrollbar = Scrollbar(self.left_pane)
        scrollbar.pack(side = tk.RIGHT, fill = tk.BOTH)
        self.left_pane.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command = self.left_pane.yview)
        
        label = Label(self.background_frame, 
                      text='Encryption Key:', 
                      font=('Helvetica', 12,'bold')
                      )
        label.place(x=355, y=50, width=460, height=30)
        
        self.key_var = StringVar()
        key_entry = Entry(self.background_frame, textvariable=self.key_var)
        key_entry.place(x= 355, y=81, width=460, height=30)         
                    
        button = Button(self.background_frame, 
                        text='Generate Random Key',
                        command=self.generate_key)
        button.place(x=355, y=120, width=150, height=50)
        
        button = Button(self.background_frame, 
                        text='Save Key',
                        command=self.add_key)
        button.place(x=510, y=120, width=150, height=50)        

        button = Button(self.background_frame, 
                        text='Delete Key',
                        command=self.delete_key_prompt)
        button.place(x=665, y=120, width=150, height=50) 

        button = Button(self.background_frame,
                             text='<<< Back to Main Menu',
                             command=self.draw_main)
        button.place(x=575, y=540, width=150, height=50)


    def select_key(self, event):
        '''
        Helper function for key_manager_window.  This read and prints the 
        key of the .key file selected in the left_pane.

        Parameters
        ----------
        event : tkinter event object
            This contains the listener object for the key manager's left_pane
        
        Attributes
        ----------
        popup_window : tkinter TopLevel object
            The popup for the key selection tool
        
        Returns
        -------
        None.
        '''
        ii = self.left_pane.curselection()
        filename = self.left_pane.get(ii)
        
        with open(self.key_dir + '\\%s.key' % filename, 'rb') as f:
            key = f.read()
            
        self.key_var.set(key.decode('utf-8'))

    def delete_key_prompt(self):
        '''
        Helper function for key_manager_window.  Provide a prompt whether to 
        not or to delete the selected key.

        Attributes
        ----------
        popup_window : tkinter TopLevel object
            The popup for the key selection tool
        
        Returns
        -------
        None.
        '''
        
        self.popup_window = tk.Toplevel()
        self.popup_window.geometry("300x100") 
        self.popup_window.wm_title("Delete Key?")
        
        # Background of the popup window
        bkgd_frame = Frame(self.popup_window, width=300, height=100)
        bkgd_frame.pack()
        
        # Label that displays the prompt
        prompt_txt = "Are you sure you want to delete this key?" 
        prompt = Label(bkgd_frame, text=prompt_txt)
        prompt.place(x=25, y=20, width=250)
        
        # Buttons to save and quit, just quit, and cancel the "quit" 
        # command
        button = Button(bkgd_frame, text="Yes", 
                           command=self.delete_key)
        button.place(x=49, y=50, width=100, height=30 )        
        
        button = Button(bkgd_frame, text="No", 
                               command=self.popup_window.destroy)
        button.place(x=151, y=50, width=100, height=30)          


    def delete_key(self):
        '''
        Helper function for key_manager_window.  This delete the selected
        .key file
        
        Returns
        -------
        None.
        '''
        
        ii = self.left_pane.curselection()
        filename = self.left_pane.get(ii)

        os.remove(self.key_dir + '\\%s.key' % filename)
        self.popup_window.destroy()
        self.key_manager_window()
        

    def add_key(self):
        '''
        Helper function for key_manager_window.  This creates a new .key file
        for the key typed or generated in the Entry box.
        
        Attributes
        ----------
        new_key : string
            The new key that will be added
        
        Returns
        -------
        None.
        '''
        
        self.new_key = self.key_var.get()

        savepath = asksaveasfilename(filetypes=(("KEY File", ['.key']),),
                                             initialdir = '', 
                                             title = "Save key")
            
        if not savepath:
            return

        with open(savepath + '.key' , "w") as f:
            f.write(self.new_key)
            
        self.key_manager_window()
            
    def one_button_popup(self, title, msg):
        '''
        Display a message pop-up with a close button

        Parameters
        ----------
        title : string
            The title bar message (should be  short).
        msg : string
            The detailed message to get displayed.
        
        Returns
        -------
        None.
        '''
        
        popup_window = tk.Toplevel()
        popup_window.geometry("300x100") 
        popup_window.wm_title(title)
        
        # Background of the popup window
        bkgd_frame = Frame(popup_window, width=300, height=100)
        bkgd_frame.pack()
        
        # Label that displays the prompt            
        prompt = Label(bkgd_frame, text=msg)
        prompt.place(x=25, y=20, width=250)
        
        # Buttons to save and quit, just quit, and cancel the "quit" 
        # command
        button = Button(bkgd_frame, text="Close", 
                           command=popup_window.destroy)
        button.place(x=100, y=50, width=100, height=30 ) 

    
    def generate_key(self):
        '''
        Helper function for key_manager_window.  This generates a new random
        encryption key.
        
        Attributes
        ----------
        new_key : byte string 
           The new random key being generated
        
        Returns
        -------
        None.
        '''
        self.new_key = binascii.hexlify(os.urandom(32))
        self.key_var.set(self.new_key.decode('utf-8'))

    def update_key_dir(self, event):
        '''
        Helper function for key_manager_window.  This updates the directory
        path using the entry box.

        Parameters
        ----------
        event : tkinter event object
            This contains the listener obj for the key manager's key_path_var
            
        Attributes
        ----------
        key_dir : string 
            This is the path to the key directory.
        
        Returns
        -------
        None.
        '''
        new_key_dir = self.key_path_var.get()
        
        if os.path.exists(new_key_dir):
            self.key_dir = new_key_dir
            self.key_manager_window()
        else:
            
            popup_window = tk.Toplevel()
            popup_window.geometry("300x100") 
            popup_window.wm_title("Invalid Path")
            
            # Background of the popup window
            bkgd_frame = Frame(popup_window, width=300, height=100)
            bkgd_frame.pack()
            
            # Label that displays the prompt            
            prompt_txt = "This path does not exist."
            prompt = Label(bkgd_frame, text=prompt_txt)
            prompt.place(x=25, y=20, width=250)
            
            # Buttons to save and quit, just quit, and cancel the "quit" 
            # command
            button = Button(bkgd_frame, text="Close", 
                               command=popup_window.destroy)
            button.place(x=100, y=50, width=100, height=30 )
            
            self.key_manager_window()            

    def change_key_dir(self):
        '''
        Helper function for key_manager_window.  This opens a browse window 
        to select a new key directory to display.
        
        Attributes
        ----------
        key_dir : string 
           This is the path to the key directory.

        Returns
        -------
        None.
        '''
        
        new_key_dir = askdirectory(initialdir = self.key_dir, 
                                    title = "Change Key Directory")
        
        if new_key_dir:
            self.key_dir = new_key_dir.replace('/', '\\')
            
            with open('.profile', 'w') as f:
                f.write('key_dir '+self.key_dir)
                
            self.key_manager_window()

if __name__ == "__main__":
    Application()                

  