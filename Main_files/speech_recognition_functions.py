import speech_recognition as sr

def speech_to_text():
    r = sr.Recognizer()
    print(sr.Microphone.list_microphone_names())

    with sr.Microphone(device_index=0) as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            print(f"You said: {text}")
        except Exception as e:
            print(f"Didn't catch what you said, please retry. Error: {e}")
            speech_to_text()

speech_to_text()
