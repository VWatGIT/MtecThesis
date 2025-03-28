import tkinter as tk
from tkinter import ttk

from datetime import datetime

class EventLogPanel:
    def __init__(self, parent, root):
        self.panel = tk.LabelFrame(parent, text="Event Log")

        self.root = root
        self.root.event_log_panel = self.panel

        # Actual Log here
        self.event_log = tk.Text(self.panel, height = 5, width = 20, state='disabled')
        self.event_log.pack(expand =True, fill="both", padx=10, pady=10)

    def log_event(self, message):
        try:
            message = str(message)
        except Exception as e:
            message = f"Error converting message to string: {e}"
            
        current_time = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{current_time}] {message}"
        self.event_log.config(state='normal')
        self.event_log.insert(tk.END, formatted_message + '\n')
        self.event_log.config(state='disabled')
        self.event_log.see(tk.END)

    def replace_last_event(self, message):
        self.delete_last_event()
        self.log_event(message)



    def delete_last_event(self):
        self.event_log.config(state='normal')
        try:
            self.event_log.delete("end-2l", "end-1l")
        except Exception as e:
            self.log_event(f"Error deleting last event: {e}")

        
        self.event_log.config(state='disabled')
    

if __name__ == "__main__":
    import time
    import threading
    
    root = tk.Tk()
    root.geometry("400x400")

    log = EventLogPanel(root, root)
    log.panel.pack(side = "top", fill = "both", expand = True)

    def test_text(log):
        def run_test(log):
            for i in range(10):
                log.log_event(f"New Test")
                if i != 0:
                    log.delete_last_event()
                log.log_event(f"Test Event {i}")
                time.sleep(0.2)
                #log.panel.after(300, log.log_event(f"Test Event {i}"))

            log.log_event("Test finished")


        test_thread = threading.Thread(target=run_test, args=(log,))
        test_thread.start()

            

    button = tk.Button(root, text="Test text", command=lambda: test_text(log))
    button.pack(side="bottom", fill="both", expand=True)
    root.mainloop()
