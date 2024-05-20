import streamlit as st
import time
import main as bot
import speech_recognition as sr

class GUI:    
    def __init__(self) -> None: 
        
        self.isRecommended: bool = False
        self.isTTS: bool = False
        self.isSTT: bool = False
        self.recommendations: list[str] = []
        self.result = ""
      
        self.bot_logo = "images/assistant.jpeg"
        self.user_logo = "images/user.jpeg"

        self.recognizer = sr.Recognizer()

        self.meta()
        self.css()
        self.sidebar() 
        self.style()
        self.conversation_layout()
        self.converse()
    
    def meta(self):
        st.set_page_config(
            page_title="Swinburne FAQ chatbot",
            page_icon="🧊",
            layout="wide",
            initial_sidebar_state="expanded",
        )
        
    def css(self):
        # Inject custom CSS to set the width of the sidebar
        st.markdown(
            """
            <style>
                .st-emotion-cache-6qob1r {
                    border-top-right-radius: 10px;
                    background-image: linear-gradient(#00c6cf33,#FFFFFF) !important;
                    width: max-contents;
                }
                .st-emotion-cache-1v0mbdj img {
                    border-radius: 35px !important;
                }
                .st-emotion-cache-1c7y2kd {
                    background-color: #ffffff00 !important;
                }
                .st-emotion-cache-4oy321 {
                    background-image: linear-gradient(#FFFFFF, #00c6cf33) !important;
                }
                .st-emotion-cache-1h9usn1 {
                    background-color: #ffffff
                }
                .st-emotion-cache-q3uqly, .st-emotion-cache-nbt3vv{
                    position: fixed;
                    bottom: 110px;
                    z-index:1;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
                             
    def style(self):
        self.user_input = st.chat_input("Please ask your question")  
        if self.isSTT: 
            st.button("🎙️ Record", use_container_width=False, type="primary", on_click=self.record_voice)  
    
    def sidebar(self):    
        with st.sidebar:
            st.image("images/title.jpeg", width=200)
            st.title("Welcome to Swinburne Frequently Asked Questions")
            st.caption(":grey[Chat with a FAQ assistant, your intelligent AI powered by OpenAI]") 
            st.divider()
            
            popover = st.popover("Accessibility Options")
            self.isRecommended = popover.toggle("Recommendations", value=False)
            self.isTTS = popover.toggle("Text-To-Speech", value=False)
            self.isSTT = popover.toggle("Speech-To-Text", value=False)
            
    def recommendation_layout(self):
        with st.expander('Prompt Suggestions For You', expanded=False):
            if len(self.recommendations) <= 0:
                pass
            else:
                for recommend in self.recommendations:
                    st.button(recommend, use_container_width=False, on_click=self.on_recommendation_click, args=(recommend,))  
                    
    def tts_layout(self, file: str):
        with st.expander('Voice Response For You', expanded=False):
            st.audio(file, format='audio/wav') 
                    
    def conversation_layout(self): 
        if 'messages' not in st.session_state:
            st.session_state['messages'] = [{"role": "bot",
                                    "content": "Welcome to Swinburne University Online! Let me know if I can help with anything today."}]
            
        for message in st.session_state['messages']:
            if message["role"] == 'bot':
                with st.chat_message(message["role"], avatar=self.bot_logo):
                    st.markdown(message["content"])
            elif message['role'] == 'user':
                with st.chat_message(message["role"], avatar=self.user_logo):
                    st.markdown(message["content"])
    
    def converse(self):
        if self.user_input:
            st.session_state.messages.append({"role": "user", "content": self.user_input})
            with st.chat_message("user", avatar=self.user_logo):
                st.markdown(self.user_input)

            with st.chat_message("assistant", avatar=self.bot_logo):
                self.generate_response()

                if self.isRecommended:
                    self.generate_recommendations()                              

                if self.isTTS:
                    self.generate_voice_response()                                
                
            st.session_state.messages.append({"role": "bot", "content": self.result})
    
    def converse_recommendation(self, recommendation: str):
        st.session_state.messages.append({"role": "user", "content": recommendation})
        with st.chat_message("user", avatar=self.user_logo):
            st.markdown(recommendation)

        with st.chat_message("assistant", avatar=self.bot_logo):
            self.generate_response(recommendation)

            if self.isRecommended:
                self.generate_recommendations()                              

            if self.isTTS:
                self.generate_voice_response()                            
                    
        st.session_state.messages.append({"role": "bot", "content": self.result})       
        
    def converse_speech_to_text(self, question: str, response: str):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user", avatar=self.user_logo):
            st.markdown(question)

        with st.chat_message("assistant", avatar=self.bot_logo):
            self.write_text_to_speech(response)
                                           
        st.session_state.messages.append({"role": "bot", "content": response})       
        
    
    def typewriter(self, text: str, speed: int):
        for word in text.split(" "):
            yield word + " "
            time.sleep(1/speed)
    
    def generate_response(self, recommendation: str = ''):
        st.toast('Generating response...', icon="⏳")
        self.result = bot.search(self.user_input + recommendation)
        st.toast('Response Generated...', icon = "✅")
        st.write_stream(self.typewriter(text=self.result, speed=35))
        
    def generate_recommendations(self):
        st.toast('Generating recommendations...', icon="⏳")
        self.recommendations = bot.get_recommendations(self.user_input)
        st.toast('Recommendation Generated...', icon = "📋")
        self.recommendation_layout()
    
    def generate_voice_response(self):
        st.toast('Generating voice response...', icon="⏳")
        voice = bot.get_voice_response(response=self.result)
        st.toast('Generated...', icon = "🔉")
        self.tts_layout(voice)
    
    def write_text_to_speech(self, response):
        st.write_stream(self.typewriter(text=response, speed=35))
        
    # Function to handle recommendation button click
    def on_recommendation_click(self, rec):
        self.converse_recommendation(recommendation=rec)
    
    def record_voice(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = self.recognizer.listen(source, 10, 3)
            rec_text = self.recognizer.recognize_google(audio)
            st.toast(rec_text + ' recorded...', icon="✅")
            st.toast('Generating response...', icon="⏳")
            result = bot.search(rec_text)
            st.toast('Response Generated...', icon = "✅")
            self.converse_speech_to_text(rec_text , result)
            
if "__main__":
    GUI()