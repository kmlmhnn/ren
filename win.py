from tkinter import Tk, StringVar, N, W, E, S, ttk, filedialog, Listbox, Scrollbar, VERTICAL, messagebox
from core import Selection, listdir, rename, insertfn, changefn, appendfn, prefixfn, suffixfn


COMMAND_MODE, SEARCH_MODE, ARG_MODE = 0, 1, 2


class Window:
    def __init__(self):
        self.selection = Selection([])
        self.mode = None
        self.root = Tk()
        self.key = StringVar()
        self.arg = StringVar()
        self.old = StringVar()
        self.new = StringVar()
        self.xform = None
        self.path = None

        self.mainframe = ttk.Frame(self.root)
        self.oldlist = Listbox(self.mainframe, listvar=self.old, height=10)
        self.newlist = Listbox(self.mainframe, listvar=self.new, height=10)
        self.scrollbar = Scrollbar(self.mainframe, orient=VERTICAL, command=self.scroll)
        self.oldlist.configure(yscrollcommand=self.scrollbar.set)
        self.search = ttk.Entry(self.mainframe, textvariable=self.key)
        self.argument = ttk.Entry(self.mainframe, textvariable=self.arg)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=0)
        self.mainframe.columnconfigure(2, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.rowconfigure(1, weight=0)
        self.mainframe.grid(column=0, row=0, sticky=(N, E, W, S))
        self.oldlist.grid(column=0, row=0, sticky=(N, E, W, S))
        self.newlist.grid(column=2, row=0, sticky=(N, E, W, S))
        self.scrollbar.grid(column=1, row=0, sticky=(N, S))
        self.search.grid(column=0, row=1, sticky=(N, E, W, S))
        self.argument.grid(column=2, row=1, sticky=(N, E, W, S))

        self.root.bind('<Escape>', lambda e: self.mode != COMMAND_MODE and self.set_command_mode())
        self.root.bind('/', lambda e: self.mode == COMMAND_MODE and self.set_search_mode())
        self.root.bind('i', lambda e: self.mode == COMMAND_MODE and self.select_transform(insertfn))
        self.root.bind('I', lambda e: self.mode == COMMAND_MODE and self.select_transform(prefixfn))
        self.root.bind('a', lambda e: self.mode == COMMAND_MODE and self.select_transform(appendfn))
        self.root.bind('A', lambda e: self.mode == COMMAND_MODE and self.select_transform(suffixfn))
        self.root.bind('c', lambda e: self.mode == COMMAND_MODE and self.select_transform(changefn))
        self.root.bind('u', lambda e: self.mode == COMMAND_MODE and self.undo_transform())
        self.root.bind('O', lambda e: self.mode == COMMAND_MODE and self.opendir())
        self.root.bind('M', lambda e: self.mode == COMMAND_MODE and self.commit())
        self.root.bind('\\', lambda e: self.mode == COMMAND_MODE and self.undo_filter())
        self.root.bind('<Return>', self.handle_return_key)

        self.set_command_mode()

    def set_command_mode(self):
        self.mode = COMMAND_MODE
        self.search.state(['readonly'])
        self.argument.state(['readonly'])

    def set_search_mode(self):
        self.mode = SEARCH_MODE
        self.search.state(['!readonly'])
        self.search.focus_set()

    def set_arg_mode(self):
        self.mode = ARG_MODE
        self.argument.state(['!readonly'])
        self.argument.focus_set()

    def scroll(self, *args, **kwargs):
        self.oldlist.yview(*args, **kwargs)
        self.newlist.yview(*args, **kwargs)

    def handle_return_key(self, e):
        if self.mode == SEARCH_MODE:
            self.filter()
        elif self.mode == ARG_MODE:
            self.transform()

    def select_transform(self, f):
        self.xform = f
        self.set_arg_mode()

    def opendir(self):
        path = filedialog.askdirectory()
        if path:
            self.selection = Selection(listdir(path))
            self.path = path
            self.show_selected()

    def show_selected(self):
        selected = self.selection.peek()
        self.old.set([o for (o, n) in selected])
        self.new.set([n if o != n else '' for (o, n) in selected])
        self.root.title('%d selections' % len(selected))

    def filter(self):
        self.set_command_mode()
        self.selection.tighten(self.key.get())
        self.show_selected()

    def undo_filter(self):
        self.selection.loosen()
        self.show_selected()

    def transform(self):
        self.set_command_mode()
        fn, substring, payload = self.xform, self.key.get(), self.arg.get()
        try:
            self.selection.transform(lambda string: fn(string, substring, payload))
        except Exception as e:
            messagebox.showinfo(message=str(e))
        self.show_selected()

    def undo_transform(self):
        self.selection.rollback()
        self.show_selected()

    def commit(self):
        count = rename(self.path, self.selection.peek())
        message = '%d files renamed.' % count
        messagebox.showinfo(message=message)
        self.selection = Selection(listdir(self.path))
        self.show_selected()
