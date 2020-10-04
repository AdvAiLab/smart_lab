from http.client import BadStatusLine

import speech_recognition as sr


class STT:
    def __init__(self):
        self.r = sr.Recognizer()
        print(sr.Microphone.list_microphone_names())

    def run(self, lang="zh-TW"):
        is_first = True
        while True:
            with sr.Microphone(device_index=10) as source:
                print("Say something")
                self.r.adjust_for_ambient_noise(source, duration=5)
                audio = self.r.listen(source)
                print("listened")

            try:
                speech_text = self.r.recognize_google(audio, language=lang)
                print('text: %s' % speech_text)
            except (sr.UnknownValueError, sr.RequestError, BadStatusLine) as e:
                is_first = False
                print(type(e).__name__)
                if "Too Many Requests" in str(e):
                    raise ConnectionRefusedError("Too Many Requests")
                continue
            return speech_text


if __name__ == '__main__':
    stt = STT()
    # lc = LabCast()
    while True:
        speech_text = stt.run()
        # lc.say_tts(speech_text)
