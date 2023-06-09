import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from datetime import datetime
import random

import socket
import threading
import json
import ast


LARGE_FONT = ("Simplified Arabic Fixed", 17,"bold")

HOST = "127.0.0.1"
PORT = 65432
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"
PAYADD = "payadd"
#option
LOGIN = "login"
LOGOUT = "logout"
MENU = "menu"
ORDER = "order"
PAY="pay"
UPDATE="update"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

Live_Account=[]
ID=[]
Ad=[]
pay_add=0
def Check_LiveAccount(username):
    for row in Live_Account:
        parse= row.find("-")
        parse_check= row[(parse+1):]
        if parse_check== username:
            return False
    return True

def Remove_LiveAccount(conn,addr):
    for row in Live_Account:
        parse= row.find("-")
        parse_check=row[:parse]
        if parse_check== str(addr):
            parse= row.find("-")
            Ad.remove(parse_check)
            username= row[(parse+1):]
            ID.remove(username)
            Live_Account.remove(row)
            conn.sendall("True".encode(FORMAT))

def check_clientLogIn(username, password):
    if Check_LiveAccount(username)== False:
        return 0
    # check if admin logged in
    if username == "a" and password == "a":
        return 1

    with open('client_account.json', 'r') as openfile:
        data = json.load(openfile)
  
    usr=data.get(username,None)
    print(usr)
    if(usr == None):
        print("Invalid Username")
    elif(usr != None):
        if(data[username]== password):
            return 1
    
    return 2

def clientLogIn(sck):

    user = sck.recv(1024).decode(FORMAT)
    print("username:--" + user +"--")

    sck.sendall(user.encode(FORMAT))
    
    pswd = sck.recv(1024).decode(FORMAT)
    print("password:--" + pswd +"--")
    
    accepted = check_clientLogIn(user, pswd)
    if accepted == 1:
        ID.append(user)
        account=str(Ad[Ad.__len__()-1])+"-"+str(ID[ID.__len__()-1])
        Live_Account.append(account)
    
    #print("accept:", accepted)
    sck.sendall(str(accepted).encode(FORMAT))
    #print("end-logIn()")

# Lấy món ăn trong menu
def getMenu():
    res=[]
    data=''
    with open('menu.json', 'r') as openfile:
        data = json.load(openfile)

    for i in range(len(data)):
        pos="dish"+str(i+1)
        res.append(data[pos])
    return res
    
# gá»­i dá»¯ liá»‡u menu cho client
def SendMenu(sck):
    menu = getMenu()
    for dish in menu:
        msg = "next"
        sck.sendall(msg.encode(FORMAT))
        sck.recv(1024)

        for data in dish:
            data = str(data)
            #print(data, end=' ')
            sck.sendall(data.encode(FORMAT))
            sck.recv(1024)

    msg = "end"
    sck.sendall(msg.encode(FORMAT))
    sck.recv(1024)

# Ä‘áº·t mÃ³n
def Insert_Order(sck):
    data = ""
    order=[]
    for i in range(7):
        data=sck.recv(1024).decode(FORMAT)
        #print(data)
        sck.sendall(data.encode(FORMAT))
        order.append(data)
    try:
        with open('order.json', 'r') as openfile:
            dict = json.load(openfile)

        if(dict.get(order[0],None) == None and int(order[4]) != 0):
            dict[order[0]]=order
            json_object = json.dumps(dict, indent = len(dict))
        # Writing to sample.json
            with open("order.json", "w") as outfile:
                outfile.write(json_object)
    except:
        sck.sendall("failed".encode(FORMAT))
        return False

    sck.sendall("success".encode(FORMAT))
    return True

# thanh toÃ¡n
def Pay(sck):
    data = ""
    pay=[]
    for i in range(2):
        data=sck.recv(1024).decode(FORMAT)
        sck.sendall(data.encode(FORMAT))
        pay.append(data)
        #print(pay)
    try:
        if(pay[1]=="1"):
            with open('order.json', 'r') as openfile:
                dict = json.load(openfile)
            dict[pay[0]][6]="PAID"
            json_object = json.dumps(dict, indent = len(dict))
            with open("order.json", "w") as outfile:
                outfile.write(json_object)
        else:
            sck.sendall("failed".encode(FORMAT))
            return False
    except:
        sck.sendall("failed".encode(FORMAT))
        return False

    sck.sendall("success".encode(FORMAT))
    return True
    
# Ä‘áº·t thÃªm mÃ³n
def UpdateOrder(sck):
    data = ""
    new_order=[]
    #current_order=[]
    for i in range(5):
        data=sck.recv(1024).decode(FORMAT)
        sck.sendall(data.encode(FORMAT))
        new_order.append(data)
    try:
        with open('order.json', 'r') as openfile:
            order_list = json.load(openfile)
        current_order=order_list.get(str(new_order[0]),None)
        if(current_order != None):
            dish1=ast.literal_eval(current_order[1])
            dish2=ast.literal_eval(current_order[2])
            dish3=ast.literal_eval(current_order[3])
            current_order=order_list[new_order[0]]
            a=dish1[2]-int(new_order[1])
            b=dish2[2]-int(new_order[2])
            c=dish3[2]-int(new_order[3])
            # check time
            current_time=datetime.strptime(current_order[5],"%d/%m/%Y %H:%M:%S")
            new_time=datetime.strptime(new_order[4],"%d/%m/%Y %H:%M:%S")
            e=(current_time.year-new_time.year)+(current_time.month-new_time.month)+(current_time.day-new_time.day)
            f=(new_time.hour*60+new_time.minute)-(current_time.hour*60+current_time.minute)

            if(a<=0 and b<=0 and c<=0):
                if(e == 0 and f <= 120):
                    dish1[2]=int(new_order[1])
                    dish2[2]= int(new_order[2])
                    dish3[2]=int(new_order[3])
                    #current_order[5]= new_order[4]
                    new_total=int(new_order[1])*int(dish1[1])+int(new_order[2])*int(dish2[1])+int(new_order[3])*int(dish3[1])
                    #pay_add=new_total-int(current_order[4])
                    #print("pay add:"+str(pay_add))
                    current_order[4]=str(new_total)
                    current_order[1]=str(dish1)
                    current_order[2]=str(dish2)
                    current_order[3]=str(dish3)
                    current_order[6]="UNPAID"
                    order_list[new_order[0]]=current_order

                else:
                    sck.sendall("failed".encode(FORMAT))
                    return False
            else:
                sck.sendall("failed".encode(FORMAT))
                return False

            json_object = json.dumps(order_list, indent = len(order_list))
        
            with open("order.json", "w") as outfile:
                outfile.write(json_object)
        else:
            sck.sendall("failed".encode(FORMAT))
            return False
    except:
        sck.sendall("failed".encode(FORMAT))
        return False

    sck.sendall("success".encode(FORMAT))
    return True


def handle_client(conn, addr):
    while True:

        option = conn.recv(1024).decode(FORMAT)

        if option == LOGIN:
            Ad.append(str(addr))
            clientLogIn(conn)
        elif option == MENU:
            SendMenu(conn)
        elif option == LOGOUT:
            Remove_LiveAccount(conn,addr)
        elif option == ORDER:
            Insert_Order(conn)
        elif option == PAY:
            Pay(conn)
        elif option == UPDATE:
            UpdateOrder(conn)

    Remove_LiveAccount(conn,addr)
    conn.close()
    print("end-thread")


def runServer():
    try:
        print(HOST)
        print("Waiting for Client")

        while True:
            print("enter while loop")
            conn, addr = s.accept()

            clientThread = threading.Thread(target=handle_client, args=(conn,addr))
            clientThread.daemon = True 
            clientThread.start()
        
            #handle_client(conn, addr)
            print("end main-loop")

    
    except KeyboardInterrupt:
        print("error")
        s.close()
    finally:
        s.close()
        print("end")
 

# defind GUI-app class
class OrderFood_Admin(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #self.iconbitmap('soccer-ball.ico')
        self.title("Restaurant Server")
        self.geometry("400x200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width=False, height=False)

        container = tk.Frame(self)
        container.pack(side="top", fill = "both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage,HomePage):
            frame = F(container, self)

            self.frames[F] = frame 

            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartPage)


    def showFrame(self, container):
        
        frame = self.frames[container]
        if container==HomePage:
            self.geometry("500x350")
        else:
            self.geometry("500x200")
        frame.tkraise()

    # close-programe function
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def logIn(self,curFrame):

        user = curFrame.entry_user.get()
        pswd = curFrame.entry_pswd.get()

        if pswd == "":
            curFrame.label_notice["text"] = "password cannot be empty"
            return 

        if user == "admin" and pswd == "server":
            self.showFrame(HomePage)
            curFrame.label_notice["text"] = ""
        else:
            curFrame.label_notice["text"] = "invalid username or password"

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="#98FB98")
        
        
        label_title = tk.Label(self, text="\nLOG IN FOR SERVER\n", font=LARGE_FONT,fg='black',bg="#98FB98").grid(row=0,column=1)

        label_user = tk.Label(self, text="\tUSERNAME ",fg='red',bg="#98FB98",font='Century 10 bold').grid(row=1,column=0)
        label_pswd = tk.Label(self, text="\tPASSWORD ",fg='red',bg="#98FB98",font='Century 10 bold').grid(row=2,column=0)

        self.label_notice = tk.Label(self,text="",bg="#98FB98",fg='red')
        self.entry_user = tk.Entry(self,width=30,bg='light yellow')
        self.entry_pswd = tk.Entry(self,width=30,bg='light yellow')

        button_log = tk.Button(self,text="LOGIN",bg="dark green",fg='floral white',command=lambda: controller.logIn(self))

        button_log.grid(row=4,column=1)
        button_log.configure(width=10)
        self.label_notice.grid(row=3,column=1)
        self.entry_pswd.grid(row=2,column=1)
        self.entry_user.grid(row=1,column=1)

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) 
        self.configure(bg="#BDB76B")
        label_title = tk.Label(self, text="\n ACTIVE ACCOUNT ON SEVER\n", font=LARGE_FONT,fg='#20639b',bg="#BDB76B").pack()
        
        self.conent =tk.Frame(self)
        self.data = tk.Listbox(self.conent, height = 10, 
                  width = 40, 
                  bg='floral white',
                  activestyle = 'dotbox', 
                  font = "Helvetica",
                  fg='#20639b')
        
        button_log = tk.Button(self,text="REFRESH",bg="#00FF00",fg='black',command=self.Update_Client)
        button_back = tk.Button(self, text="LOG OUT",bg="#FF0000",fg='black' ,command=lambda: controller.showFrame(StartPage))
        button_back.pack(side=BOTTOM)
        button_back.configure(width=10)
        button_log.pack(side= BOTTOM)
        button_log.configure(width=10)

        
        self.conent.pack_configure()
        self.scroll= tk.Scrollbar(self.conent)
        self.scroll.pack(side = RIGHT, fill= BOTH)
        self.data.config(yscrollcommand = self.scroll.set)
        
        self.scroll.config(command = self.data.yview)
        self.data.pack()
        
    def Update_Client(self):
        self.data.delete(0,len(Live_Account))
        for i in range(len(Live_Account)):
            self.data.insert(i,Live_Account[i])
    


sThread = threading.Thread(target=runServer)
sThread.daemon = True 
sThread.start()

        
app = OrderFood_Admin()
app.mainloop()