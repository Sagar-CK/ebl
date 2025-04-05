from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
import json
from schemas import ChatRequest
import constants
import requests

load_dotenv()
client = genai.Client(api_key=os.getenv("API_KEY"))

app = FastAPI()



@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses from the model.
    """
    messages = request.messages

    response_data = {"text": ""} 
    
    # Convert messages to the format required by the model
    response_data = {"text": ""}
    
    print(f"Received request: {request}")
    if not os.path.exists("images"):
        os.makedirs("images")
        
    image_files = []
    image_bytes = []
    
    for url in request.photo_urls:
        img_data = requests.get(url).content
        # hash the URL to create a unique filename
        filename = url.split("/")[-1]
        with open(f"images/{filename}.jpg", "wb") as handler:
            handler.write(img_data)
            image_bytes.append(img_data)
        
        image_files.append(f"images/{filename}.jpg")

    # Define a streaming generator function
    async def event_stream():
    
        async for chunk in await client.aio.models.generate_content_stream(
            model=constants.LLM_FLASH,
            contents=[
                str(messages),
                types.Part.from_bytes(
                    data=image_bytes[0],
                    mime_type="image/jpeg",
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=constants.MUSCLE_PROMPT,
            ),

        ):
            if chunk and chunk.text:
                # Update the response data with the new chunk of text
                response_data["text"] += chunk.text
                # Yield the data as a server-sent event
                yield f"event: response\ndata: {json.dumps(response_data)}\n\n"

        # Finalize the response
        yield f"event: end\ndata: {json.dumps({'text': response_data['text']})}\n\n"

    # Return the stream as a StreamingResponse
    return StreamingResponse(event_stream(), media_type="text/event-stream")

