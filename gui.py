import main as bot
import streamlit as st
import trubrics
import time

def typewriter(text: str, speed: int):
    # tokens = text.split()
    container = st.empty()
    for index in range(len(text) + 1):
        curr_full_text: str = "".join(text[:index])
        container.markdown(curr_full_text)
        time.sleep(1/speed)
        
# Function to handle recommendation button click
def on_recommendation_click(rec):
    st.session_state.recommendation_clicked = True
    st.session_state.selected_recommendation = rec
    
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/SADidula/TDP_FAQ_Langchain_LLM_Bot/tree/main/models)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"
    
st.title("💬 Swinburne FAQ Chatbot")
st.caption("🚀 your intellegent chatbot powered by OpenAI")
 
# URL for the logo of the assistant bot
# We need it as a separate variable because it's used in multiple places
bot_logo = 'https://pbs.twimg.com/profile_images/1739538983112048640/4NzIg1h6_400x400.jpg'
 
# We use st.session_state and fill in the st.session_state.messages list
# It's empty in the beginning, so we add the first message from the bot
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{"role": "bot",
                                    "content": "Hello, how can I help?"}]
    st.session_state['recommendation_clicked'] = False
    st.session_state['selected_recommendation'] = ""
    
# Then we show all the chat messages in Markdown format
for message in st.session_state['messages']:
    if message["role"] == 'bot':
        with st.chat_message(message["role"], avatar=bot_logo):
            st.markdown(message["content"])
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Sidebar button to end chat
if st.sidebar.button("End Chat"):
    st.sidebar.header("Feedback")
    feedback = st.selectbox("Feedback", options=["👍", "👎"], key="feedback_thumbs")
    submit_feedback = st.button("Submit Feedback")

    if submit_feedback:
        st.success("Thank you for your feedback!")
        
        # Submit feedback through trubric_emails
        if "TRUBRICS_EMAIL" in st.secrets:
            config = trubrics.init(
                email=st.secrets.TRUBRICS_EMAIL,
                password=st.secrets.TRUBRICS_PASSWORD,
            )
            collection = trubrics.collect(
                component_name="default",
                model="gpt",
                response=feedback,
                metadata={"chat": st.session_state.messages},
            )
            trubrics.save(config, collection)
            st.toast("Feedback recorded!", icon="📝")
 
if query := st.chat_input("Please ask your question here:"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.spinner('Generating response....'):
        result = bot.search(query)
        
    with st.spinner('Generating recommendations....'):
        recommendations = bot.get_recommendations(query)
        
    with st.spinner('Generating voice....'):
        voice = bot.get_voice_response(response=result)

    with st.chat_message("assistant", avatar=bot_logo):
        typewriter(text=result, speed=100)
        if recommendations:  
            st.markdown("**Recommended Questions:**")
            for rec in recommendations:
                if st.button(rec, on_click=on_recommendation_click, args=(rec,)):  # Create clickable button for each recommendation
                    pass
                
        # Display the response audio
        if voice:  
            st.markdown("**Voice Answer:**")
            st.audio(voice, format='audio/wav') 
                
    st.session_state.messages.append({"role": "bot", "content": result})
   
# If a recommendation button is clicked, automatically send it as a new question and display response
if st.session_state.recommendation_clicked:
    original_question = st.session_state.messages[-1]["content"]
    query = st.session_state.selected_recommendation
    st.session_state.messages.append({"role": "user", "content": query})
    
    with st.chat_message("user"):
        st.markdown(query)# Show the selected recommendation in the chat
        
    with st.spinner('Generating response....'):
        result = bot.search(query)
        
    with st.spinner('Generating recommendations....'):
        recommendations = bot.get_recommendations(query)
        
    with st.spinner('Generating voice....'):
        voice = bot.get_voice_response(response=result)

    with st.chat_message("assistant", avatar=bot_logo):
        typewriter(text=result, speed=100)
        # Display the response audio
        st.audio(voice, format='audio/wav') 
        
    st.session_state.messages.append({"role": "bot", "content": original_question})
    st.session_state.messages.append({"role": "bot", "content": result})
    st.session_state.recommendation_clicked = False  # Reset recommendation clicked state