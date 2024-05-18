import re
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

@st.experimental_singleton
def installff():
  os.system('sbase install geckodriver')
  os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')

def get_match_data(url, driver):
    driver.get(url + ":tab=stats")
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    data["home_team"] = get_team_data(soup, "home")
    data["away_team"] = get_team_data(soup, "away")

    return data


def get_team_data(soup, side):
    index = 0 if side == "home" else 1
    data = {}

    teams = re.findall(r"[A-Za-z ]+(?= vs)|(?<=vs )[A-Za-z ]+", soup.find("h1").text)

    data["name"] = teams[index].strip()
    data["score"] = (
        soup.find("span", {"class": re.compile(".*MFHeaderStatusScore.*")})
        .text.split("-")[index]
        .strip()
    )
    data["possesion"] = soup.find_all(
        "div", {"class": re.compile(".*PossessionSegment .*")}
    )[index].text

    data.update(get_stats(soup, side))

    return data


def get_stats(soup, side):
    index = 0 if side == "home" else 1
    stats = {}
    for stat in soup.find_all("li", {"class": re.compile(".*Stat.*")}):
        stat_name = stat.find("span", recursive=False).text
        stats[stat_name] = stat.find_all("div", recursive=False)[index].text
    return stats


def load_model():
    load_dotenv()
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        safety_settings=safety_settings,
        generation_config=generation_config,
        system_instruction=os.environ["SYSTEM_INSTRUCTION"],
    )

    return model


def model_inference(model, input):
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(input)

    return response.text


def load_driver():
    _ = installff()
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    return driver
