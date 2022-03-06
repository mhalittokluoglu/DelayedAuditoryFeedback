import sounddevice as sd

import tkinter as tk
import threading



class DAF:
    def __init__(self, win):
        self.win = win
        self.condition = False
        latency_label = tk.Label(win, text = 'Latency[ms]:')
        feedback_label = tk.Label(win, text = 'Feedback Amplitude:')
        self.feedback_e = tk.Entry(win)
        self.latency_e = tk.Entry(win)
        self.latency_e.insert(tk.END, "200.0")
        self.delay = float(self.latency_e.get()) / 1000
        self.latency_e.bind('<Return>', self.Latency_Changed)

        self.feedback_amp = 20.0
        self.feedback_e.insert(tk.END, '20.0')
        self.feedback_e.bind('<Return>', self.Amplitude_Changed)

        self.start_button = tk.Button(win, text = 'Start', command = self.Start)
        self.ApplicationRunning = True
        self.thread_exit_condition = False
        self.thread_exit_mutex = threading.Lock()

        latency_label.grid(row = 0, column = 0)
        feedback_label.grid(row = 1, column = 0)
        self.latency_e.grid(row = 0, column = 1)
        self.feedback_e.grid(row = 1, column = 1)
        self.start_button.grid(row = 2, columnspan = 2)
        stream_thread = threading.Thread(target = self.StartStream)
        stream_thread.start()
        win.protocol("WM_DELETE_WINDOW", self.App_Closed)

    def callback(self, indata, outdata, frames, time, status):
        outdata[:] = indata * self.feedback_amp

    
    def Start(self):
        self.start_button['text'] = 'Stop'
        self.start_button['command'] = self.Stop
        delay = self.delay
        try:
            self.delay = float(self.latency_e.get()) / 1000
        except:
            self.delay = delay
            self.latency_e.delete("0", tk.END)
            self.latency_e.insert(tk.END, str(float(delay * 1000)))
        amp = self.feedback_amp
        try:
            self.feedback_amp = float(self.feedback_e.get())
        except:
            self.feedback_amp = amp
            self.feedback_e.delete("0", tk.END)
            self.feedback_e.insert(tk.END, str(float(amp)))
        self.condition = True

    def Stop(self):
        self.start_button['text'] = 'Start'
        self.start_button['command'] = self.Start   
        self.condition = False

    def StartStream(self):
        while True:
            self.thread_exit_mutex.acquire()
            if not self.ApplicationRunning:
                break
            self.thread_exit_mutex.release()
            if self.condition == True:
                with sd.Stream(channels=2, callback=self.callback, latency = self.delay):
                        while self.condition:
                            sd.sleep(int(200))

    def Latency_Changed(self, e):
        itwasrunning = False
        if self.condition == True:
            itwasrunning = True
            self.condition = False
        import time
        time.sleep(0.1)
        delay = self.delay
        try:
            self.delay = float(self.latency_e.get()) / 1000
        except:
            self.delay = delay
            self.latency_e.delete("0", tk.END)
            self.latency_e.insert(tk.END, str(float(delay * 1000)))
        if itwasrunning:
            self.condition = True

    def Amplitude_Changed(self, e):
        itwasrunning = False
        if self.condition == True:
            itwasrunning = True
            self.condition = False
        import time
        time.sleep(0.1)
        amp = self.feedback_amp
        try:
            self.feedback_amp = float(self.feedback_e.get())
        except:
            self.feedback_amp = amp
            self.feedback_e.delete("0", tk.END)
            self.feedback_e.insert(tk.END, str(float(amp)))
        if itwasrunning:
            self.condition = True


    def App_Closed(self):
        self.condition = False
        self.thread_exit_mutex.acquire()
        self.ApplicationRunning = False
        self.thread_exit_mutex.release()
        self.win.destroy()




win = tk.Tk()
win.title("DAF")
app = DAF(win)
win.mainloop()
