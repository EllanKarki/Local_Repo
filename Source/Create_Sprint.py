# %%
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import pandas as pd
from jira import JIRA
import logging
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

def connect_to_jira():
    jira_url = url_combobox.get()
    username = username_entry.get()
    password = password_entry.get()

    auth = (username, password)
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Make a request to Jira to verify the connection
        response = requests.get(jira_url, auth=auth, headers=headers, verify=False)

        if response.status_code == 200:
            messagebox.showinfo("Success", "Connected to Jira successfully!")
            root.destroy()  # Close the form window
            open_second_form(jira_url, auth)
        else:
            messagebox.showerror("Error", f"Failed to connect to Jira: {response.status_code}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def open_second_form(jira_url, auth):
    def submit_sprint_details():
        project_code = project_code_entry.get()
        squad_number = squad_number_entry.get()
        sprint_number = sprint_number_entry.get()
        messagebox.showinfo("User Input", f"Project Code: {project_code}\nSquad Number: {squad_number}\nSprint Number: {sprint_number}")        
        
        # Read sprint details from Excel file
        df = pd.read_excel('credentials.xlsx', sheet_name=project_code)

        # Find the row that matches the given Squad Number and Sprint Number
        matching_row = df[(df["SQNumber"] == squad_number) & (df["SPNumber"] == sprint_number)]

        if matching_row.empty:
            messagebox.showerror("Error", f"No row found with Squad Number: {squad_number} and Sprint Number: {sprint_number}")
        else:
            # Extract sprint details
            sprint_name = matching_row['SprintName'].values[0]
            start_date = matching_row['StartDate'].values[0]
            end_date = matching_row['EndDate'].values[0]
            board_id = matching_row['BoardID'].values[0]

            # Create the sprint in Jira
            data = {
                "name": sprint_name,
                "originBoardId": int(board_id),
                "startDate": start_date,
                "endDate": end_date,
            }

            response = requests.post(f"{jira_url}/rest/agile/1.0/sprint", auth=auth, headers={"Content-Type": "application/json"}, json=data, verify=False)

            if response.status_code == 201:
                messagebox.showinfo("Success", "Sprint created successfully!")
                print(f"Sprint {sprint_name} created successfully")
                #second_form.destroy()  # Close the second form window
            else:
                messagebox.showerror("Error", f"Failed to create sprint: {response.status_code}")

    second_form = tk.Tk()
    second_form.title("Sprint Details Form")
    second_form.geometry("300x200")

    tk.Label(second_form, text="Project Code:").grid(row=0, column=0, padx=10, pady=10)
    project_code_entry = tk.Entry(second_form)
    project_code_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(second_form, text="Squad Number:").grid(row=1, column=0, padx=10, pady=10)
    squad_number_entry = tk.Entry(second_form)
    squad_number_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(second_form, text="Sprint Number:").grid(row=2, column=0, padx=10, pady=10)
    sprint_number_entry = tk.Entry(second_form)
    sprint_number_entry.grid(row=2, column=1, padx=10, pady=10)

    submit_button = tk.Button(second_form, text="Submit", command=submit_sprint_details)
    submit_button.grid(row=3, columnspan=2, padx=10, pady=20)

    second_form.mainloop()

# Create the main window
root = tk.Tk()
root.title("Jira Connection Form")
root.geometry("400x200")

# Create and place the labels and entry widgets with padding
tk.Label(root, text="Jira URL:").grid(row=0, column=0, padx=10, pady=10)
url_combobox = ttk.Combobox(root, values=["https://jiraagile.sg.uobnet.com", "https://jiraagilep.sg.uobnet.com"], width=30)
url_combobox.grid(row=0, column=1, padx=10, pady=10)

url_combobox.current(0)  # Set the default value

tk.Label(root, text="Username:").grid(row=1, column=0, padx=10, pady=10)
username_entry = tk.Entry(root, width=35)
username_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Password:").grid(row=2, column=0, padx=10, pady=10)
password_entry = tk.Entry(root, show='*', width=35)
password_entry.grid(row=2, column=1, padx=10, pady=10)

# Create and place the connect button with padding
connect_button = tk.Button(root, text="Connect", command=connect_to_jira)
connect_button.grid(row=3, columnspan=2, padx=10, pady=20)

# Run the application
root.mainloop()


