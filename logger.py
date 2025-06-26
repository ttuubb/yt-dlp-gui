def update_log(listbox, msg, error=False):
    listbox.insert("end", msg)
    if error:
        listbox.itemconfig("end", foreground="red")
    listbox.see("end")
