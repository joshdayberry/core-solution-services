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
LLM Generation Service
"""
from common.models import UserChat
from common.utils.errors import ResourceNotFoundException
from common.utils.http_exceptions import InternalServerError
from common.utils.logging_handler import Logger
from common.config import PROJECT_ID
from services.langchain_service import langchain_llm_generate
from typing import Optional
from config import (LANGCHAIN_LLM, GOOGLE_LLM, GOOGLE_MODEL_GARDEN,
                    OPENAI_LLM_TYPE_GPT3_5, VERTEX_LLM_TYPE_BISON_TEXT,
                    CHAT_LLM_TYPES, REGION)
from vertexai.preview.language_models import (ChatModel, TextGenerationModel)
from google.cloud import aiplatform
import time

Logger = Logger.get_logger(__file__)

async def llm_generate(prompt: str, llm_type: str) -> str:
  """
  Generate text with an LLM given a prompt.

  Args:
    prompt: the text prompt to pass to the LLM

    llm_type: the type of LLM to use (default to openai)

  Returns:
    the text response: str
  """
  Logger.info(f"Generating text with an LLM given a prompt={prompt},"
              f" llm_type={llm_type}")
  # default to openai LLM
  if llm_type is None:
    llm_type = OPENAI_LLM_TYPE_GPT3_5

  try:
    start_time = time.time()
    # for google models, prioritize native client over langchain
    if llm_type in GOOGLE_MODEL_GARDEN.keys():
      aip_endpoint_name = GOOGLE_MODEL_GARDEN.get(llm_type)
      response = await model_garden_predict(prompt, aip_endpoint_name)
    elif llm_type in GOOGLE_LLM.keys():
      google_llm = GOOGLE_LLM.get(llm_type, VERTEX_LLM_TYPE_BISON_TEXT)
      is_chat = llm_type in CHAT_LLM_TYPES
      response = await google_llm_predict(prompt, is_chat, google_llm)
    elif llm_type in LANGCHAIN_LLM.keys():
      response = await langchain_llm_generate(prompt, llm_type)
    else:
      raise ResourceNotFoundException(f"Cannot find llm type '{llm_type}'")

    process_time = round(time.time() - start_time)
    Logger.info(f"Received response in {process_time} seconds from "
                f"model with llm_type={llm_type}.")
    return response
  except Exception as e:
    raise InternalServerError(str(e)) from e


async def llm_chat(prompt: str, llm_type: str,
                   user_chat: Optional[UserChat] = None) -> str:
  """
  Send a prompt to a chat model and return response.

  Args:
    prompt: the text prompt to pass to the LLM
    llm_type: the type of LLM to use (default to openai)
    user_chat (optional): a user chat to use for context

  Returns:
    the text response: str
  """
  Logger.info(f"Generating chat with llm_type=[{llm_type}].")
  Logger.debug(f"prompt=[{prompt}].")
  if llm_type not in CHAT_LLM_TYPES:
    raise ResourceNotFoundException(f"Cannot find chat llm type '{llm_type}'")

  try:
    response = None
    if llm_type in GOOGLE_LLM.keys():
      google_llm = GOOGLE_LLM.get(llm_type)
      is_chat = True
      response = await google_llm_predict(prompt, is_chat,
                                          google_llm, user_chat)
    elif llm_type in LANGCHAIN_LLM.keys():
      response = await langchain_llm_generate(prompt, llm_type, user_chat)
    return response
  except Exception as e:
    raise InternalServerError(str(e)) from e


async def model_garden_predict(prompt: str,
    aip_endpoint_name: str, parameters: dict = None) -> str:
  """
  Generate text with a Model Garden model.
  Args:
    prompt: the text prompt to pass to the LLM
    aip_endpoint_name: endpoint id from the Vertex AI online predictions
    parameters (optional):  parameters to be used for prediction

  Returns:
    the prediction text.
  """
  aip_endpoint = f"projects/{PROJECT_ID}/locations/" \
                 f"{REGION}/endpoints/{aip_endpoint_name}"
  Logger.info(f"Generating text using Model Garden "
              f"endpoint=[{aip_endpoint}], prompt=[{prompt}], "
              f"parameters=[{parameters}.")

  if parameters is None:
    parameters = {
        "prompt": f"'{prompt}'",
        "max_tokens": 900,
        "temperature": 0.2,
        "top_p": 1.0,
        "top_k": 10,
    }
  else:
    parameters.update({"prompt": f"'{prompt}'"})

  instances = [parameters, ]

  endpoint_without_peft = aiplatform.Endpoint(aip_endpoint)

  response = endpoint_without_peft.predict(instances=instances)
  predictions_text = "\n".join(response.predictions)
  Logger.info(f"Received response from "
              f"{response.model_resource_name} version="
              f"[{response.model_version_id}] with {len(response.predictions)}"
              f" prediction(s) = [{predictions_text}] ")

  return predictions_text


async def google_llm_predict(prompt: str, is_chat: bool,
                             google_llm: str, user_chat=None) -> str:
  """
  Generate text with a Google LLM given a prompt.

  Args:
    prompt: the text prompt to pass to the LLM
    is_chat: true if the model is a chat model
    google_llm: name of the vertex llm model
    user_chat:

  Returns:
    the text response.
  """
  Logger.info(f"Generating text with a Google LLM given a prompt,"
              f" is_chat=[{is_chat}], google_llm=[{google_llm}]")
  Logger.debug(f"prompt=[{prompt}].")
  prompt_list = []
  if user_chat is not None:
    history = user_chat.history
    for entry in history:
      content = UserChat.entry_content(entry)
      if UserChat.is_human(entry):
        prompt_list.append(f"Human input: {content}")
      elif UserChat.is_ai(entry):
        prompt_list.append(f"AI response: {content}")
  prompt_list.append(prompt)
  context_prompt = prompt.join("\n\n")

  # Temperature controls the degree of randomness in token selection.
  # Token limit determines the maximum amount of text output.
  # Tokens are selected from most probable to least until the sum of
  #  their probabilities equals the top_p value.
  # top_k of 1 means the selected token is the most probable among all tokens.

  parameters = {
    "temperature": 0.2,
    "max_output_tokens": 1024,
    "top_p": 0.95,
    "top_k": 40,
  }

  try:
    if is_chat:
      chat_model = ChatModel.from_pretrained(google_llm)
      chat = chat_model.start_chat(max_output_tokens=1024)
      response = await chat.send_message_async(context_prompt, **parameters)
    else:
      text_model = TextGenerationModel.from_pretrained(google_llm)
      response = await text_model.predict_async(
          context_prompt,
          **parameters,
      )

  except Exception as e:
    raise InternalServerError(str(e)) from e

  Logger.info(f"Received response from the Model [{response.text}]")
  response = response.text

  return response
