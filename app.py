import streamlit as st
import re
from dotenv import load_dotenv
import utils

load_dotenv()
driver = utils.load_driver()
model = utils.load_model()

st.title("Match Report AI :soccer:")
st.write("""
    Get an AI generated match report of any football match with just a few clicks!        
""")
st.write('---')

url_pattern = re.compile(r"^https://www\.fotmob\.com/matches/.+$")

match_url = st.text_input("Enter [FotMob](https://www.fotmob.com/) URL of the match")
if st.button("Analyze"):
    if url_pattern.match(match_url):
        with st.spinner("Generating..."):
            stats = utils.get_match_data(match_url, driver)
            analysis = utils.model_inference(model, str(stats))
        st.subheader("Analysis")
        st.write(analysis)
    else:
        st.warning("Enter a valid url!")
