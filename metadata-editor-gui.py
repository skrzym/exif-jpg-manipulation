import Tkinter as tk
import tkFileDialog
import rename_by_datetime as rbd
import all_media_by_datetime as ambd
import time
import os


class MetadataEditorGui:

    def __init__(self, master):
        self.master = master
        #self.master.geometry("400x500")
        self.master.title("Hello World")
        # self.master.resizable(False, False)
        # self.master.tk_setPalette(background='#e6e6e6')

        # Bind keys to major functions and redirect 'red x' to our exit function
        self.master.protocol("WM_DELETE_WINDOW", self.click_exit)
        self.master.bind('<Return>', self.click_ok)
        self.master.bind('<Escape>', self.click_exit)

        self.current_dir = None

        # ******************** TOP MENU ********************
        menu_bar = tk.Menu(master)

        # create a pull-down menu, and add it to the menu bar
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.click_ok)
        file_menu.add_command(label="Save", command=self.click_ok)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.click_exit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # create more pull-down menus
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Cut", command=self.click_ok)
        edit_menu.add_command(label="Copy", command=self.click_ok)
        edit_menu.add_command(label="Paste", command=self.click_ok)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.click_ok)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # display the menu
        self.master.config(menu=menu_bar)

        # ******************** MAIN LAYOUT ********************
        # Main App Frame
        self.frame = tk.Frame(self.master)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)
        # self.frame['background'] = '#FFFFFF'

        # Source Photos --------------------

        self.list_1_frame = tk.Frame(self.frame)
        self.label_1 = tk.Label(self.list_1_frame, text='No Folder Selected')
        self.label_1.pack(side=tk.TOP, fill=tk.X)
        self.scrollbar_1 = tk.Scrollbar(self.list_1_frame)
        self.scrollbar_1.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_1 = tk.Listbox(self.list_1_frame, width=40, height=25)
        self.listbox_1.pack()
        self.listbox_1.config(yscrollcommand=self.scrollbar_1.set)
        self.scrollbar_1.config(command=self.listbox_1.yview)
        self.list_1_frame.grid(row=1, column=0)

        self.list_2_frame = tk.Frame(self.frame)
        self.label_2 = tk.Label(self.list_2_frame, text='Progress Details')
        self.label_2.pack(side=tk.TOP, fill=tk.X)
        self.button_run = tk.Button(self.list_2_frame, text='Run', command=self.run, width=20)
        self.button_run.pack(side=tk.BOTTOM)
        self.button_run['state'] = tk.DISABLED
        self.button_choose_dir = tk.Button(self.list_2_frame, text='Select Folder', command=lambda: self.populate_listbox(listbox=self.listbox_1), width=20)
        self.button_choose_dir.pack(side=tk.BOTTOM)
        self.scrollbar_2 = tk.Scrollbar(self.list_2_frame)
        self.scrollbar_2.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
        self.listbox_2 = tk.Listbox(self.list_2_frame, width=50, height=15)
        self.listbox_2.pack(pady=(0, 10))
        self.listbox_2.config(yscrollcommand=self.scrollbar_2.set)
        self.scrollbar_2.config(command=self.listbox_2.yview)
        self.list_2_frame.grid(row=1, column=1, stick=tk.N)




        # ******************** STATUS BAR ********************
        self.status_bar = tk.Label(self.master, text='Idle', bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Center GUI on user's screen
        self.center(self.master)

    def add_log(self, msg):
        self.listbox_2.insert(tk.END, str(msg))
        self.master.update_idletasks()
        self.listbox_2.see(tk.END)

    def run(self, event=None):
        if self.current_dir:
            self.status_bar['text'] = 'RUNNING...'
            self.master.update_idletasks()
            #time.sleep(2)
            rbd.modify_jpeg_filename(self.current_dir, log=self.add_log, verbose=True)
            self.status_bar['text'] = 'Idle'
        else:
            self.listbox_2.insert(tk.END, 'You need to select a folder.')
            self.status_bar['text'] = 'YOU MUST SELECT A FOLDER FIRST!'
            self.master.update_idletasks()

    def populate_listbox(self, event=None, listbox=None):
        listbox.delete(0, tk.END)# clear the listbox
        self.current_dir = tkFileDialog.askdirectory()
        jpgs, other, subdirs = rbd.list_dir_jpeg(self.current_dir)
        self.label_1['text'] = str(os.path.basename(self.current_dir))
        for item in jpgs:
            listbox.insert(tk.END, os.path.basename(item))
        if len(jpgs) > 0:
            self.button_run['state'] = tk.NORMAL
        rbd.directory_status(self.current_dir, self.add_log)

    def select_dir(self, event=None):
        print tkFileDialog.askdirectory()

    def click_ok(self, event=None):
        print('PLACEHOLDER - The user clicked "OK"')

    def click_exit(self, event=None):
        print("Exiting the program")
        self.master.destroy()

    @staticmethod
    def center(win):
        """
        FROM: https://stackoverflow.com/a/10018670/1459035
        centers a tkinter window
        :param win: the root or Toplevel window to center
        """
        win.update_idletasks()
        width = win.winfo_width()
        frm_width = win.winfo_rootx() - win.winfo_x()
        win_width = width + 2 * frm_width
        height = win.winfo_height()
        titlebar_height = win.winfo_rooty() - win.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = win.winfo_screenwidth() // 2 - win_width // 2
        y = win.winfo_screenheight() // 2 - win_height // 2
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        win.deiconify()


if __name__ == '__main__':
    # info = AppKit.NSBundle.mainBundle().infoDictionary()
    # info['LSUIElement'] = True
    root = tk.Tk()
    app = MetadataEditorGui(root)
    root.mainloop()

'''
def center(win):
    """
    centers a tkinter window
    :param win: the root or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.attributes('-alpha', 0.0)
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Exit", command=root.destroy)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)
    frm = tk.Frame(root, bd=4, relief='raised')
    frm.grid(row=0,column=0)
    lab = tk.Label(frm, text='Hello World!', bd=4, relief='sunken')
    lab.grid(ipadx=4, padx=4, ipady=4, pady=4)
    root.geometry('500x500')
    center(root)
    root.attributes('-alpha', 1.0)
    root.mainloop()
'''
