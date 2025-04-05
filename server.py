from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI

import os
import json
from schemas import ChatRequest, Plan
import constants
import requests
from io import BytesIO

load_dotenv()

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
open_router_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_ROUTER_KEY"),
)

@app.post("/chat/plan")
async def chat_plan(request: ChatRequest):
    
    if not os.path.exists("messages"):
        os.makedirs("messages")
    path = f"messages/{request.session_id}.csv"
    with open(path, "a") as f:
        for message in request.messages:
            f.write(f"{message.role},{message.content}\n")

    # Select the appropriate system instruction
    system_instruction = constants.MUSCLE_PROMPT
    if len(request.messages) // 2 == 1:
        system_instruction = constants.MUSCLE_PROMPT_MOTIVATION
    elif len(request.messages) // 2 == 2:
        system_instruction = constants.MUSCLE_PROMPT_PREV
    elif len(request.messages) // 2 == 3:
        system_instruction = constants.MUSCLE_PROMPT_NOTES

    # Construct OpenAI messages
    openai_messages = [{"role": "system", "content": system_instruction}]
    for m in request.messages:
        openai_messages.append({"role": m.role, "content": m.content})
    for url in request.photo_urls or []:
        openai_messages.append({
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": url,
                }
            ]
        })

    model_name = constants.LLM_FLASH
    
    if system_instruction == constants.MUSCLE_PROMPT:
        model_name = constants.LLM_PRO
            
        # If it's time to generate a full plan, run a two-step call
        try:
            response = open_router_client.chat.completions.create(
                model=model_name,
                messages=openai_messages,
            )

            detailed_summary = response.choices[0].message.content

            plan_prompt = [
                {"role": "system", "content": constants.MUSCLE_PLAN},
                {"role": "user", "content": detailed_summary},
            ]
            

            completion = open_router_client.beta.chat.completions.parse(
                model="o3-mini",
                messages=plan_prompt,
                response_format=Plan,
            )
            
            plan_response = completion.choices[0].message

            if plan_response.refusal:
                raise HTTPException(status_code=400, detail="Refusal to generate a plan.")   
            if not plan_response.parsed:
                raise HTTPException(status_code=400, detail="Invalid plan response.")
            
            return plan_response.parsed

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        
    else:
        model_name = constants.LLM_FLASH
        response = client.responses.create(
            model=model_name,
            input=openai_messages,
        )
        return response.output_text
