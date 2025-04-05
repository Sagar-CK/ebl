from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from openai import OpenAI

import os
from pprint import pprint
from schemas import ChatRequest, Plan, ResponsePlan
import constants
from io import BytesIO

load_dotenv()

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
open_router_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_ROUTER_KEY"),
)

@app.post("/chat/plan")
async def chat_plan(request: ChatRequest) -> ResponsePlan:
    
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
    image_messages = []
    text_messages = []
    openai_messages = [{"role": "system", "content": system_instruction}]
    for m in request.messages:
        openai_messages.append({"role": m.role, "content": m.content})
        text_messages.append(openai_messages[-1])
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
        image_messages.append(openai_messages[-1])

    model_name = constants.LLM_FLASH
    
    if system_instruction == constants.MUSCLE_PROMPT:
        model_name = constants.LLM_PRO
            
        try:
            # remove the original system prompt
            final_messages = [{"role":"system", "content": constants.MUSCLE_PRROMPT_IMAGES}] + text_messages
            final_messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": constants.MUSCLE_PRROMPT_IMAGES,
                        },
                        *[
                            {
                                "type": "image_url",
                                "image_url": {"url": url},
                            }
                            for url in request.photo_urls or []
                        ]
                    ]
                }
            )
            pprint(final_messages)
            
            image_description = open_router_client.chat.completions.create(
                model="x-ai/grok-2-vision-1212",
                messages=final_messages,
            )
            
            print(image_description)
            if image_description.choices[0].message.refusal:
                raise HTTPException(status_code=400, detail="Refusal to generate image description.")
            
            openai_messages.append({"role": "assistant", "content": image_description.choices[0].message.content})
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
            
            return ResponsePlan(
                plan=plan_response.parsed
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    else:
        model_name = constants.LLM_FLASH
        response = client.responses.create(
            model=model_name,
            input=openai_messages,
        )
        
        return ResponsePlan(response=response.output_text)
