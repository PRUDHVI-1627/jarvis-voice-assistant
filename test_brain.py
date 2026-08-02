from jarvis.brain import think

history = []
reply, history = think("hello, who are you?", history)
print("jarvis:", reply)

reply, history = think("what's 12 times 7?", history)
print("jarvis:", reply)