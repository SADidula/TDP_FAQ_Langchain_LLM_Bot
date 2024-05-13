@DeprecationWarning
def open_ai_res():
    response = OpenAI().chat.completions.create(
    model=model_open,
    messages=[
        {"role": "user", "content": question},
        ]
    )

    return response.choices[0].message.content

@DeprecationWarning
def typewriter():
    container = st.empty()
    for index in range(len(text) + 1):
        curr_full_text: str = "".join(text[:index])
        container.markdown(curr_full_text)
        time.sleep(1/speed)
        
@DeprecationWarning
def play_voice_on_req(response: str):
    file = voice.construct_voice(response=response)
    # Open the WAV file
    wf = wave.open(os.getcwd() + '/' + file, 'rb')

    # Instantiate PyAudio
    p = pyaudio.PyAudio()

    # Open a stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read data
    data = wf.readframes(1024)

    # Play the sound
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    # Close the stream and PyAudio
    stream.close()
    p.terminate()    
