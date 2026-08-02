from jarvis.wakeword import wait_for_wake_word

print("say 'hey jarvis' to test detection...")
heard = wait_for_wake_word()
print("detected:", heard)