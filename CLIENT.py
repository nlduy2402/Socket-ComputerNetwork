from random import randint
import socket
import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk 
from tkinter import*
import threading
from datetime import datetime
import json
from PIL import ImageTk as igtk
from PIL import Image as ig
HOST = "127.0.0.1"
PORT = 65432
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"

LARGE_FONT = ("verdana", 13,"bold")

#option
LOGIN = "login"
LOGOUT = "logout" 
MENU = "menu"
ORDER="order"
PAY="pay"
UPDATE="update"

#GUI intialize
class OrderFood_App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.geometry("500x200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width=False, height=False)

        container = tk.Frame(self)
        container.pack(side="top", fill = "both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, HomePage):
            frame = F(container, self)

            self.frames[F] = frame 

            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartPage)
    
    def showFrame(self, container):
        frame = self.frames[container]
        if container==HomePage:
            self.geometry("500x500")
        else:
            self.geometry("350x200")
        frame.tkraise()
    # close-programe function
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            try:
                option = LOGOUT
                client.sendall(option.encode(FORMAT))
            except:
                pass

    def logIn(self,curFrame,sck):
        try:
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()

            if user == "" or pswd == "":
                curFrame.label_notice = "Fields cannot be empty"
                return 
       
            #notice server for starting log in
            option = LOGIN
            sck.sendall(option.encode(FORMAT))

            #send username and password to server
            sck.sendall(user.encode(FORMAT))
            #print("input:", user)

            sck.recv(1024)
            #print("s responded")

            sck.sendall(pswd.encode(FORMAT))
            #print("input:", pswd)

            # see if login is accepted
            accepted = sck.recv(1024).decode(FORMAT)
            print("accepted: "+ accepted)

            if accepted == "1":
                self.showFrame(HomePage)
                
                curFrame.label_notice["text"] = ""
            elif accepted == "2":
                curFrame.label_notice["text"] = "invalid username or password"
            elif  accepted == "0":
                curFrame.label_notice["text"] = "user already logged in"

        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"
            print("Error: Server is not responding")

    def logout(self,curFrame, sck):
        try:
            option = LOGOUT
            sck.sendall(option.encode(FORMAT))
            accepted = sck.recv(1024).decode(FORMAT)
            if accepted == "True":
                self.showFrame(StartPage)
        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"



class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")

        label_title = tk.Label(self, text="LOG IN", font=LARGE_FONT,fg='#20639b',bg="bisque2")
        label_user = tk.Label(self, text="username ",fg='#20639b',bg="bisque2",font='verdana 10 ')
        label_pswd = tk.Label(self, text="password ",fg='#20639b',bg="bisque2",font='verdana 10 ')

        self.label_notice = tk.Label(self,text="",bg="bisque2")
        self.entry_user = tk.Entry(self,width=20,bg='light yellow')
        self.entry_pswd = tk.Entry(self,width=20,bg='light yellow')

        button_log = tk.Button(self,text="LOG IN", bg="#20639b",fg='floral white',command=lambda: controller.logIn(self, client)) 
        button_log.configure(width=10)
        
        label_title.pack()
        label_user.pack()
        self.entry_user.pack()
        label_pswd.pack()
        self.entry_pswd.pack()
        self.label_notice.pack()

        button_log.pack()
        

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
        
        # define home page
        label_title = tk.Label(self, text="HOME PAGE", font=LARGE_FONT,fg='#20639b',bg="bisque2")
        button_back = tk.Button(self, text="LOG OUT",bg="red",fg='black', command=lambda: controller.logout(self,client))
        button_menu = tk.Button(self, text="MENU", bg="#20639b",fg='black',command=self.listMenu)
        button_order = tk.Button(self,text="ORDER", bg="#40ff00",fg='black',command=lambda: self.OrderFood(self.order_frame))
        button_pay = tk.Button(self,text="PAY",bg="yellow",fg='black',command=lambda:self.Pay(self.pay_frame))
        button_update = tk.Button(self,text="UPDATE",bg="orange",fg='black',command=self.UpdateOrder)
        button_img = tk.Button(self,text="IMAGE",bg="brown",fg='black',command=lambda:self.ShowImage(self.img_frame))
        label_title.pack(pady=10)   

        button_menu.configure(width=10)
        button_order.configure(width=10)
        button_pay.configure(width=10)
        button_back.configure(width=10)
        button_update.configure(width=10)
        button_img.configure(width=10)
        self.label_notice = tk.Label(self, text="", bg="bisque2")
        self.label_notice.pack(pady=4)

        button_menu.pack(pady=2) 
        button_order.pack(pady=2)
        button_pay.pack(pady=2)
        button_update.pack(pady=2)
        button_img.pack(pady=2)
        button_back.pack(pady=2)
       
        # menu tree
        self.frame_list = tk.Frame(self, bg="tomato")
        self.tree = ttk.Treeview(self.frame_list)
        self.tree["column"] = ("Name", "Price", "Note")
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Name", anchor='c', width=120)
        self.tree.column("Price", anchor='e', width=40)
        self.tree.column("Note", anchor='c', width=100)
        self.tree.heading("0", text="", anchor='c')
        self.tree.heading("Name", text="TÃªn mÃ³n Äƒn", anchor='c')
        self.tree.heading("Price", text="GiÃ¡", anchor='e')
        self.tree.heading("Note", text="Ghi chÃº", anchor='c')
        self.tree.pack(pady=20)

        #ORDER FRAME
        self.order_win=tk.Toplevel(self)
        self.order_win.protocol("WM_DELETE_WINDOW", self.Destroy)
        self.order_win.resizable(width=False,height=False)
        self.order_win.geometry("350x120")
        self.order_win.configure(bg="#FF9966")
        self.order_win.protocol("WM_DELETE_WINDOW")
        self.order_win.withdraw()
        self.order_frame=tk.Frame(self.order_win,bg="#FF9966")

        self.lb1=tk.Label(self.order_frame,text="Spaghetti",font=LARGE_FONT,bg="#FF9966",fg="black")
        self.lb1.configure(width=10)
        self.sb1=tk.Spinbox(self.order_frame,from_=0,to=10,font=("Helvetica",13))

        self.lb2=tk.Label(self.order_frame,text="Hamburger",font=LARGE_FONT,bg="#FF9966",fg="black")
        self.lb2.configure(width=10)
        self.sb2=tk.Spinbox(self.order_frame,from_=0,to=10,font=("Helvetica",13))

        self.lb3=tk.Label(self.order_frame,text="Chicken",font=LARGE_FONT,bg="#FF9966",fg="black")
        self.lb3.configure(width=10)
        self.sb3=tk.Spinbox(self.order_frame,from_=0,to=10,font=("Helvetica",13))
        
        # PAY FRAME:
        self.pay_win=tk.Toplevel(self)
        self.pay_win.protocol("WM_DELETE_WINDOW", self.Destroy)
        self.pay_win.geometry("250x120")
        self.pay_win.resizable(width=False,height=False)
        self.pay_win.configure(bg="#FF9966")
        self.pay_win.withdraw()
        self.pay_frame=tk.Frame(self.pay_win,bg="#FF9966")
        self.pay_label=tk.Label(self.pay_frame,text="ID",font=LARGE_FONT,bg="#FF9966",fg="black",width=5)
        self.pay_id=tk.Entry(self.pay_frame,width=10)
        self.var=IntVar()
        self.cash_pay=tk.Radiobutton(self.pay_frame, text="CASH", variable=self.var, value=1,bg="#FF9966")
        self.card_pay = tk.Radiobutton(self.pay_frame, text="CARD", variable=self.var, value=2,bg="#FF9966")
        self.id_card_label = tk.Label(self.pay_frame,text="CARD ID:",font=LARGE_FONT,bg="#FF9966",fg="black")
        self.card_id=tk.Entry(self.pay_frame,width=20)

        # IMAGE FRAME
        self.img_win=tk.Toplevel(self)
        self.img_win.protocol("WM_DELETE_WINDOW", self.Destroy)
        self.img_win.geometry("400x330")
        self.img_win.resizable(width=False,height=False)
        self.img_win.configure(bg="#FF9966")
        self.img_win.withdraw()
        self.img_frame=tk.Frame(self.img_win,bg="#FF9966")
        self.img1 = igtk.PhotoImage(ig.open("image/chicken.jpg"))
        self.img2 = igtk.PhotoImage(ig.open("image/burger.jpg"))
        self.img3 = igtk.PhotoImage(ig.open("image/spaghetti.jpg"))
        self.img_num=0
        self.img_label=tk.Label(self.img_frame,text="ID",font=LARGE_FONT,bg="#FF9966",fg="black",image=self.img1)

        #Update Frame
        self.update_win=tk.Toplevel(self)
        self.update_win.protocol("WM_DELETE_WINDOW", self.Destroy)
        self.update_win.geometry("350x150")
        self.update_win.resizable(width=False,height=False)
        self.update_win.configure(bg="#FF9966")
        self.update_win.withdraw()
        self.update_frame=tk.Frame(self.update_win,bg="#FF9966")

        self.id_order=tk.Label(self.update_frame,text="ID",font=LARGE_FONT,bg="#FF9966",fg="black")
        self.id_order_edit=tk.Entry(self.update_frame,width=10)
        self.lb4=tk.Label(self.update_frame,text="Spaghetti",font=LARGE_FONT,bg="#FF9966",fg="black")
        self.lb4.configure(width=10)
        self.sb4=tk.Spinbox(self.update_frame,from_=0,to=10,font=("Helvetica",13))

        self.lb5=tk.Label(self.update_frame,text="Hamburger",font=LARGE_FONT,bg="#FF9966",fg="black")
        self.lb5.configure(width=10)
        self.sb5=tk.Spinbox(self.update_frame,from_=0,to=10,font=("Helvetica",13))

        self.lb6=tk.Label(self.update_frame,text="Chicken",font=LARGE_FONT,bg="#FF9966",fg="black")
        self.lb6.configure(width=10)
        self.sb6=tk.Spinbox(self.update_frame,from_=0,to=10,font=("Helvetica",13))
        self.edit_button=tk.Button(self.update_frame,text="CONFIRM",bg="light green",font=LARGE_FONT,command=self.Update)

        
    def Destroy(self):
        self.order_win.withdraw()
        self.order_frame.grid_forget()
        self.img_win.withdraw()
        self.img_frame.grid_forget()
        self.pay_win.withdraw()
        self.pay_frame.grid_forget() 
        self.update_frame.grid_forget()
        self.update_win.withdraw()   

    # EDIT ORDER
    def Update(self):
        self.update_win.withdraw()
        self.update_frame.grid_forget()
        
        id=self.id_order_edit.get()
        a=self.sb4.get()
        b=self.sb5.get()
        c=self.sb6.get()
        now = datetime.now()
            # dd/mm/YY H:M:S
        time = now.strftime("%d/%m/%Y %H:%M:%S")
        order=[]
        order.append(str(id))
        order.append(a)
        order.append(b)
        order.append(c)
        order.append(time)
        try:
            option=UPDATE
            client.sendall(option.encode(FORMAT))

            for data in order:
                data=str(data)
                #print(data,end=' ')
                client.sendall(data.encode(FORMAT))
                client.recv(1024)

            status = client.recv(1024).decode(FORMAT)
            if status == "success":
                self.label_notice["text"] = "UPDATE SUCCESS !"
                return True
            elif status =="failed":
                self.label_notice["text"] = "UPDATE FAILED !"
                return False
        except:
            self.label_notice["text"] = "Error"

    def UpdateOrder(self):
        self.id_order.grid(row=0,column=0)
        self.id_order_edit.grid(row=0,column=1)
        self.lb4.grid(row=1,column=0)
        self.sb4.grid(row=1,column=1)

        self.lb5.grid(row=2,column=0)
        self.sb5.grid(row=2,column=1)

        self.lb6.grid(row=3,column=0)
        self.sb6.grid(row=3,column=1)
        self.edit_button.grid(row=4,column=1)
        self.update_frame.grid()
        self.update_win.deiconify()

    # CONTROL IMAGE
    def ChangeImage(self):
        self.img_win.withdraw()
        self.img_frame.grid_forget()
        self.img_num+=1
        num=self.img_num
        if(num%3==0):
            self.img_label.configure(image=self.img1)
        if(num%3==1):
            self.img_label.configure(image=self.img2)
        if(num%3==2):
            self.img_label.configure(image=self.img3)
        self.img_win.deiconify()
        self.img_label.grid()
        self.img_frame.grid(row=0,column=0)

    def ShowImage(self,curFrame):
        self.img_win.deiconify()
        self.img_label.grid()
        self.img_frame.grid(row=0,column=0)
        next_button=tk.Button(curFrame,text=">>",command=self.ChangeImage)
        next_button.grid(row=1,column=0,pady=2)
        return

    # CONTROL PAYMENT
    def Pay(self,Frame):
        self.frame_list.pack_forget()
        self.pay_label.grid(row=0,column=0)
        self.pay_id.grid(row=0,column=1)
        self.cash_pay.grid(row=1,column=0)
        self.card_pay.grid(row=1,column=1)
        self.id_card_label.grid(row=2,column=0)
        self.card_id.grid(row=2,column=1)
        self.pay_win.deiconify()
        self.pay_frame.grid()
        pay_button=tk.Button(Frame,text="CONFIRM",font=LARGE_FONT,bg="light green",fg="black",command=self.PayOrder)
        pay_button.grid(row=3,column=0,columnspan=2)
        return

    def Check_CardID(self,id):
        n=len(id)
        if(n==10):
            for i in range(n):
                if(ord(id[i]) < 48 or ord(id[i]) > 57):
                    return False
        else:
            return False

        return True

    def PayOrder(self):
        self.pay_win.withdraw()
        self.pay_frame.grid_forget()
        id=self.pay_id.get()
        card_id=self.card_id.get()
        try:
            if(len(id) == 0):
                self.label_notice["text"] = "ID order cann't be empty. Try again !"
                return False
            if(self.var.get() == 2 and self.Check_CardID(card_id)== True and len(card_id)!= 0) or (self.var.get() == 1 and len(card_id)==0):
                data=[str(self.pay_id.get()),"1"]
            else:
                data=[str("unknow"),"0"]
            option=PAY
            client.sendall(option.encode(FORMAT))
            for i in data:
                i=str(i)
                client.sendall(i.encode(FORMAT))
                client.recv(1024)

            status = client.recv(1024).decode(FORMAT)
            if status == "success":
                self.label_notice["text"] = "PAYMENT SUCCESS !"
                return True
            elif status =="failed":
                self.label_notice["text"] = "PAYMENT FAILED !"
                return False
        except:
            self.label_notice["text"] = "Error"

    # ORDER FOOD
    def OrderFood(self,curFrame):
        self.lb1.grid(row=0,column=0)
        self.sb1.grid(row=0,column=1)

        self.lb2.grid(row=1,column=0)
        self.sb2.grid(row=1,column=1)

        self.lb3.grid(row=2,column=0)
        self.sb3.grid(row=2,column=1)

        self.order_win.deiconify()
        self.order_frame.grid()
        
        order_button=tk.Button(curFrame,text="CONFIRM",font=LARGE_FONT,bg="light green",fg="black",command=lambda:self.AddOrder(curFrame))
        order_button.grid(row=3,columnspan=2)

    def AddOrder(self,frame):
        self.order_win.withdraw()
        self.order_frame.pack_forget()
        
        try:
            option = MENU
            client.sendall(option.encode(FORMAT))
            menu = self.receiveMenu()
        except:
            self.label_notice["text"] = "Error"

        order=[]
        try:
            c1=[menu[0][0],menu[0][1],int(self.sb1.get())]
            c2=[menu[1][0],menu[1][1],int(self.sb2.get())]
            c3=[menu[2][0],menu[2][1],int(self.sb3.get())]
            total=c1[2]*int(menu[0][1])+c2[2]*int(menu[1][1])+c3[2]*int(menu[2][1])
            now = datetime.now()
            # dd/mm/YY H:M:S
            time = now.strftime("%d/%m/%Y %H:%M:%S")
            status="UNPAID"

            id=randint(100,999)
            print(id)
            order.append(id)
            order.append(c1)
            order.append(c2)
            order.append(c3)
            order.append(total)
            order.append(time)
            order.append(status)
            print(order)

            if(total==0):
                self.label_notice["text"] = "Invalid Number Of Dishs"
                return
        except:
            self.label_notice["text"] = "Error"

        try:
            option=ORDER
            client.sendall(option.encode(FORMAT))

            for data in order:
                data=str(data)
                #print(data,end=' ')
                client.sendall(data.encode(FORMAT))
                client.recv(1024)

            status = client.recv(1024).decode(FORMAT)
            if status == "success":
                notice="Total:"+str(order[4])+"$ and ID:"+str(order[0])
                #self.label_notice["text"] = "success"
                self.label_notice["text"] = notice
                return True
            elif status =="failed":
                self.label_notice["text"] = "ORDER FAILED !"
                return False
        except:
            self.label_notice["text"] = "Error"

    # GET MENU
    def receiveMenu(self):
        
        dish = []
        Menu = []
        data = ''
        while True:
            data = client.recv(1024).decode(FORMAT)
            client.sendall(data.encode(FORMAT))
            if data == "end":
                break

            for i in range(3):
                data = client.recv(1024).decode(FORMAT)
                client.sendall(data.encode(FORMAT))
                dish.append(data) 

            Menu.append(dish)
            dish = []
        return Menu

    def listMenu(self):
        try:
            #self.frame_detail.pack_forget()
            self.update_frame.pack_forget()
            option = MENU
            client.sendall(option.encode(FORMAT))
            
            menu = self.receiveMenu()
            
            x = self.tree.get_children()
            for item in x:
                self.tree.delete(item)

            i = 0
            for m in menu:
                self.tree.insert(parent="", index="end", iid=i, values=(m[0], m[1], m[2]))
                i += 1

            self.frame_list.pack(pady=10)
        except:
            self.label_notice["text"] = "Error"
            
    

#GLOBAL socket initialize
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)

client.connect(server_address)

app = OrderFood_App()

#main
try:
    app.mainloop()
except:
    print("Error: server is not responding")
    client.close()

finally:
    client.close()