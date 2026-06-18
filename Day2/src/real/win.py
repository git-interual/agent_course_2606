import tkinter as tk
from tkinter import scrolledtext
import threading
import asyncio
import agent

# Tkinter와 asyncio는 각각 자신의 이벤트 루프를 사용한다.
# Tkinter의 mainloop는 메인 스레드에서 실행해야 하므로, API 통신을 담당할
# asyncio 이벤트 루프는 별도로 만들고 백그라운드 스레드에서 실행한다.
api_loop = asyncio.new_event_loop()

def run_api_loop():
    # 새 스레드에서는 기본 asyncio 이벤트 루프가 자동으로 연결되지 않는다.
    # 따라서 위에서 만든 api_loop를 이 스레드의 이벤트 루프로 명시적으로 등록한다.
    asyncio.set_event_loop(api_loop)

    # API 요청이 들어올 때까지 이벤트 루프를 계속 대기시킨다.
    # 실제 코루틴은 send_message()에서 run_coroutine_threadsafe()로 전달된다.
    api_loop.run_forever()

# daemon=True로 실행하면 GUI 창이 종료될 때 이 백그라운드 스레드도 함께 종료된다.
threading.Thread(target=run_api_loop, daemon=True).start()

# 애플리케이션의 최상위 창을 만들고 크기를 고정한다.
win = tk.Tk()
win.title("ChatGPT 챗봇")
win.geometry("500x700")
win.resizable(False, False)

# 채팅 내역 표시 영역을 입력 영역과 분리하기 위한 프레임이다.
# expand=True와 fill=tk.BOTH를 함께 사용해 남는 공간을 모두 채운다.
chat_frame = tk.Frame(win)
chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# ScrolledText는 Text 위젯에 세로 스크롤바가 결합된 위젯이다.
# state=tk.DISABLED로 두어 사용자가 채팅 기록을 직접 수정하지 못하게 한다.
chat_log = scrolledtext.ScrolledText(
    chat_frame,
    wrap=tk.WORD,
    state=tk.DISABLED,
    font=("맑은 고딕", 11),
    bg="#f5f5f5",
    relief=tk.FLAT,
)
chat_log.pack(fill=tk.BOTH, expand=True)

# Text 위젯의 태그를 이용해 발신자별 글자색, 정렬, 라벨 글꼴을 구분한다.
# 실제 말풍선 위젯을 여러 개 만드는 대신 하나의 Text 영역에 스타일을 적용하는 방식이다.
chat_log.tag_config("user", foreground="#1a73e8", justify="right")
chat_log.tag_config("user_label", foreground="#1a73e8", justify="right", font=("맑은 고딕", 9, "bold"))
chat_log.tag_config("bot", foreground="#333333", justify="left")
chat_log.tag_config("bot_label", foreground="#888888", justify="left", font=("맑은 고딕", 9, "bold"))

def append_message(sender, message):
    # 평소에는 읽기 전용인 채팅창을 메시지를 넣는 동안만 잠시 활성화한다.
    chat_log.config(state=tk.NORMAL)

    # 사용자 메시지는 오른쪽, 챗봇 메시지는 왼쪽 스타일 태그를 적용한다.
    if sender == "나":
        chat_log.insert(tk.END, f"\n{sender}\n", "user_label")
        chat_log.insert(tk.END, f"{message}\n", "user")
    else:
        chat_log.insert(tk.END, f"\n{sender}\n", "bot_label")
        chat_log.insert(tk.END, f"{message}\n", "bot")

    # 메시지 추가가 끝나면 다시 읽기 전용으로 바꾸고 마지막 메시지로 스크롤한다.
    chat_log.config(state=tk.DISABLED)
    chat_log.see(tk.END)

def start_bot_message(sender):
    # 스트리밍 답변을 시작할 때 발신자 라벨을 한 번만 출력한다.
    # 이후 수신되는 여러 텍스트 조각은 append_bot_chunk()가 같은 줄에 이어 붙인다.
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, f"\n{sender}\n", "bot_label")
    chat_log.config(state=tk.DISABLED)
    chat_log.see(tk.END)

def append_bot_chunk(message):
    # API에서 도착한 스트림 조각(chunk)을 즉시 화면 끝에 추가한다.
    # 줄바꿈을 자동으로 넣지 않아 여러 조각이 하나의 자연스러운 답변으로 연결된다.
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, message, "bot")
    chat_log.config(state=tk.DISABLED)
    chat_log.see(tk.END)

def finish_bot_message():
    # 한 번의 스트리밍 응답이 끝났음을 표시하기 위해 마지막에 줄바꿈을 추가한다.
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "\n", "bot")
    chat_log.config(state=tk.DISABLED)
    chat_log.see(tk.END)

def send_message(event=None):
    # Text 위젯은 마지막에 자동으로 개행 문자를 포함하므로 strip()으로 제거한다.
    user_input = input_box.get("1.0", tk.END).strip()

    # 빈 문자열은 API로 전송하지 않는다.
    if not user_input:
        return

    # 입력창을 비우고 사용자 메시지를 채팅 기록에 먼저 표시한다.
    input_box.delete("1.0", tk.END)
    append_message("나", user_input)

    # 응답 생성 중 중복 요청이 들어가지 않도록 전송 버튼을 잠근다.
    send_btn.config(state=tk.DISABLED)

    async def stream_reply():
        # 이 코루틴은 asyncio 백그라운드 스레드에서 실행된다.
        # Tkinter 위젯은 메인 스레드에서만 안전하게 수정할 수 있으므로,
        # 모든 화면 갱신은 win.after(0, callback)으로 메인 이벤트 루프에 예약한다.
        win.after(0, lambda: start_bot_message("ChatGPT"))
        try:
            # queryStream()은 답변 전체가 아니라 생성되는 텍스트 조각을 차례로 반환한다.
            async for chunk in agent.queryStream(user_input):
                # lambda의 기본 인자에 현재 chunk를 저장해야 콜백 실행 시점에도
                # 반복문의 해당 텍스트 조각을 정확히 사용할 수 있다.
                win.after(0, lambda chunk=chunk: append_bot_chunk(chunk))
        except Exception as e:
            # 네트워크/API 오류도 메인 스레드의 채팅창에 일반 메시지처럼 표시한다.
            # e=e 역시 콜백이 나중에 실행될 때 현재 예외 객체를 유지하기 위한 처리다.
            win.after(0, lambda e=e: append_bot_chunk(f"오류가 발생했습니다: {e}"))

        # 정상 완료와 오류 발생 모두 답변 줄을 마무리하고 전송 버튼을 다시 활성화한다.
        win.after(0, finish_bot_message)
        win.after(0, lambda: send_btn.config(state=tk.NORMAL))

    # 현재 함수는 Tkinter 메인 스레드에서 호출된다.
    # 코루틴을 직접 실행하지 않고, 백그라운드의 api_loop에 스레드 안전하게 제출한다.
    # 이 덕분에 API 응답을 기다리는 동안에도 GUI가 멈추지 않고 계속 반응한다.
    asyncio.run_coroutine_threadsafe(stream_reply(), api_loop)

def close_window():
    # 창을 닫을 때 백그라운드 이벤트 루프에 종료 신호를 안전하게 전달한다.
    # call_soon_threadsafe()를 쓰는 이유는 api_loop가 다른 스레드에서 실행 중이기 때문이다.
    api_loop.call_soon_threadsafe(api_loop.stop)
    win.destroy()

# 운영체제의 창 닫기 버튼을 눌렀을 때 close_window()가 호출되도록 연결한다.
win.protocol("WM_DELETE_WINDOW", close_window)

# 화면 아래쪽의 입력창과 전송 버튼을 담는 프레임이다.
input_frame = tk.Frame(win)
input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

# 여러 줄 입력이 가능한 Text 위젯을 사용한다.
input_box = tk.Text(
    input_frame,
    height=3,
    font=("맑은 고딕", 11),
    relief=tk.SOLID,
    bd=1,
)
input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

# Enter는 메시지를 전송하고 "break"를 반환해 Text 위젯의 기본 줄바꿈을 막는다.
input_box.bind("<Return>", lambda e: (send_message(), "break")[1])

# Shift+Enter는 이벤트를 소비하지 않으므로 Text 위젯의 기본 동작인 줄바꿈이 실행된다.
input_box.bind("<Shift-Return>", lambda e: None)  # Shift+Enter는 줄바꿈

# 버튼 클릭과 Enter 입력이 모두 동일한 send_message() 함수를 사용한다.
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

# 프로그램 실행 직후 채팅창에 안내 메시지를 미리 출력한다.
append_message("ChatGPT", "안녕하세요! ChatGPT API를 이용한 챗봇입니다. 무엇이든 물어보세요.")

# Tkinter 이벤트 루프를 시작한다. 이 호출은 창이 닫힐 때까지 계속 실행된다.
win.mainloop()
