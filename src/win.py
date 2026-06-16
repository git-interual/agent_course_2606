import tkinter as tk
from tkinter import scrolledtext
import threading
import chatbot
import poem

win = tk.Tk()
win.title("ChatGPT 챗봇")
win.geometry("500x700")
win.resizable(False, False)

# 채팅 내역 표시 영역
chat_frame = tk.Frame(win)
chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

chat_log = scrolledtext.ScrolledText(
    chat_frame,
    wrap=tk.WORD,
    state=tk.DISABLED,
    font=("맑은 고딕", 11),
    bg="#f5f5f5",
    relief=tk.FLAT,
)
chat_log.pack(fill=tk.BOTH, expand=True)

# 말풍선 색상 태그
chat_log.tag_config("user", foreground="#1a73e8", justify="right")
chat_log.tag_config("user_label", foreground="#1a73e8", justify="right", font=("맑은 고딕", 9, "bold"))
chat_log.tag_config("bot", foreground="#333333", justify="left")
chat_log.tag_config("bot_label", foreground="#888888", justify="left", font=("맑은 고딕", 9, "bold"))

def append_message(sender, message):
    chat_log.config(state=tk.NORMAL)
    if sender == "나":
        chat_log.insert(tk.END, f"\n{sender}\n", "user_label")
        chat_log.insert(tk.END, f"{message}\n", "user")
    else:
        chat_log.insert(tk.END, f"\n{sender}\n", "bot_label")
        chat_log.insert(tk.END, f"{message}\n", "bot")
    chat_log.config(state=tk.DISABLED)
    chat_log.see(tk.END)

def send_message(event=None):
    user_input = input_box.get("1.0", tk.END).strip()
    if not user_input:
        return
    input_box.delete("1.0", tk.END)
    append_message("나", user_input)
    send_btn.config(state=tk.DISABLED)

    def call_api():
        try:
            if "," in user_input:
                reply = poem.get_response(user_input)
                sender = "AI 시인"
            else:
                reply = chatbot.get_response(user_input)
                sender = "ChatGPT"
        except Exception as e:
            reply = f"오류가 발생했습니다: {e}"
            sender = "ChatGPT"
        win.after(0, lambda: append_message(sender, reply))
        win.after(0, lambda: send_btn.config(state=tk.NORMAL))

    threading.Thread(target=call_api, daemon=True).start()

# 입력 영역
input_frame = tk.Frame(win)
input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

input_box = tk.Text(
    input_frame,
    height=3,
    font=("맑은 고딕", 11),
    relief=tk.SOLID,
    bd=1,
)
input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
input_box.bind("<Return>", lambda e: (send_message(), "break")[1])
input_box.bind("<Shift-Return>", lambda e: None)  # Shift+Enter는 줄바꿈

send_btn = tk.Button(
    input_frame,
    text="전송",
    font=("맑은 고딕", 11),
    bg="#1a73e8",
    fg="white",
    activebackground="#1558b0",
    relief=tk.FLAT,
    padx=12,
    command=send_message,
)
send_btn.pack(side=tk.LEFT, fill=tk.Y)

append_message("ChatGPT", "안녕하세요! ChatGPT API를 이용한 챗봇입니다. 무엇이든 물어보세요.")

win.mainloop()

