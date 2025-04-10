"""
Streamlit web application for FindMyDinner.
"""
import os
import streamlit as st
from dotenv import load_dotenv
from agent.agent import FindMyDinnerAgent

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="FindMyDinner",
    page_icon="🍽️",
    layout="wide"
)

# Check for API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent" not in st.session_state:
        if OPENAI_API_KEY and GOOGLE_PLACES_API_KEY:
            st.session_state.agent = FindMyDinnerAgent(
                openai_api_key=OPENAI_API_KEY,
                places_api_key=GOOGLE_PLACES_API_KEY
            )
        else:
            st.session_state.agent = None

def main():
    """Main function to run the Streamlit app."""
    # Initialize session state
    initialize_session_state()
    
    # Display header
    st.title("🍽️ FindMyDinner")
    st.subheader("Find restaurants that are currently open near you")
    
    # API key input section
    with st.sidebar:
        st.header("API Keys")
        
        openai_key = st.text_input(
            "OpenAI API Key",
            value=OPENAI_API_KEY or "",
            type="password",
            help="Enter your OpenAI API key"
        )
        
        places_key = st.text_input(
            "Google Places API Key",
            value=GOOGLE_PLACES_API_KEY or "",
            type="password",
            help="Enter your Google Places API key"
        )
        
        if st.button("Save Keys"):
            if openai_key and places_key:
                st.session_state.agent = FindMyDinnerAgent(
                    openai_api_key=openai_key,
                    places_api_key=places_key
                )
                st.success("API keys saved successfully!")
            else:
                st.error("Both API keys are required")
        
        st.markdown("---")
        st.markdown(
            """
            ### How to use
            1. Enter your OpenAI and Google Places API keys
            2. Ask questions like:
               - "Find restaurants near New York City"
               - "What Italian restaurants are open within 2 km of my location?"
               - "Show me details about the first restaurant"
            """
        )
    
    # Check if API keys are provided
    if not st.session_state.agent:
        st.warning(
            "Please enter your OpenAI and Google Places API keys in the sidebar to use this application."
        )
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about restaurants near you..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent.run(prompt)
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_message = f"Error: {str(e)}"
                    st.error(error_message)
                    
                    # Add error message to chat history
                    st.session_state.messages.append({"role": "assistant", "content": error_message})

if __name__ == "__main__":
    main()
