import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="MathSolver")

st.title("MathSolver using Gemini AI")

# Get API key from user input
api_key = st.sidebar.text_input("Enter your Google AI API key", type="password")

if not api_key:
    st.warning("Please enter your API key.")
    st.stop()

# Configure Gemini API
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Maintain chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi! I can solve math problems from both photos and uploads. Choose your input method below!"}
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "mime_type" in msg:
            st.image(msg["content"], use_column_width=True)
        else:
            st.write(msg["content"])

# Input method selection
input_method = st.radio("Choose input method:", 
                       ["Take a Photo", "Upload an Image"],
                       horizontal=True)

image_source = None

if input_method == "Take a Photo":
    image_source = st.camera_input("Capture math problem", key="camera")
elif input_method == "Upload an Image":
    image_source = st.file_uploader("Upload math problem", 
                                   type=["png", "jpg", "jpeg"])
# Previous code remains the same...
if st.button("Solve", key="solve_button"):
    if image_source:
        image = Image.open(image_source)
        
        # Add user message with image to chat history
        st.session_state.messages.append({
            "role": "user",
            "content": image,
            "mime_type": "image/jpeg" if input_method == "Take a Photo" else image_source.type
        })

        # Display image in chat
        with st.chat_message("user"):
            st.image(image, use_column_width=True)

        # Generate response using Gemini API
        with st.spinner("Analyzing problem..."):
            try:
                prompt = """Solve this math problem from the image. 
                Provide detailed step-by-step explanations using only text formatting.
                Use **bold** for emphasis and mathematical expressions.
                Present the final answer clearly at the end without any HTML, boxes, or special formatting.
                """
                
                response = model.generate_content([prompt, image])
                assistant_response = response.text

                # Remove any residual HTML tags
                import re
                clean_response = re.sub('<[^<]+?>', '', assistant_response)

                # Add assistant's response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": clean_response
                })

                # Display assistant's response
                st.write("**Solution:**")
                st.markdown(clean_response)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning(f"Please {input_method.lower()} first")

# Clear history button remains the same...
# Add clear chat history button
if st.button("Clear History"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I can solve math problems from both photos and uploads. Choose your input method below!"}
    ]
    st.rerun()