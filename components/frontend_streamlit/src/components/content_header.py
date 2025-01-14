# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Main page top content, includes logo img and select boxes
"""

from api import get_all_chat_llm_types
from pathlib import Path
import streamlit as st
import validators
import base64
import os

# Helper to read image from relative path
def add_logo(logo_path):
  logo_url = os.path.join(os.path.dirname(__file__), logo_path)
  if validators.url(logo_url) is True:
    logo = f"{logo_url}"
  else:
    logo = f"data:image/png;base64,"\
        f"{base64.b64encode(Path(logo_url).read_bytes()).decode()}"
  st.image(logo)


# Includes the logo and selection boxes for LLM type and chat mode
def display_header():
  top_content_styles = """
    <style>
      .main [data-testid="stImage"] {
        padding-top: 16px;
      }
      @media screen and (max-width: 1024px) {
        .main [data-testid="stImage"] img {
          max-width: 85% !important;
        }
      }
      @media screen and (min-width: 1024px) and (max-width: 1366px) {
        .main [data-testid="stImage"] img {
          max-width: 89% !important;
        }
      }
    </style>
  """
  st.markdown(top_content_styles, unsafe_allow_html=True)

  chat_llm_types = get_all_chat_llm_types()

  img, model, chat_mode = st.columns([6, 1.7, 1.7])
  with img:
    add_logo("../assets/rit_logo.png")
  with model:
    selected_model = st.selectbox(
        "Model", chat_llm_types)
    st.session_state.chat_llm_type = selected_model
  with chat_mode:
    selected_chat = st.selectbox(
        "Chat Mode", ["Auto", "Chat", "Plan", "Query"])
    st.session_state.default_route = selected_chat

  return {"model": selected_model, "chat_mode": selected_chat}
