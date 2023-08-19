#Final Project GUI
import tkinter as tk
from tkinter import ttk, filedialog
import ds_messenger as ds
from tkinter.simpledialog import askstring # https://docs.python.org/3/library/dialog.html
import time


class Body(tk.Frame):
    """
    The body part of the GUI. Includes a treeview widget displaying the usernames of the user's friends, a history message widget displaying the messages the user's friends
    have sent to the user, and a entry widget allowing the user to enter message he/she want to send to his/her friends.
    """
    def __init__(self, root, current_user=None):
        """
        initializer for Body of the GUI.

        :param current_user: the user who are using the GUI to send and receive messages.
        """
        tk.Frame.__init__(self,root)
        self.root = root
        self.current_user = current_user
        self._messages = []
        self._users = []
        self.index = None
        try:
            self.entry = self.current_user.retrieve_all()
        except ds.FailToJoin:
            # Toplevel object which will be treated as a new window 
            closeWindow = tk.Toplevel(self.root)
            closeWindow.title("Wrong Log In!!")
            closeWindow.geometry("300x200")

            login_frame = tk.Frame(master=closeWindow, bg="")
            login_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        
            editor_frame = tk.Frame(master=login_frame, bg="red")
            editor_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        
        
            login_editor = tk.Text(editor_frame, width=0)
            login_editor.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=0, pady=0)

            login_editor.insert(0.0, "Failed to Log in. The password is incorrect. Please close all the windows and start over.\n")
        else:
            self._draw()
        

    def node_select(self, event):
        """
        Detects which friend has been chosen by the user and will display the message this friend has sent to the user.
        """
        self.index = int(self.user_tree.selection()[0])-1
        from_user = self._users[self.index]
        self.set_history_message(self.entry, from_user)


    def set_users(self):
        """
        insert the username of the current user's friend list into the treeview widget in order.
        """
        id = 1
        # update the add_user widget.
        for DirectMessage in self.entry:
            # add all senders in to a list
            if DirectMessage['recipient'] not in self._users:
                self._users.append(DirectMessage['recipient'])
        # displays all of the DS users that have sent you messages
        for sender in self._users:
            self._insert_user_tree(id, sender)
            id += 1
            

    def insert_user(self, user: str):
        """
        Allows the user to add the username of his/her new friend.

        :param user: the username of the friend wanted to be added into the tree widget.
        """
        self._users.append(user)
        self._insert_user_tree(len(self._users), user)

    def _insert_user_tree(self, id, username):
        '''
        insert the username to the user_tree
        '''
        name = username
        if len(name) > 25:
            name = name[:24] + "..."

        self.user_tree.insert('', id, id, text=name)

    def get_text_entry(self):
        """
        Returns the text that the user have entered in the bottom of the body frame, which is the message he/she want to send.

        :return str
        """
        return self.message_editor.get('1.0', 'end').rstrip()

    def set_history_message(self, text:list, from_user:str):
        """
        Clears the texts currently displaying on the upper widget of the body frame, and then displays the time and content of the messages of the user selected in the
        treeview on the upper right widget.

        :param text: A nested list including the lists of the time, username, and message that the user have sent.  
        :param from_user: The username that the user choose to check for history messages.
        """
        self.message_reader.delete(0.0, 'end')
        message_menu = ""
        if text == []:
            self.message_reader.insert(0.0, "No old messages. Start communicating.\n")
        else:
            for i in text:
                if i['recipient'] == from_user:
                    # localtime() from https://docs.python.org/3/library/time.html#time.localtime
                    # and https://overiq.com/python-3-time-module/
                    ltime = time.localtime(float(i['timestamp']))
                    local_time = str(ltime.tm_mon) + '/' + str(ltime.tm_mday) + '/' + str(ltime.tm_year) + ' at '\
                                 + str(ltime.tm_hour) + ':' + str(ltime.tm_min) + ':' + str(ltime.tm_sec)
                    message_menu = message_menu + local_time + ": " + i['recipient'] + ": " + i['message'] +"\n"
            if message_menu == "":
                self.message_reader.insert(0.0, "No old messages. Start communicating.\n")
            else:
                self.message_reader.insert(0.0, message_menu)
        
        
    def _draw(self):
        """
        Draws the userframe, the treeview widget, the message_history widget, and the message_editor widget.
        """
        user_frame = tk.Frame(master=self, width=250)
        user_frame.pack(fill=tk.BOTH, side=tk.LEFT)
        
        self.user_tree = ttk.Treeview(user_frame)
        self.user_tree.bind("<<TreeviewSelect>>", self.node_select)
        self.user_tree.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=5, pady=5)

        # set the add user widget
        self.set_users()
        
        # reading history frame
        history_frame = tk.Frame(master=self, bg="blue")
        history_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

        reader_frame = tk.Frame(master=history_frame, bg="red")
        reader_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        
        rscroll_frame = tk.Frame(master=history_frame, bg='blue', width=10)
        rscroll_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)
        
        self.message_reader = tk.Text(reader_frame, width=0)
        self.message_reader.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=0, pady=0)

        message_reader_scrollbar = tk.Scrollbar(master=rscroll_frame, command=self.message_reader.yview)
        self.message_reader['yscrollcommand'] = message_reader_scrollbar.set
        message_reader_scrollbar.pack(fill=tk.Y, side=tk.LEFT, expand=False, padx=0, pady=0)

        # writing message frame
        message_frame = tk.Frame(master=self, bg="")
        message_frame.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True)

        editor_frame = tk.Frame(master=message_frame, bg="red")
        editor_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        
        scroll_frame = tk.Frame(master=message_frame, bg='blue', width=10)
        scroll_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)
        
        self.message_editor = tk.Text(editor_frame, width=0)
        self.message_editor.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=0, pady=0)

        message_editor_scrollbar = tk.Scrollbar(master=scroll_frame, command=self.message_editor.yview)
        self.message_editor['yscrollcommand'] = message_editor_scrollbar.set
        message_editor_scrollbar.pack(fill=tk.Y, side=tk.LEFT, expand=False, padx=0, pady=0)

        self.root.update()


# Footer
class Footer(tk.Frame):
    """
    This creates 2 buttons which allows the user to add his/her friend to the treeview widget and makes him enable to send messages to his friends.
    """
    def __init__(self, root, send_callback=None, add_user_callback=None):
        """
        Initializes the Footer of the GUI.

        :param send_callback: the callback relates to the send button.  
        :param add_user_callback: the callback relates to the add user button.
        """
        tk.Frame.__init__(self, root)
        self.root = root
        self._send_callback = send_callback
        self._add_user_callback = add_user_callback

        self._draw()

    def user_click(self):
        """
        Reacts when the user clicks on 'Add User' button.
        """
        if self._add_user_callback is not None:
            self._add_user_callback()

    def send_click(self):
        """
        Reacts when the user clicks on 'Send' button.
        """
        if self._send_callback is not None:
            self._send_callback()


    def _draw(self):
        """
        Draws the two button created in the Footer of the GUI.
        """
        send_button = tk.Button(master=self, text='Send', width=20)
        send_button.configure(command=self.send_click)
        send_button.pack(fill=tk.BOTH, side=tk.RIGHT, padx=5, pady=5)

        user_button = tk.Button(master=self, text='Add User', width = 20)
        user_button.configure(command=self.user_click)
        user_button.pack(fill=tk.BOTH, side=tk.LEFT, padx=5, pady=5)

    


class MainApp(tk.Frame):
    """
    Calls the body and footer to form a complete GUI.
    """
    def __init__(self, root):
        """
        Initializes the GUI with asking the username and password of the user.
        """
        tk.Frame.__init__(self, root)
        self.root = root
        self.user_lst = []
        # ask username and password
        self.sender()

        # After initialization of the current user is complete, call the _draw method to pack the widgets
        # into the root frame
        self._draw()

    def sender(self):
        """
        Asks the username and password of the user and creates a DirectMessenger object.
        """
        # askstring() from https://docs.python.org/3/library/dialog.html
        self.username = askstring("Username", "Please Enter your username")
        self.password = askstring("Password", "Please Enter your password")
        # self.messenger is an instance of class DirectMessenger
        self.messenger = ds.DirectMessenger("168.235.86.101", self.username, self.password)
            
        
    def send(self):
        """
        Connects to the send_callback in Footer and sends messages to selected user in the treeview.
        """
        if self.body.index == None:
            self.body.message_reader.delete(0.0, 'end')
            self.body.message_reader.insert(0.0, "No user selected.\n")
            pass
        else:
            recipient_name = self.body._users[self.body.index]
            message = self.body.get_text_entry()
            result = self.messenger.send(message, recipient_name)
            if result:
                print("Post sent.")
                sent_msg = self.username + ' sent: ' + message +'\n'
                self.body.message_reader.insert('end', sent_msg)
            else:
                print("Post fail to send.")
                self.body.message_reader.delete(0.0, 'end')
                self.body.message_reader.insert(0.0, "Messages failed to send. You cannot wrap a line.")
        
    def add_user(self):
        """
        Connects to the add_user_callback in Footer and adds the username of the friend the user want to add to the treeview.
        """
        new_username = askstring("Username", "Please Enter the username")
        self.body.insert_user(new_username)

        
    def _draw(self):
        """
        Draws the body and footer of the GUI.
        """
        # The Body and Footer classes must be initialized and packed into the root window.
        self.body = Body(self.root, current_user=self.messenger)
        self.body.pack(fill=tk.BOTH, side = tk.TOP)
        
        self.footer = Footer(self.root, send_callback=self.send, add_user_callback=self.add_user)
        self.footer.pack(fill=tk.BOTH, side=tk.BOTTOM)

if __name__=="__main__":
    main = tk.Tk()
    
    main.title("ICS 32 Distributed Social Platform")
    
    main.option_add('*tearOff', False)
    MainApp(main)

    main.update()
    main.minsize(720, main.winfo_height())
    main.mainloop()
