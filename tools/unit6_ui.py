"""Local desktop view. Retrieved text and model output remain plain text."""
import json
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import ttk

from src.rag_guard.unit6_app import build_app, case_documents


def main():
    cases = json.loads(Path("config/unit6_cases.json").read_text(encoding="utf-8"))
    mapping = {c["id"]: c for c in cases}
    root = tk.Tk()
    root.title("RAG Guard Unit 6 | Local research prototype")
    root.geometry("1050x760")
    ttk.Label(root, text="Synthetic cases only. Hybrid screening before local generation.").pack(pady=8)
    selection = ttk.Combobox(root, values=list(mapping), state="readonly", width=30)
    selection.set("clean-01")
    selection.pack()
    output = tk.Text(root, wrap="word", font=("Consolas", 12), padx=12, pady=12)
    output.pack(fill="both", expand=True, padx=12, pady=12)
    status = tk.StringVar(value="Ready. Select a case and run it.")
    ttk.Label(root, textvariable=status).pack(pady=5)
    mailbox = queue.Queue()

    def display(text):
        output.configure(state="normal")
        output.delete("1.0", "end")
        output.insert("end", text)
        output.configure(state="disabled")

    def work(case):
        try:
            result = build_app(case_documents(case)).run(case["query"], 1)
            mailbox.put((case, result, None))
        except Exception as exc:
            mailbox.put((case, None, type(exc).__name__))

    def run():
        case = mapping[selection.get()]
        button.configure(state="disabled")
        status.set("Running locally. The first run also loads model assets.")
        display("Question: " + case["query"] + "\n\nSource passage:\n" + case["text"])
        threading.Thread(target=work, args=(case,), daemon=True).start()

    def poll():
        try:
            case, result, error = mailbox.get_nowait()
        except queue.Empty:
            root.after(100, poll)
            return
        button.configure(state="normal")
        if error:
            status.set("Run failed: " + error + ". Check the setup with unit6_doctor.")
        else:
            audit = result["audit"]
            text = "Question: " + case["query"] + "\n\nSource passage:\n" + case["text"]
            text += "\n\nScreening evidence:\n" + json.dumps(audit["decisions"], indent=2)
            text += "\n\nAnswer:\n" + result["answer"]
            text += "\n\nRule offsets identify matched text, not the semantic model's reasoning."
            display(text)
            status.set(audit["status"] + " | {:.2f} ms".format(audit["total_ms"]))
        root.after(100, poll)

    button = ttk.Button(root, text="Run selected case", command=run)
    button.pack(pady=8)
    root.after(100, poll)
    root.mainloop()


if __name__ == "__main__":
    main()
