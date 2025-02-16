import tkinter as tk
from tkinter import ttk
import socket
import json
import threading
import time
import matplotlib.pyplot as plt
import queue 
from tkinter import filedialog
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tools import get_demo_firefighter_data
demo_firefighter_data = [
    {
        "name": "John",
        "location": "Building A, Floor 2",
        "gesture": "None",
        "id": 0,
        "wifi_strength": "Excellent",
        "last_updated": "10 Seconds Ago",

    },
    {
        "name": "Sarah",
        "location": "Building A, Floor 2",
        "gesture": "None",
        "id": 1,
        "wifi_strength": "Good",
        "last_updated": "100 seconds ago",

        

    },
    {
        "name": "Michael",
        "location": "Building A, Floor 2",
        "gesture": "None",
        "id": 2,
        "wifi_strength": "Bad",
        "last_updated": "300 Seconds Ago",

    }

]

def update_treeview(treeview, text, var):
        new_value = var.get()
        # Find the item in the Treeview that corresponds to the label_text
        for item in treeview.get_children():
            if treeview.item(item, "values")[0] == text:
                # Update the value in the Treeview
                treeview.item(item, values=(text, new_value))
class DashboardApp:
    def __init__(self, root):
        self.data_queue = queue.Queue()

        ## SERVER ## 
        # self.host = "127.0.0.1"
        self.host = "192.168.0.30"

        self.port = 5555
        self.server= None
        # self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.client_socket.connect((self.server_host, self.server_port))
        # self.refresh_data()

        ## DATA QUEUES ## 
        self.root = root
        self.label = ttk.Label(root, text="Hello, Tkinter!")
        self.root.title("Firefighter Dashboard")
        self.root.geometry("1600x1400")
        self.firefighter_data = {}  # Dictionary to store actual firefighter data
        self.view_data = {}         # Dictionary to store view representation data
        self.folder_path = ""
        # Make the root window resizable
        # self.root.columnconfigure(0, weight=1)  # Make the column expandable
        # self.root.rowconfigure(0, weight=1)     # Make the row expandable

        # Create the left and right frames
        self.root.resizable(height = None, width = None)
        self.left_frame = tk.PanedWindow(self.root, orient="vertical")
        self.left_frame.pack(side="left", padx=10, pady=10, expand=True)
        # self.left_frame.resizable(height = 100, width = 100)

        self.right_frame = tk.PanedWindow(self.root, orient="horizontal")
        
        # self.right_frame.pack(side="right", padx=10, pady=10, fill="both", expand=False)
        self.right_frame.pack(fill="both", expand=True)
        # create bottom frame
        self.bottom_frame = tk.PanedWindow(self.root, orient="horizontal")
        # make the 
        self.bottom_frame.pack()
        # self.bottom_frame.pack(side="bottom", padx=10, pady=10, fill="both", expand=True)
        
        # Make the right frame resizable
        # self.right_frame.columnconfigure(0, weight=1)  # Make the column expandable
        # self.right_frame.rowconfigure(0, weight=1)     # Make the row expandable
        
        # make the left frame resizeable
        # self.left_frame.columnconfigure(0, weight=1)  # Make the column expandable
        # self.left_frame.rowconfigure(0, weight=1)     # Make the row expandable

        # make the bottom frame resizeable
        # self.bottom_frame.columnconfigure(0, weight=1)  # Make the column expandable
        # self.bottom_frame.rowconfigure(0, weight=1)     # Make the row expandable
        
        # put a divider between the firefighter data and the gesture data
        divider = ttk.Separator(self.bottom_frame, orient="horizontal", style="TSeparator")
        divider.pack(fill="x")
        # 
        # Create tabs in the left frame
        self.left_notebook = ttk.Notebook(self.left_frame)
        self.left_notebook.pack(fill="both", expand=True)

        self.tab_record_gestures_left = ttk.Frame(self.left_notebook)
        self.left_notebook.add(self.tab_record_gestures_left, text="Record Gestures (Left)")

        # Create widgets for Record Gestures tab in the left frame
        self.create_record_gestures_widgets(self.tab_record_gestures_left)

        # Create tabs in the right frame
        self.right_notebook = ttk.Notebook(self.right_frame)
        self.right_notebook.pack(fill="both", expand=True)

        self.tab_record_gestures_right = ttk.Frame(self.right_notebook)
        self.right_notebook.add(self.tab_record_gestures_right, text="Record Gestures (Right)")
        
        # Create widget for realtime firefighter data on the right
        self.tab_create_firefighter_data = ttk.Frame(self.right_notebook)
        self.right_notebook.add(self.tab_create_firefighter_data, text="Realtime Firefighter Data")
        self.create_firefighter_data_widgets(self.tab_create_firefighter_data)

        # Create widgets for Record Gestures tab in the right frame
        self.create_record_gestures_widgets(self.tab_record_gestures_right)

        # Labels to display data
        self.strength_label = ttk.Label(root, text="Bluetooth/Wi-Fi Strength:")
        self.strength_label.pack()

        self.names_label = ttk.Label(root, text="Firefighter Names:")
        self.names_label.pack()

        self.locations_label = ttk.Label(root, text="Firefighter Locations:")
        self.locations_label.pack()

        self.time_label = ttk.Label(root, text="Time:")
        self.time_label.pack()

        # Button to refresh data
        self.refresh_button = ttk.Button(root, text="Refresh Data", command=self.refresh_data)
        self.refresh_button.pack()

        # Create the main notebook with tabs
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # Create tabs
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab_record_gestures = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text="Realtime Inference")
        self.notebook.add(self.tab2, text="bash terminal")

        # put a bash terminal in the second tab
        self.bash_terminal = tk.Text(self.tab2)
        self.bash_terminal.pack()
        self.bash_terminal.insert(tk.END, "Welcome to the bash terminal\n")


       

        



        # self.notebook.add(self.tab2, text="Realtime Firefighter Data")
        # self.notebook.add(self.tab_record_gestures, text="Record Gestures")

        # Make the main notebook resizable
        self.tab1.columnconfigure(0, weight=1)
        self.tab1.columnconfigure(1, weight=1)
        self.tab1.rowconfigure(0, weight=1)

        self.create_record_gestures_widgets(self.tab_record_gestures)

        self.create_matplotlib_plot(self.tab1)

        # self.create_firefighter_data_widgets(self.tab2)

        def correctly_resize(event):
            self.canvas_widget.config(width=event.width, height=event.height)
            self.canvas.draw()

            self.tab1.bind("<Configure>", correctly_resize)
            self.canvas_widget.pack(expand=True, fill=tk.BOTH)
        

    
        
    # def handle_client(self, client, addr):
    #     try:
    #         while True:
    #             data = self.get_data_with_timestamp(addr)  # Include client address in the data
    #             client.sendall(data.encode())
    #             time.sleep(1)  # Simulate data update every 1 second
    #     except ConnectionResetError:
    #         print(f"Client {addr} disconnected")
    #         client.close()
    
    def get_data_with_timestamp(self):
        timestamp = time.time()
        data_with_timestamp = {
            "timestamp": timestamp,
            "data": self.data
        }
        return json.dumps(data_with_timestamp)

    def start_server(self):
        print("in start server")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client, addr = self.server.accept()
            print(f"Connected to {addr}")
            # data = self.server.recv(1024).decode()
            # client_handler = threading.Thread(target=self.handle_client, args=(client, addr))
            # client_handler.start()
            handle_client_thread = threading.Thread(target=self.handle_client, args=(client, addr))
            handle_client_thread.daemon = True
            handle_client_thread.start()
            # client_handler = threading.Thread(target=self.handle_client, args=(client,))
            # client_handler.start()

    def handle_client(self, client, addr):
        while True:
            try:
                
                    # data = self.get_data_with_timestamp(addr)  # Include client address in the data
                    # client.sendall(data.encode())
                    # receive data from the client
                    # wait for data from the client
                    
                    data = client.recv(1024).decode()
                    if data:
                        print("Received data:", data)
                        # self.firefighter_data_handler(data)
                        try: 
                            firefighter = json.loads(data)
                            self.update_firefighter_widget(firefighter["id"], new_firefighter_data=firefighter)
                            self.refresh_data()
                        except Exception as e:
                            print("Error in updating firefighter widget", e)
                    # time.sleep(1)  # Simulate data update every 1 second
            except ConnectionResetError:
                print(f"Client {addr} disconnected")
                client.close()

        # while True:
        #     try:
        #         data = self.server.recv(1024).decode()
        #         print("Received data:", data)
        #         # pass
        #         # data_dict = json.loads(data)
        #         self.refresh_data()
        #     # catch all errors
        #     except Exception as e:
        #         print("Connection to the server closed")
        #         # try to reconnect
        #         self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #         self.server.connect((self.host, self.port))
        #         # continue
        #         # break
        #     self.update_labels([])
            
        #     data = self.client_socket.recv(1024).decode()
        #     print("Received data:", data)
        #     data_dict = json.loads(data)
        #     self.update_labels(data_dict["data"])
        #     self.refresh_data()
        # l = self.render_firefighter_data()

    # def create_firefighter_data_widgets(self, tab_frame):
        
    #     self.rendred_firefighters  = demo_firefighter_data
    #     for firefighter in self.rendred_firefighters:
    #         # put a divider between the firefighter data
    #         divider = ttk.Separator(tab_frame, orient="horizontal", style="TSeparator")
    #         divider.pack(fill="x")
    #         firefighter["gesture"] = tk.StringVar()
    #         firefighter["gesture"].set("None")
    #         firefighter["frame"] = tk.Frame(tab_frame)
    #         firefighter["frame"].pack()
    #         firefighter["name_label"] = tk.Label(firefighter["frame"], text=firefighter["name"])
    #         firefighter["name_label"].pack()
    #         firefighter["location_label"] = tk.Label(firefighter["frame"], text=firefighter["location"])
    #         firefighter["location_label"].pack()
    #         # firefighter["gesture_label"] = tk.Label(firefighter["frame"], textvariable=firefighter["gesture"])
    #         firefighter["gesture_label"] = tk.Label(firefighter["frame"], textvariable=firefighter["gesture"])

    #         firefighter["gesture_label"].pack()
    #         firefighter["id"] = tk.Label(firefighter["frame"], text=firefighter["id"])
    #         firefighter["id"].pack()
    #         firefighter["wifi_strength_label"] = tk.Label(firefighter["frame"], text="Wifi Strength: Excellent")
    #         firefighter["wifi_strength_label"] = tk.Label(firefighter["frame"], text="Wifi Strength:"+firefighter["wifi_strength"])
    #         firefighter["wifi_strength_label"].pack()
    #         firefighter["last_updated_label"] = tk.Label(firefighter["frame"], text="Last Updated: {} seconds ago".format(firefighter["last_updated"]))

    #         # color code the wifi strength
    #         if "Excellent" in firefighter["wifi_strength"]:
    #             firefighter["wifi_strength_label"].config(fg="green")
    #         elif "Good" in firefighter["wifi_strength"]:
    #             firefighter["wifi_strength_label"].config(fg="blue")
    #         elif "Fair" in firefighter["wifi_strength"]:
    #             firefighter["wifi_strength_label"].config(fg="orange")
    #         elif "Poor" in firefighter["wifi_strength"]:
    #             firefighter["wifi_strength_label"].config(fg="red")
            

    #     self.rendred_firefighters[0]["id"].config(text="699")
    #     self.rendred_firefighters[1]["gesture"].set("69")
    
        # self.firefighter_data = {}  # Dictionary to store actual firefighter data
        # self.view_data = {}         # Dictionary to store view representation data
    def get_firefighter_data(self): 
        return self.firefighter_data
        
        

    def create_firefighter_data_widgets(self, tab_frame):
        # demo_firefighter_data = get_demo_firefighter_data()  # Assuming you have a function to get demo firefighter data
        # demo_firefighter_data = get_demo_firefighter_data()  # Assuming you have a function to get demo firefighter data
        demo_firefighter_data = self.get_firefighter_data()  # Assuming you have a function to get demo firefighter data
        
        for firefighter in demo_firefighter_data:
            firefighter_id = firefighter["id"]
            self.create_firefighter_widget(tab_frame, firefighter_id, firefighter)
            self.update_firefighter_widget(firefighter_id, firefighter)

    def create_firefighter_widget(self, tab_frame, firefighter_id, firefighter_data):
        # Create and pack separator
        divider = ttk.Separator(tab_frame, orient="horizontal")
        divider.pack(fill="x")

        # Create frame for firefighter widget
        frame = tk.Frame(tab_frame)
        frame.pack()

        # Store firefighter data in firefighter_data dictionary using firefighter_id as key
        self.firefighter_data[firefighter_id] = firefighter_data

        # Create view representation data and store it using firefighter_id as key
        # automate making the view data
        view_data = {}
        for key, value in firefighter_data.items():
            view_data[key + "_var"] = tk.StringVar(value=value)

        view_data["frame"] = frame
        # view_data = {
        #     "name_var": tk.StringVar(value=firefighter_data["name"]),
        #     "id_var": tk.StringVar(value=firefighter_data["id"]),
        #     "location_var": tk.StringVar(value=firefighter_data["location"]),
        #     "gesture_var": tk.StringVar(value=firefighter_data["gesture"]),
        #     "wifi_strength_var": tk.StringVar(value=firefighter_data["wifi_strength"]),
        #     "last_updated_var": tk.StringVar(value=firefighter_data["last_updated"]),
        #     "ip_var": tk.StringVar(value=firefighter_data["ip"]),
        #     "bt_id_var": tk.StringVar(value=firefighter_data["bt_id"]),
        #     "tapstrap_connected_var": tk.StringVar(value=firefighter_data["tapstrap_connected"]),
        #     "tapstrap_battery_var": tk.StringVar(value=firefighter_data["tapstrap_battery"]),
        #     "frame": frame
        # }
        self.view_data[firefighter_id] = view_data

        # Create and pack labels
        # labels = [
        #     ("Name", view_data["name_var"]),
        #     ("ID", view_data["id_var"]),
        #     ("IP", view_data["ip_var"]),
        #     ("Bluetooth ID", view_data["bt_id_var"]),
        #     ("Tapstrap Connected", view_data["tapstrap_connected_var"]),
        #     ("TapStrap Battery Percent", view_data["tapstrap_battery_var"]),
        #     ("Location", view_data["location_var"]),
        #     ("Gesture", view_data["gesture_var"]),
        #     ("Wifi Strength", view_data["wifi_strength_var"]),
        #     ("Last Updated", view_data["last_updated_var"]),
        # ]
        # automate the creation of the labels
        labels = []
        for key, value in view_data.items():
            if "var" in key:
                labels.append((key.replace("_var", ""), value))
        # for label_text, label_var in labels:
        #     label = tk.Label(frame, text=label_text + ": ", anchor="e")
        #     # label.pack(side=tk.LEFT, padx=5, pady=5)
        #     label.pack()
        #     # justfiy the text such that everything is evenly spaced 
        #     value_label = tk.Label(frame, textvariable=label_var)
        #     # value_label.pack(side=tk.LEFT, padx=5, pady=5)
        #     value_label

        # for label_text, label_var in labels:
        #     label = tk.Label(frame, text=label_text + ": ", anchor="e")
        #     # label.pack()
        #     value_label = tk.Label(frame, textvariable=label_var)
        #     # value_label.pack()

        # Create and pack treeview widget
        treeview = ttk.Treeview(frame, columns=("name", "value"), show="headings")
        treeview.pack()
        treeview.heading("name", text="firefighter name:")
        treeview.heading("value", text=firefighter_data["name"])
        # Insert firefighter data as rows in the table
        for label_text, label_var in labels:
            if type(label_var) == tk.StringVar:
                treeview.insert("", "end", values=(label_text, label_var.get()))
                # Trace changes in the StringVar and update Treeview
                label_var.trace("w", lambda *args, var=label_var, text=label_text: update_treeview(treeview, text, var))
            # if label is a normal string then just add it to the treeview
            # elif type(label_var) == str:
            #     treeview.insert("", "end", values=(label_text, label_var))


        # for label_text, label_var in labels:
        #     treeview.insert("", "end", values=(label_text, label_var.get()))
        # for label_text, label_var in labels:
        #     # label_text = tk.Label(frame, text=label_text + ": ", anchor="e")
        #     # label_var = tk.Label(frame, textvariable=label_var)
        #     # treeview.insert("", "end", values=(label_text, label_var))
        #     treeview.insert("", "end", values=(label_text, label_var))
    # Function to update Treeview with new values
  
    def update_firefighter_widget(self, firefighter_id, new_firefighter_data):
        # Update actual firefighter data
        print("firefighter id: ", firefighter_id)
        # if the firefighter id is not in the firefighter data then add it
        if firefighter_id not in self.firefighter_data:
            self.firefighter_data[firefighter_id] = new_firefighter_data
            self.create_firefighter_widget(self.tab_create_firefighter_data, firefighter_id, new_firefighter_data)
            
            # create the view data
        # for data in self.firefighter_data[firefighter_id]:
        #     view_data = self.view_data[firefighter_id]

        # check which fields are being updated
        # for data in self.firefighter_data[firefighter_id]:
        # print("data", data)
        self.firefighter_data[firefighter_id].update(new_firefighter_data)
        # Update view representation data
        view_data = self.view_data[firefighter_id]
        # print("view data:\n",view_data)

        # for key, value in view_data.items():
        #     # check if the type is a stringvar
        #     if type(value) == tk.StringVar:
        #         view_data[key].set(value.get())

        # for key, value in new_firefighter_data.items():
        #     # if key in view_data:
        #         view_data[key].set(value)

        # view_data["gesture_var"].set(new_firefighter_data["gesture"])
        # view_data["wifi_strength_var"].set("Wifi Strength: " + new_firefighter_data["wifi_strength"])
        # view_data["last_updated_var"].set("Last Updated: {} seconds ago".format(new_firefighter_data["last_updated"]))
        view_data["wifi_strength_var"].set(new_firefighter_data["wifi_strength"])
        # list of view data row names
        labels = [k for k in view_data.keys() if "var" in k]
        for l in labels:
            view_data[l].set(new_firefighter_data[l.replace("_var", "")])
        # print("labels", labels)

        # view_data["last_updated_var"].set(new_firefighter_data["last_updated"])


    def create_matplotlib_plot(self, tab_frame):
        # Create a figure
        # f = plt.Figure(figsize=(5,4), dpi=100)
        # a = f.add_subplot(111)
        # a.plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 2, 3, 13, 4, 1, 2])
        
        # # Create a canvas for the figure
        # self.canvas = FigureCanvasTkAgg(f, tab_frame)
        # self.canvas.draw()
        # self.canvas_widget = self.canvas.get_tk_widget()

        self.fig, self.ax = plt.subplots()  
        # plot a sine wave 
        x = [i for i in range(10)]
        y = [i**2 for i in range(10)]
        self.ax.plot(x, y)


        x2 = [i for i in range(10)]
        y2 = [i**3 for i in range(10)]
        self.ax.plot(x2, y2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=tab_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

    
        # self.firefighter_labels = []
        # self.firefighter_data = []

        # self.fig, self.ax = plt.subplots()
        # self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab1)
        # self.canvas_widget = self.canvas.get_tk_widget()
        # self.canvas_widget.grid(row=0, column=0, sticky="nsew")
        # self.firefighter_labels = []
        # self.firefighter_data = []

    ### TAB 3 FUNCTIONS ###
        
    def create_record_gestures_widgets(self, tab_frame):
        # Folder selection
        self.folder_label = tk.Label(tab_frame, text="Select Gesture Folder:")
        self.folder_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.folder_var = tk.StringVar()
        self.folder_entry = tk.Entry(tab_frame, textvariable=self.folder_var, width=40)
        self.folder_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")

        self.browse_button = tk.Button(tab_frame, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=0, column=2, padx=10, pady=5)

        # Gesture name entry
        self.gesture_label = tk.Label(tab_frame, text="Enter Gesture Name:")
        self.gesture_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.gesture_name_var = tk.StringVar()
        self.gesture_name_entry = tk.Entry(tab_frame, textvariable=self.gesture_name_var, width=40)
        self.gesture_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        # Record button
        self.record_button = tk.Button(tab_frame, text="Record Gesture", command=self.record_gesture)
        self.record_button.grid(row=2, column=1, padx=10, pady=5, sticky="we")

        self.stop_record_button = tk.Button(tab_frame, text="Stop Recording", command=self.stop_record_gesture)
        self.stop_record_button.grid(row=2, column=2, padx=10, pady=5, sticky="we")

        # Recording status
        self.recording_text = tk.StringVar()
        self.recording_text.set("Not Recording")
        self.recording_label = tk.Label(tab_frame, textvariable=self.recording_text)
        self.recording_label.grid(row=3, column=1, padx=10, pady=5, sticky="we")

    def browse_folder(self):
        try: 
            self.folder_path = filedialog.askdirectory(initialdir=".", title="Select Gesture Folder")
            print("Selected folder:", self.folder_path)
            if self.folder_path:
                self.folder_var.set(self.folder_path)
                print(f"Selected folder: {self.folder_path}")
        except Exception as e:
            print("Error selecting folder:", e)
            print("Please select a folder")

    def record_gesture(self):
        try: 
            gesture_name = self.gesture_name_var.get()
            print("GESTURE NAME:", gesture_name)
            folder_path = self.folder_var.get()
            print("folder path:", folder_path)
            if gesture_name and folder_path and not self.recording:
                self.recording = True
                self.recording_text.set(f"Completed Recording Gesture in folder '{folder_path}'")
                gesture_folder = os.path.join(folder_path, gesture_name)
                print(f"Gesture '{gesture_name}' recorded in folder '{gesture_folder}'")
            else:
                self.recording_text.set("Not Recording")
                print("Please enter both gesture name and select a folder.")
        except Exception as e:
            print("Error recording gesture:", e)
            self.recording_text.set(f"Error: {e}")

    def stop_record_gesture(self):
        self.recording = False
        self.recording_text.set("Not Recording")
   

        # Start receiving data
        # self.receive_data()
    def render_firefighter_data(self):
        # each firefighter will have a name, location, and gesture
        tk.Label(self.tab2, text="Firefighter Data").pack()

        for firefighter in self.rendred_firefighters:
            print("Rendering firefighter data")
            print("firefighter", firefighter)
            # turn the firefighter into a dictionary
            # firefighter = dict(firefighter)
            # create new keys for the firefighter
            # rendered["id"]+=1
            firefighter["gesture"] = tk.StringVar()
            firefighter["gesture"].set("None")
            firefighter["frame"] = tk.Frame(self.tab2)
            firefighter["frame"].pack()
            firefighter["name_label"] = tk.Label(firefighter["frame"], text=firefighter["name"])
            firefighter["name_label"].pack()
            firefighter["location_label"] = tk.Label(firefighter["frame"], text=firefighter["location"])
            firefighter["location_label"].pack()
            firefighter["gesture_label"] = tk.Label(firefighter["frame"], textvariable=firefighter["gesture"])
            firefighter["gesture_label"].pack()
            firefighter["id"] = tk.Label(firefighter["frame"], text=firefighter["id"])
            
            # rendered["id"] = str(int(rendered["id"])+1)
            # rendered["id"] = tk.Label(rendered["frame"], text=str(int(rendered["id"])+1))
            # increment id by 1 




    def refresh_data(self):
        # self.client_socket.sendall("Refresh".encode())
        # self.root.after(1000, self.refresh_data)
        self.root.update_idletasks()
        self.root.update()
    
    # def update_firefighter_data(self, data):
    #     self.firefighter_data = data
    #     for firefighter in self.firefighter_data:
    #         firefighter["gesture"] = tk.StringVar()
    #         firefighter["gesture"].set("None")

    def update_labels(self, data):
        # strength = data["strength"]
        # names = data["names"]
        # locations = data["locations"]
        # self.strength_label.config(text=f"Bluetooth/Wi-Fi Strength: {strength}")
        # self.names_label.config(text=f"Firefighter Names: {names}")
        # self.locations_label.config(text=f"Firefighter Locations: {locations}")
        self.time_label.config(text=f"Time: {time.ctime()}")
        # update firefighter data
        # self.render_firefighter_data()
        for firefighter in get_demo_firefighter_data():
            # pass
            firefighter_id = firefighter["id"]
            self.update_firefighter_widget(firefighter_id, firefighter)
            # firefighter["gesture"].set("None")
        # self.update_firefighter_widget()
        # self.render_firefighter_data()
        # print("Updated labels")

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    # run server in a separate thread
    # app.start_server()
    server_thread = threading.Thread(target=app.start_server)
    # run the thread in daemon mode so that it automatically stops when the main program exits
    server_thread.daemon = True
    server_thread.start()
    # run the receive_data method in a separate thread
    # receive_data_thread = threading.Thread(target=app.receive_data)
    # run the thread in daemon mode so that it automatically stops when the main program exits
    # receive_data_thread.daemon = True
    # receive_data_thread.start()
    # run tk in main loop

    root.mainloop()

# User
# I want to have a matplotlib chart within a tab named "realtime mesh network structure"
# I want it to use the lsit of firefighters, and show how the networks are chained together.  I want my computer to be seen as the abse station, and each firefighter should be a node thats connecting. Make this a function as this will be changing in real time, and the tree/graph structure will change 