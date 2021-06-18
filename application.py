# -*- coding: utf-8 -*-
"""
application.py
By Ronald Kemker
14 Jun 2021

Description: This is the main GUI application for the "Pierce's Lock" 
             Encryption/Decryption Software.

"""

import tkinter as tk
from tkinter import Frame, Button, Label, Menu, Entry, StringVar, Listbox, \
    Scrollbar
from tkinter.filedialog import askopenfilename,asksaveasfilename,askdirectory
from PIL import ImageTk, Image
import glob, base64

from AESCipher import AESCipher

class Application(object):
    
    def __init__(self):

        self.window_height = 400
        self.window_width = 400
        self.key_dir = 'keys'
        self.version = "0.1"
        self.last_update = '18 Jun 2021'
        
        self.window = tk.Tk()
        self.window.title("Pierces Lock 0.1")  # to define the title
        self.window.geometry("%dx%d" % (self.window_width, 
                                        self.window_height))        
        
        menu = Menu(self.window)
        self.window.config(menu=menu)
        
        fileMenu = Menu(menu)
        menu.add_cascade(label='File', menu=fileMenu)
        fileMenu.add_command(label='Quit', command=self.quit_prompt)
        
        toolMenu = Menu(menu)
        menu.add_cascade(label='Tools', menu=toolMenu)
        toolMenu.add_command(label='Encrypt File', 
                             command=self.encryption_window)
        toolMenu.add_command(label='Decrypt File', 
                             command=self.decryption_window)
        toolMenu.add_command(label='Key Manager', 
                             command=self.key_manager_window)
        
        helpMenu = Menu(menu)
        menu.add_cascade(label='Help', menu=helpMenu)
        helpMenu.add_command(label='About', command=self.about_window)
        
        self.draw_menu()
        self.window.mainloop()

    def draw_menu(self):
            
        self.window_height = 400
        self.window_width = 400
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
        
        
        label = Label(self.background_frame, 
                      text='Pierces Lock', 
                      font=('Helvetica', 18,'bold'))
        label.place(x=50, y=49, width=300, height=50)
        
        button1 = Button(self.background_frame,
                         text='Encrypt File',
                         command=self.encryption_window)
        button1.place(x=150, y=100, width=100, height=50)

        button2 = Button(self.background_frame,
                         text='Decrypt File',
                         command=self.decryption_window)
        button2.place(x=150, y=151, width=100, height=50)

        button3 = Button(self.background_frame,
                         text='Key Manager',
                         command=self.key_manager_window)
        button3.place(x=150, y=202, width=100, height=50)
        
        button4 = Button(self.background_frame,
                         text='Exit',
                         command=self.quit_prompt)
        button4.place(x=150, y=253, width=100, height=50)

    def about_window(self):
        
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
        

    
    def encryption_window(self):
        
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
                             command=self.draw_menu)
        
        button.place(x=5, y=self.window_height - 35, width=150, height=30)
    
    def decryption_window(self):
        
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
                             command=self.draw_menu)
        
        button.place(x=5, y=self.window_height - 35, width=150, height=30)  
        
        
    def key_manager_window(self):
        self.window_height = 600
        self.window_width = 600
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
        
        
        label = Label(self.background_frame,
                      text='Key Directory: ')
        label.place(x=0, y=0, width=100, height=30)
        
        key_path_var = StringVar()
        path_pane = Entry(self.background_frame, textvariable=key_path_var)
        key_path_var.set(self.key_dir)
        path_pane.place(x=100, y=0, width=self.window_width-250, height=30)
        
        button = Button(self.background_frame,
                        text='Browse Working Directory',
                        command=self.change_key_dir)
        button.place(x=self.window_width-150, y=0, width=150, height=30)
        
        self.left_pane = Listbox(self.background_frame)
        self.left_pane.bind('<<ListboxSelect>>', self.select_key)
        
        self.left_pane.place(x=0, y=31, 
                        width=self.window_width/2, 
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
        label.place(x=301, y=50, width=298, height=30)
        
        self.key_var = StringVar()
        key_entry = Entry(self.background_frame, textvariable=self.key_var)
        key_entry.place(x= 301, y=81, width=298, height=30)         
                    
        button = Button(self.background_frame, 
                        text='Generate Random Key',
                        command=self.generate_key)
        button.place(x=375, y=120, width=150, height=50)
        
        button = Button(self.background_frame, 
                        text='Save Key',
                        command=self.add_key)
        button.place(x=375, y=171, width=150, height=50)        

        button = Button(self.background_frame,
                             text='<<< Back to Main Menu',
                             command=self.draw_menu)
        button.place(x=375, y=222, width=150, height=50)


    def select_key(self, event):
        ii = self.left_pane.curselection()
        filename = self.left_pane.get(ii)
        
        with open(self.key_dir + '\\%s.key' % filename, 'rb') as f:
            key = f.read()
            
        self.key_var.set(base64.urlsafe_b64encode(key))


    def add_key(self):
        savepath = asksaveasfilename(filetypes=(("KEY File", ['.key']),),
                                             initialdir = '', 
                                             title = "Save key")
            
        if not savepath:
            return

        with open(savepath + '.key' , "wb") as f:
            f.write(self.new_key)
            
        self.key_manager_window()

    def generate_key(self):
        cipher = AESCipher()
        self.new_key = cipher.generate_key()
        self.key_var.set(base64.urlsafe_b64encode(self.new_key))

    def change_key_dir(self):
        new_key_dir = askdirectory(initialdir = self.key_dir, 
                                    title = "Change Key Directory")
        
        if new_key_dir:
            self.key_dir = new_key_dir
            self.key_manager_window()
       
        
        
    def quit_prompt(self):
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


    def find_file(self):
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

    def find_cmf_file(self):
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

    def find_key(self):
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


    def encrypt(self):
        if self.filepath and self.keypath:
            
            savepath = asksaveasfilename(filetypes=(("CMF File", 
                                                         ['.cmf']),),
                                             initialdir = '', 
                                             title = "Save encrypted file")
            
            if not savepath:
                return
            
            cipher = AESCipher()
            
            with open(self.keypath, "rb") as f:
                key = f.read()
            
            signing_key = cipher.generate_key()
            ciphertext = cipher.encrypt_file(self.filepath, 
                                             key, 
                                             signing_key)
            
            if savepath[-4:] != '.cmf':
                savepath = savepath + '.cmf'
            
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
                                   command=self.draw_menu)
            button.place(x=151, y=50, width=100, height=30)  

    def decrypt(self):
        if self.filepath and self.keypath:
            
            savepath = asksaveasfilename(initialdir = '', 
                                             title = "Save decrypted file")
            
            if not savepath:
                return
            
            cipher = AESCipher()
            
            with open(self.keypath, "rb") as f:
                key = f.read()
            
            with open(self.filepath , "rb") as f:
                msg = f.read()
                signing_key = msg[:cipher.block_size]
                ciphertext = msg[cipher.block_size:]
            
            deciphertext = cipher.decrypt(ciphertext, key, signing_key)
            
            with open(savepath, 'wb') as f:
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
                                   command=self.draw_menu)
            button.place(x=151, y=50, width=100, height=30)    
            


if __name__ == "__main__":
    app = Application()                

  