import Tkinter as tk
import ttk
import tkFileDialog
import rename_by_datetime as rbd
import all_media_by_datetime as ambd
import time
import os


class MetadataEditorGui:

    def __init__(self, master):
        self.master = master
        self.IDLE = 'Waiting for user input...'
        #self.master.geometry("400x500")
        self.master.title("Media Filename Modification Program")
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
        menu_file = tk.Menu(menu_bar, tearoff=0)
        menu_file.add_command(label="Open", command=self.click_ok)
        menu_file.add_command(label="Save", command=self.click_ok)
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self.click_exit)
        menu_bar.add_cascade(label="File", menu=menu_file)

        # create more pull-down menus
        menu_edit = tk.Menu(menu_bar, tearoff=0)
        menu_edit.add_command(label="Cut", command=self.click_ok)
        menu_edit.add_command(label="Copy", command=self.click_ok)
        menu_edit.add_command(label="Paste", command=self.click_ok)
        menu_bar.add_cascade(label="Edit", menu=menu_edit)

        menu_help = tk.Menu(menu_bar, tearoff=0)
        menu_help.add_command(label="About", command=self.click_ok)
        menu_bar.add_cascade(label="Help", menu=menu_help)

        # display the menu
        self.master.config(menu=menu_bar)

        # ******************** MAIN LAYOUT ********************
        # Main App Frame
        self.frame = tk.Frame(self.master)
        self.frame.pack(expand=True, side=tk.TOP, fill=tk.BOTH, padx=20, pady=20)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(1, weight=1)
        # self.frame['background'] = '#FFFFFF'

        # LEFT SIDE
        self.frame_list_1 = tk.Frame(self.frame)
        self.notebook_1 = ttk.Notebook(self.frame_list_1)

        # Notebook Tab 1 - Live Photos
        self.frame_tab_live = tk.Frame(self.notebook_1)
        self.scrollbar_live = tk.Scrollbar(self.frame_tab_live)
        self.scrollbar_live.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
        self.listbox_live = tk.Listbox(self.frame_tab_live, width=50, height=20)
        self.listbox_live.pack(expand=True, fill=tk.BOTH)
        self.listbox_live.config(yscrollcommand=self.scrollbar_live.set)
        self.scrollbar_live.config(command=self.listbox_live.yview)

        # Notebook Tab 2 - Regular JPEGS
        self.frame_tab_photos = tk.Frame(self.notebook_1)
        self.scrollbar_photos = tk.Scrollbar(self.frame_tab_photos)
        self.scrollbar_photos.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
        self.listbox_photos = tk.Listbox(self.frame_tab_photos, width=50, height=20)
        self.listbox_photos.pack(expand=True, fill=tk.BOTH)
        self.listbox_photos.config(yscrollcommand=self.scrollbar_photos.set)
        self.scrollbar_photos.config(command=self.listbox_photos.yview)

        # Notebook Tab 3 - Movies
        self.frame_tab_videos = tk.Frame(self.notebook_1)
        self.scrollbar_videos = tk.Scrollbar(self.frame_tab_videos)
        self.scrollbar_videos.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
        self.listbox_videos = tk.Listbox(self.frame_tab_videos, width=50, height=20)
        self.listbox_videos.pack(expand=True, fill=tk.BOTH)
        self.listbox_videos.config(yscrollcommand=self.scrollbar_videos.set)
        self.scrollbar_videos.config(command=self.listbox_videos.yview)

        # Notebook Tab 4 - Other Files
        self.frame_tab_other = tk.Frame(self.notebook_1)
        self.scrollbar_other = tk.Scrollbar(self.frame_tab_other)
        self.scrollbar_other.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
        self.listbox_other = tk.Listbox(self.frame_tab_other, width=50, height=20)
        self.listbox_other.pack(expand=True, fill=tk.BOTH)
        self.listbox_other.config(yscrollcommand=self.scrollbar_other.set)
        self.scrollbar_other.config(command=self.listbox_other.yview)

        # Notebook Tab 5 - Sub Folders
        self.frame_tab_folders = tk.Frame(self.notebook_1)
        self.scrollbar_folders = tk.Scrollbar(self.frame_tab_folders)
        self.scrollbar_folders.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
        self.listbox_folders = tk.Listbox(self.frame_tab_folders, width=50, height=20)
        self.listbox_folders.pack(expand=True, fill=tk.BOTH)
        self.listbox_folders.config(yscrollcommand=self.scrollbar_folders.set)
        self.scrollbar_folders.config(command=self.listbox_folders.yview)

        # Build Notebook
        self.notebook_1.add(self.frame_tab_live, text='Live')
        self.notebook_1.add(self.frame_tab_photos, text='Photos')
        self.notebook_1.add(self.frame_tab_videos, text='Videos')
        self.notebook_1.add(self.frame_tab_other, text='Other')
        self.notebook_1.add(self.frame_tab_folders, text='Folders')
        self.notebook_1.pack()

        self.frame_list_1.grid(row=1, column=0, stick=tk.N + tk.E)
        # END LEFT SIDE

        # RIGHT SIDE
        self.frame_list_2 = tk.Frame(self.frame)
        # Buttons SubFrame
        self.frame_buttons = tk.Frame(self.frame_list_2)
        self.label_choose_dir = tk.Label(self.frame_buttons, text='1)')
        self.button_choose_dir = tk.Button(self.frame_buttons, text='Select Folder',
                                           command=lambda: self.populate_notebook(), width=20)
        self.label_run = tk.Label(self.frame_buttons, text='2)')
        self.button_run = tk.Button(self.frame_buttons, text='Run', command=self.run, width=20)
        self.label_choose_dir.grid(row=0, column=0)
        self.button_choose_dir.grid(row=0, column=1)
        self.label_run.grid(row=1, column=0)
        self.button_run.grid(row=1, column=1)
        self.button_run['state'] = tk.DISABLED
        self.frame_buttons.pack(side=tk.BOTTOM, fill=tk.Y, expand=True)

        self.label_2 = tk.Label(self.frame_list_2, text='Progress Details')
        self.label_2.pack(side=tk.TOP, fill=tk.X)
        self.scrollbar_2 = tk.Scrollbar(self.frame_list_2)
        self.scrollbar_2.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
        self.listbox_2 = tk.Listbox(self.frame_list_2, width=53, height=15)
        self.listbox_2.pack(pady=(0, 10))
        self.listbox_2.config(yscrollcommand=self.scrollbar_2.set)
        self.scrollbar_2.config(command=self.listbox_2.yview)

        self.frame_list_2.grid(row=1, column=1, stick=tk.N + tk.W, padx=(20,0))
        # END RIGHT SIDE

        # ******************** STATUS BAR ********************
        self.frame_status = tk.Frame(self.master, bd=1, relief=tk.SUNKEN)
        self.frame_status.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar = tk.Label(self.frame_status, text=self.IDLE, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X)
        self.progress_bar = ttk.Progressbar(self.frame_status, orient='horizontal', mode='indeterminate')

        # Center GUI on user's screen
        self.center(self.master)

    def activate_progressbar(self, enable=True):
        # TODO - Needs more advanced implementation
        '''
        if enable:
            self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            self.progress_bar.start(50)
        else:
            self.progress_bar.pack_forget()
            self.progress_bar.stop()
        '''

    def add_log(self, msg):
        self.listbox_2.insert(tk.END, str(msg))
        self.master.update_idletasks()
        self.listbox_2.see(tk.END)

    def run(self, event=None):
        if self.current_dir:
            self.status_bar['text'] = 'RUNNING...'
            self.master.update_idletasks()
            self.activate_progressbar()
            ambd.modify_media_filenames(self.current_dir, log=self.add_log, verbose=True)
            self.activate_progressbar(False)
            self.status_bar['text'] = self.IDLE
            self.update_notebook()
            self.add_log('Check "' + self.current_dir + '" for the modified files.')
            self.status_bar['text'] = 'Check "' + self.current_dir + '" for the modified files.'
        else:
            self.listbox_2.insert(tk.END, 'You need to select a folder.')
            self.status_bar['text'] = 'YOU MUST SELECT A FOLDER FIRST!'
            self.master.update_idletasks()

    def update_notebook(self):
        if self.current_dir:
            self.status_bar['text'] = 'Analyzing files in selected folder...'
            self.activate_progressbar()
            self.master.update_idletasks()
            self.listbox_live.delete(0, tk.END)
            self.listbox_photos.delete(0, tk.END)
            self.listbox_videos.delete(0, tk.END)
            self.listbox_other.delete(0, tk.END)
            self.listbox_folders.delete(0, tk.END)

            # Determine if any files in folder are valid media files
            lives, jpegs, movs, others, subdirs = ambd.list_dir_files(self.current_dir)
            valid_count = len(lives) + len(jpegs) + len(movs)
            # Add valid files names to list of files to be edited
            for item in lives:
                self.listbox_live.insert(tk.END, os.path.basename(item))
            for item in jpegs:
                self.listbox_photos.insert(tk.END, os.path.basename(item))
            for item in movs:
                self.listbox_videos.insert(tk.END, os.path.basename(item))
            for item in others:
                self.listbox_other.insert(tk.END, os.path.basename(item))
            for item in subdirs:
                self.listbox_folders.insert(tk.END, os.path.basename(item))

            self.status_bar['text'] = self.IDLE

            return valid_count

    def populate_notebook(self, event=None, directory=None):
        # Select a folder with media files to rename
        self.status_bar['text'] = 'Selecting folder...'
        self.master.update_idletasks()
        if directory:
            self.current_dir = directory
        else:
            self.current_dir = tkFileDialog.askdirectory()

        if self.current_dir:
            valid_count = self.update_notebook()

            self.status_bar['text'] = 'Checking if "Run" can be enabled...'

            if valid_count > 0:
                self.button_run['state'] = tk.NORMAL

            # Add details to logger on valid media status and change Status Bar
            ambd.directory_status(self.current_dir, self.add_log)
            self.status_bar['text'] = self.IDLE
            self.activate_progressbar(False)
            self.master.update_idletasks()


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

