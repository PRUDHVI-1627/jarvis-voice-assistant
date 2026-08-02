from jarvis.stt import listen

text = listen(duration=4)
print("you said:", text)