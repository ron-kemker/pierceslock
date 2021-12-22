# -*- coding: utf-8 -*-
"""
password_manager.py
By Ronald Kemker
21 Nov 2021

Description: This is a Password Manager for the Pierce's Lock Application

"""

import glob, os, binascii
import tkinter as tk
from tkinter import Frame, Button, Label, Menu, Entry, StringVar, Listbox, \
    Scrollbar, ttk
from tkinter.filedialog import askopenfilename,asksaveasfilename, askdirectory
from AESCipher import AESCipher, AuthenticationFailed,DecryptionFailed, \
    UnpaddingError, TTLError
    
class BaseApp(object):
    '''
    BaseApp Class is a helper class to test interoperability with the base
    pierce's lock application.'
    
    '''
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Password Manager")
        self.key_dir = os.path.abspath('keys')
        
    def quit_prompt(self):
        '''
        Helper function for draw_menu function.  Displays a prompt to quit the
        application.
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
        
class PasswordManager(object):
    def __init__(self, base_app=None):
        '''
        This is a Password Manager for the Pierce's Lock Application.  The 
        output password file (.PWF) is encrypted with AES-256.

        Parameters
        ----------
        base_app : Application object, optional
            This is a pointer to the main Pierce's lock application.
        
        Attributes
        ----------
        base_app : Application object, optional
            This is a pointer to the main Pierce's lock application.
        window_height : int 
           Pixel height of base application 
        window_width : int 
           Pixel width of base application 
        pwm_key : list of Strings
            This is the column headers for the Password Manager table
        test_mode : boolean
            True if running password_manager.py as a stand-alone application.
            False if running the Password Manager from the Pierce's Lock
            application.

        Returns
        -------
        None.
        
        TODO: Hide the Password by default
        TODO: Add sort capability
        TODO: Check if saved before quit        

        '''
               
        self.pwm_keys = ["Account Name", "Username", "Password", "URL", 
                         "Notes"]

        self.base_app = base_app
        self.window_height = 600
        self.window_width = 1000
        
        if base_app == None:
            self.test_mode = True
            self.base_app = BaseApp()
        else:
            self.test_mode = False
        
        
        if self.test_mode:
            self.password_manager_window()
            self.base_app.window.mainloop()

    def draw_menu(self, treev):
        '''
        This draws the menu bar

        Parameters
        ----------
        treev : tkinter Treeview object
            This contains the database for display purposes.
        
        Attributes
        ----------
        menu : tkinter Menu object
            This is the file menu bar.
        
        Returns
        -------
        None.        
        '''
        if hasattr(self, 'menu'):
            self.menu.destroy()
        
        # Build the menu
        self.menu = Menu(self.base_app.window)
        self.base_app.window.config(menu=self.menu)
        
        fileMenu = Menu(self.menu)
        self.menu.add_cascade(label='File', menu=fileMenu)
            
        fileMenu.add_command(label='New Password File', 
                                  command=self.password_manager_window)
        
        cmd = lambda:self.key_prompt_window(treev, 'load')
        fileMenu.add_command(label='Open Password File', 
                                  command=cmd)
        
        cmd = lambda:self.key_prompt_window(treev, 'save')
        fileMenu.add_command(label='Save Password File', 
                                  command=cmd)
        
        fileMenu.add_command(label='Close Password File', 
                                  command=self.password_manager_window)
            
        fileMenu.add_command(label='Quit', 
                                  command=self.base_app.quit_prompt)
        
        if not self.test_mode:
            toolMenu = Menu(self.menu)
            self.menu.add_cascade(label='Tools', menu=toolMenu)
            toolMenu.add_command(label='Main Menu', 
                             command=self.base_app.draw_main)    
            toolMenu.add_command(label='Encrypt File', 
                                 command=self.base_app.encryption_window)
            toolMenu.add_command(label='Decrypt File', 
                                 command=self.base_app.decryption_window)
            toolMenu.add_command(label='Key Manager', 
                                 command=self.base_app.key_manager_window)
            
            toolMenu.add_command(label='Password Manager', 
                                 command=self.password_manager_window)        
        
            helpMenu = Menu(self.menu)
            self.menu.add_cascade(label='Help', menu=helpMenu)
            helpMenu.add_command(label='About', 
                                 command=self.base_app.about_window)

    def password_manager_window(self):
        '''
        Opens the password manager window in the application
    
        Attributes
        ----------
        iid : int
            This is a row counter for the Treeviewer object

        Returns
        -------
        None.               
        '''        

        self.base_app.window.geometry("%dx%d" % (self.window_width, 
                                        self.window_height))
        
        self.iid = 0
        
        if hasattr(self, 'popup_window'):
            self.popup_window.destroy()
        if hasattr(self.base_app, 'background_frame'):
            self.base_app.background_frame.destroy()        
        
        
        self.base_app.background_frame = Frame(self.base_app.window, 
                                 width=self.window_width,
                                 height=self.window_height)
        self.base_app.background_frame.pack()
        

        treev = ttk.Treeview(self.base_app.background_frame, 
                             selectmode='browse')
        treev.place(x=10, y=65, width=self.window_width-20, 
                       height=self.window_height-95)

        verscrlbar = ttk.Scrollbar(self.base_app.background_frame,
                           orient ="vertical",
                           command = treev.yview) 
        verscrlbar.place(x=self.window_width-21, y=65, width=20, 
                         height=self.window_height-95)

        # Configuring treeview
        treev.configure(xscrollcommand = verscrlbar.set)

        # Defining number of columns
        treev["columns"] = tuple(self.pwm_keys)
         
        # Defining heading
        treev['show'] = 'headings'
         
        # Assigning the width and anchor to  the respective columns
        for i, key in enumerate(self.pwm_keys):
            treev.column(key, stretch=tk.YES, anchor='c')
            treev.heading(key, text=key, anchor ='c')
        
        # '''Buttons''' 
        button = Button(self.base_app.background_frame,
                        text='New Entry',
                        command=lambda:self.add_new_password_window(treev))
        button.place(x=10, y=10, width=150, height=50)
        
        button = Button(self.base_app.background_frame,
                              text='Edit Entry',
                              command=lambda:self.edit_password_window(treev))
        button.place(x=165, y=10, width=150, height=50)

        button = Button(self.base_app.background_frame,
                              text='Delete Entry',
                              command=lambda:self.delete_password_cmd(treev))
        button.place(x=320, y=10, width=150, height=50)    

        self.draw_menu(treev)        
        
    def key_prompt_window(self, treev, mode):
        '''
        Helper function for password_manager.  This function asks you to select
        an encryption key
        
        Parameters
        ----------
        treev : tkinter Treeview object
            This contains the database for display purposes.
        mode : string
            To save space, this conditional is to gate the save or load
            functions.
        
        Attributes
        ----------
        pane : tkinter Listbox object
            This has the list of keys to be selected
            
        Returns
        -------
        None.   
        '''
        
        window_height = 600
        window_width = 600
        popup_window = tk.Toplevel()
        popup_window.geometry("%dx%d" % (window_width, 
                                        window_height))
        # popup_window.wm_title('Save Password File')
        
        # Background of the popup window
        bkgd_frame = Frame(popup_window, width=window_width, 
                           height=window_height)
        bkgd_frame.pack()        
        
        label = Label(bkgd_frame, text='Select Encryption Key')
        label.place(x=10, y=0, width=window_width-20, height=30)

        label = Label(bkgd_frame,
                      text='Key Directory: ')
        label.place(x=10, y=31, width=100, height=30)
        
        self.key_path_var = StringVar()
        path_pane = Entry(bkgd_frame, 
                          textvariable=self.key_path_var)
        self.key_path_var.set(self.base_app.key_dir)
        path_pane.bind('<Return>', lambda:self.update_key_dir(treev, mode))
        path_pane.place(x=100, y=31, width=window_width-250, height=30)
        
        cmd = lambda:self.change_key_dir(popup_window, treev, mode)
        button = Button(bkgd_frame,
                        text='Browse Working Directory',
                        command=cmd)
        button.place(x=window_width-150, y=31, width=150, height=30)
        
        self.pane = Listbox(bkgd_frame)
        self.pane.bind('<<ListboxSelect>>', self.select_key)
        
        self.pane.place(x=10, y=62, 
                        width=window_width-20, 
                        height=window_height-130)
    
    
        for i, key_file in enumerate(glob.glob(self.base_app.key_dir + '/*.key')):
            self.pane.insert(i, key_file.split('\\')[-1][:-4])
        
        scrollbar = Scrollbar(self.pane)
        scrollbar.pack(side = tk.RIGHT, fill = tk.BOTH)
        self.pane.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command = self.pane.yview)


        if mode == 'save':    
            cmd = lambda:self.save_password_cmd(treev, popup_window)
        elif mode == 'load':
            cmd = lambda:self.load_password_cmd(treev, popup_window)
            
        button = Button(bkgd_frame,
                        text='Select',
                        command=cmd)
        button.place(x=199, y=window_height-60, width=100, height=50)
        
        button = Button(bkgd_frame,
                              text='Cancel',
                              command=popup_window.destroy)
        button.place(x=301, y=window_height-60, width=100, height=50)
        
    def update_key_dir(self, event, treev, mode):
        '''
        Helper function for key_manager_window.  This updates the directory
        path using the entry box.

        Parameters
        ----------
        event : tkinter event object
            This contains the listener obj for the key manager's key_path_var
        treev : tkinter Treeview object
            This contains the database for display purposes.
        mode : string
            To save space, this conditional is to gate the save or load
            functions.
            
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
            self.base_app.key_dir = new_key_dir
            self.key_prompt_window(treev, mode)  
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
            
            self.key_prompt_window(treev, mode)  

    def change_key_dir(self, popup_window, treev, mode):
        '''
        Helper function for key_manager_window.  This opens a browse window 
        to select a new key directory to display.
        
        Parameters
        ----------
        treev : tkinter Treeview object
            This contains the database for display purposes.
        mode : string
            To save space, this conditional is to gate the save or load
            functions.
                
        Attributes
        ----------
        key_dir : string 
           This is the path to the key directory.

        Returns
        -------
        None.
        '''
        
        popup_window.destroy()
        new_key_dir = askdirectory(initialdir = self.base_app.key_dir, 
                                    title = "Change Key Directory")
        
        if new_key_dir:
            self.base_app.key_dir = new_key_dir.replace('/', '\\')
            
            # with open('.profile', 'w') as f:
            #     f.write('key_dir '+self.base_app.key_dir)
                
            self.key_prompt_window(treev, mode)

    def select_key(self, event):
        '''
        Helper function for save_password_file_window.  This is the command
        used for key selection.

        Parameters
        ----------
        event : tkinter event object
            This contains the listener object for the key manager's left_pane
            
        Attributes
        ----------
        keypath : string
            The location of the .key file that will be used.

        Returns
        -------
        None.   
        '''
        ii = self.pane.curselection()
        filename = self.pane.get(ii)
        self.keypath = self.base_app.key_dir + '\\%s.key' % filename

    def save_password_cmd(self, treev, window):
        '''
        Helper function for password_manager.  This will encrypt and save the 
        password file.

        Parameters
        ----------
        treev : tkinter Treeview object
            This contains the database for display purposes.
        window : tkinter TopLevel object
            This is the popup window that contains the key selection
            
        Returns
        -------
        None.   
        '''
        window.destroy()
        
        if self.keypath:
            
            savepath = asksaveasfilename(filetypes=(("PWF File", 
                                                         ['.pwf']),),
                                             initialdir = '', 
                                             title = "Encrypt/Save?")
            
            if not savepath:
                return
            
            cipher = AESCipher()
            
            with open(self.keypath, "r") as f:
                key = f.read()
            
            key = binascii.unhexlify(key)
            
            csv_data = ''
            for row_id in treev.get_children():
                row = treev.item(row_id)['values']
                for val in row:
                    csv_data = csv_data + str(val) + ','
                csv_data = csv_data[:-1] + '\n'
            
            b = bytearray()
            b.extend(map(ord, csv_data))
            
            ciphertext, iv = cipher.encrypt(b, key)
            ciphertext, signing_key = cipher.encode_authentication(ciphertext, iv)
            
            if savepath[-4:] != '.pwf':
                savepath = savepath+'.pwf'
                
            # else:
            #     savepath = savepath[:-4] + '.pwf'
                
            with open(savepath , "wb") as f:
                f.write(signing_key + ciphertext)
       
            popup_window = tk.Toplevel()
            popup_window.geometry("300x100") 
            popup_window.wm_title("Save Successful")
            
            # Background of the popup window
            bkgd_frame = Frame(popup_window, width=300, height=100)
            bkgd_frame.pack()
            
            # Label that displays the prompt
            prompt_txt = "Save Successful"
            prompt = Label(bkgd_frame, text=prompt_txt)
            prompt.place(x=25, y=20, width=250)
            
            # Buttons to confirm save
            button = Button(bkgd_frame, text="Ok", 
                               command=popup_window.destroy)
            button.place(x=100, y=50, width=100, height=30 )        

    def load_password_cmd(self, treev, window):
        '''
        Helper function for password_manager.  This function finds the .pwf 
        file to be loaded.  
        
        Parameters
        ----------
        treev : tkinter Treeview object
            This contains the database for display purposes.
        window : tkinter TopLevel object
            This is the popup window that contains the key selection
        
        Attributes
        ----------
        iid : int
            This is a row counter for the Treeviewer object 
        
        Returns
        -------
        None.   
        '''
        
        window.destroy()
        pwf_file = askopenfilename(filetypes=(("PWF File", ['.pwf']),),
                                        initialdir = '', 
                                title = "Select file")
        
        if self.keypath:
            if not pwf_file:
                return
            
            cipher = AESCipher()
            
            with open(self.keypath, "r") as f:
                key = f.read()
            
            key = binascii.unhexlify(key)            
        
            with open(pwf_file, "rb") as f:
                msg = f.read()
                signing_key = msg[:16]
                ciphertext = msg[16:]
            
            try:
                ciphertext, iv = cipher.authenticate(ciphertext, signing_key)
            except TTLError:
                self.base_app.one_button_popup("TTL Failure",
                            "The message's time-to-live (TTL) has expired.")
                return
            except AuthenticationFailed:
                self.base_app.one_button_popup("Authentication Failed",
                                      "Message Authentication has Failed")                
                return
            
            try:
                deciphertext = cipher.decrypt(ciphertext, key, iv)
            except DecryptionFailed:
                self.base_app.one_button_popup("Decryption Failed",
                                      "Message Decryption has Failed")                
                return                
            except UnpaddingError:
                self.base_app.one_button_popup("Unpadding Failed",
                            "Message unpadding after decryption has failed.")                
                return                       
        
            csv_data = deciphertext.decode('utf-8').split('\n')
            self.iid = 0
            treev.delete(*treev.get_children())
            
            for row in csv_data:
                row = row.split(',')
                treev.insert("", 'end', iid=self.iid, text ="L1", 
                             values=tuple(row))
                self.iid = self.iid + 1
                
                                   
    def add_new_password_window(self, treev):
        '''
        This form is for the entry of a new password.
    
        Parameters
        ----------
        treev : tkinter Treeview object
            This contains the database for display purposes.
        
        Attributes
        ----------
        iid : int
            This is a row counter for the Treeviewer object
            
        Returns
        -------
        None.   
    
        '''
        
        popup_width = 400
        popup_height = len(self.pwm_keys) * 50 + 60
        
        popup_window = tk.Toplevel()
        popup_window.geometry("%sx%s" % (popup_width, popup_height)) 
        popup_window.wm_title("Add New Password")
        
        # Background of the popup window
        bkgd_frame = Frame(popup_window, width=400, height=popup_height)
        bkgd_frame.pack()
        
        string_var = []
        
        for i, key in enumerate(self.pwm_keys):
            # Label that displays the prompt            
            prompt = Label(bkgd_frame, text=key)
            prompt.place(x=25, y=20+i*50, width=popup_width-50)
    
            string_var.append(StringVar())
            entry_field = Entry(bkgd_frame, textvariable=string_var[-1])        
            entry_field.place(x=25, y=40+i*50, width=popup_width-50)
        
        # Buttons to save and quit, just quit, and cancel the "quit" 
        # command
        
        cmd = lambda:self.add_new_password_cmd(treev,string_var,popup_window)
        
        button = Button(bkgd_frame, text="Ok", command=cmd)
        button.place(x=99, y=popup_height-35, width=100, height=30 )  
        
        # Buttons to save and quit, just quit, and cancel the "quit" 
        # command
        button = Button(bkgd_frame, text="Cancel", 
                           command=popup_window.destroy)
        button.place(x=201, y=popup_height-35, width=100, height=30)          
    
    def add_new_password_cmd(self, treev, string_var, popup_window):
        '''
        The command that adds a new password to the TreeView object

        Parameters
        ----------
        treev : tkinter Treeview object
            This contains the database for display purposes.
        string_var : list of tkinter StringVar objects
            This is the listener for the form Entry objects
        popup_window : tkinter TopLevel object
            This window contains the add password form

        Attributes
        ----------
        iid : int
            This is a row counter for the Treeviewer object
            
        Returns
        -------
        None.  
        '''
        entry = []
        for i in range(len(string_var)):
            entry.append(string_var[i].get())
            
        treev.insert("", 'end', iid=self.iid, text ="L1", values=tuple(entry))
        self.iid = self.iid + 1
        popup_window.destroy()
        
        
    def delete_password_cmd(self, treev):
        '''
        The command that deletes a new password to the Treeview object

        Parameters
        ----------
        treev : tkinter Treeview object
            This contains the database for display purposes.
            
        Returns
        -------
        None.  
        '''
        try:
            treev.delete(int(treev.focus()))
        except ValueError:
            pass
    
    def edit_password_window(self, treev):
        
        '''
        Opens a form for the selected password entry.  You can edit this form.
    
        Parameters
        ----------
        treev : tkinter Treeview object
            This contains the database for display purposes.
            
        Returns
        -------
        None.      
        '''
    
        string_var = []
        items = treev.item(treev.focus())['values']
        
        if items == '':
            return  
        
        popup_width = 400
        popup_height = len(self.pwm_keys) * 50 + 60
        
        popup_window = tk.Toplevel()
        popup_window.geometry("%sx%s" % (popup_width, popup_height)) 
        popup_window.wm_title("Edit Password")
        
        # Background of the popup window
        bkgd_frame = Frame(popup_window, width=400, height=popup_height)
        bkgd_frame.pack()
        
        for i, key in enumerate(self.pwm_keys):
            # Label that displays the prompt            
            prompt = Label(bkgd_frame, text=key)
            prompt.place(x=25, y=20+i*50, width=popup_width-50)
    
            string_var.append(StringVar())
            entry_field = Entry(bkgd_frame, textvariable=string_var[-1])
            string_var[-1].set(items[i])
            entry_field.place(x=25, y=40+i*50, width=popup_width-50)
        
        # Buttons to save and quit, just quit, and cancel the "quit" 
        # command
        
        cmd = lambda:self.edit_password_cmd(treev,string_var, popup_window)
        
        button = Button(bkgd_frame, text="Ok", command=cmd)
        button.place(x=99, y=popup_height-35, width=100, height=30 )  
        
        # Buttons to save and quit, just quit, and cancel the "quit" 
        # command
        button = Button(bkgd_frame, text="Cancel", 
                           command=popup_window.destroy)
        button.place(x=201, y=popup_height-35, width=100, height=30)  
     
    def edit_password_cmd(self, treev, string_var, popup_window):
        '''
        This command edits the password entry.

        Parameters
        ----------
        treev : tkinter Treeview object
            This contains the database for display purposes.
        string_var : list of tkinter StringVar objects
            This is the listener for the form Entry objects
        popup_window : tkinter TopLevel object
            This window contains the add password form
            
        Returns
        -------
        None.  
        '''
        entry = []
        
        for i in range(len(string_var)):
            entry.append(string_var[i].get())
        
        selected_item = treev.selection()[0]    
        treev.item(selected_item, text ="L1", values=tuple(entry))
        popup_window.destroy()
        
if __name__ == "__main__":
    PasswordManager()