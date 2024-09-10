import os
import time
import json
import boto3

import googleapiclient.discovery
import requests
from typing import Optional, Tuple, List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.llms import Replicate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

from mangum import Mangum

def get_secret(secret_name: str) -> str:
    region_name = "us-east-1"

    # Create a Secrets Manager client
    client = boto3.client("secretsmanager", region_name=region_name)

    # Retrieve the secret value
    try:
        get_secret_value_response = client.get_secret_value(SecretId="recitube-backend")
        secret_string = get_secret_value_response["SecretString"]
        secrets = json.loads(secret_string)
        if secret_name not in secrets:
            raise KeyError(f"Secret '{secret_name}' not found in the secret string")
        return secrets[secret_name]
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise
    
# Configuration
class Config:
    REPLICATE_API_KEY: str = get_secret("recitube-backend-replicate-api-key")
    GOOGLE_API_KEY: str = get_secret("recitube-backend-google-api-key")
    SMARTPROXY_USERNAME: str = get_secret("recitube-backend-smartproxy-username")
    SMARTPROXY_PASSWORD: str = get_secret("recitube-backend-smartproxy-password")


# Models
class Recipe(BaseModel):
    name: str = Field(description="name of the recipe")
    ingredients: List[str] = Field(description="ingredients to make the recipe")

class RecipesResponse(BaseModel):
    recipes: List[Recipe] = Field(description="list of recipes")

# Services
class TranscriptService:
    @staticmethod
    def get_transcript(video_id: str) -> Optional[str]:
        username = Config.SMARTPROXY_USERNAME
        password = Config.SMARTPROXY_PASSWORD
        proxy = f"https://{username}:{password}@gate.smartproxy.com:7000"

        start_time = time.time()
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies={"https": proxy})
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Transcript fetched in {execution_time:.2f} seconds")
            return " ".join([item["text"] for item in transcript])
        except (TranscriptsDisabled, NoTranscriptFound, Exception) as e:
            print(e)
            return None



class TranscriptServiceOfficial:

    @staticmethod
    def get_transcript(video_id: str, api_key: str) -> str:
        # Initialize YouTube API client
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
        
        # Step 1: Get available captions for the video
        request = youtube.captions().list(
            part="id,snippet",
            videoId=video_id
        )
        response = request.execute()
        
        # Check if there are any captions available
        if not response.get('items'):
            return "No captions available for this video."

        # Take the first available caption track (you can choose based on language if needed)
        caption_id = response['items'][0]['id']
        
        # Step 2: Download the caption in SRT format
        caption_url = f"https://www.googleapis.com/youtube/v3/captions/{caption_id}"
        params = {
            "key": api_key,
            "tfmt": "srt"  # Request caption in SubRip (srt) format
        }
        caption_response = requests.get(caption_url, params=params)
        print(caption_response.text)

        if caption_response.status_code != 200:
            return f"Failed to download captions: {caption_response.status_code}"

        # Step 3: Parse the SRT caption to plain text
        return TranscriptServiceOfficial.parse_srt(caption_response.text)

    @staticmethod
    def parse_srt(srt_data: str) -> str:
        """Parses the SRT file data into plain text"""
        lines = srt_data.splitlines()
        transcript = []
        for line in lines:
            if not line.isdigit() and "-->" not in line:  # Skip index and timecode lines
                transcript.append(line)
        return " ".join(transcript)


class IngredientExtractor:
    def __init__(self, config: Config):
        self.parser = JsonOutputParser(pydantic_object=RecipesResponse)

        self.llm = Replicate(
            model="meta/meta-llama-3-8b-instruct",
            model_kwargs={"temperature": 0.75, "max_length": 1000, "top_p": 1}
        )
        self.prompt = PromptTemplate(
            input_variables=["transcript"],
            template="""This is the youtube transcript of a recipe video:\n\n{transcript}
            It might contain one or multiple recipes. I want you to list all ingredients, recipe by recipe, such that i can easily search for them online.
            Please list just the recipe title and ingredients, no amounts needed. Please return just the plain ingredient info.
            Your output must always be only JSON , here is an example response:
            
            ```
            {{[{{"name": "Tuna with rice", "ingredients": ["Tuna", "Rice"]}},{{"name": "Broccoli with garlic", "ingredients": ["garlic", "broccoli"]}}]}}
            ```

            Under no circumstances return any preamble or explanations. Start your output with the json.
            Don't output any newlines
            """,
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )

    def extract(self, transcript_text: str) -> List[Recipe]:
        chain = self.prompt | self.llm | self.parser
        return chain.invoke({"transcript": transcript_text})


# FastAPI app and dependencies
app = FastAPI()
handler = Mangum(app)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

def get_config() -> Config:
    return Config()

def get_transcript_service(config: Config = Depends(get_config)) -> TranscriptService:
    os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY
    return TranscriptService()

def get_ingredient_extractor(config: Config = Depends(get_config)) -> IngredientExtractor:
    os.environ["REPLICATE_API_TOKEN"] = config.REPLICATE_API_KEY
    return IngredientExtractor(config)

# Routes
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/extract-ingredients", response_model=RecipesResponse)
async def extract_ingredients_from_video(
    video: str,
    transcript_service: TranscriptService = Depends(get_transcript_service),
    ingredient_extractor: IngredientExtractor = Depends(get_ingredient_extractor)
) -> RecipesResponse | None:
    ts = transcript_service.get_transcript(video)
    print(ts)
    if not ts:
        raise HTTPException(status_code=404, detail="Transcript not found or unavailable for this video.")

    for attempt in range(1):
        try:
            start_time = time.time()
            recipes_response = ingredient_extractor.extract(ts)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Extraction completed in {execution_time:.2f} seconds")
            print(recipes_response)
            return RecipesResponse(recipes=recipes_response)
        except (json.JSONDecodeError, Exception) as e:
            if attempt == 2:
                raise HTTPException(status_code=500, detail="Failed to extract or parse ingredients after 3 attempts.")
            print(e)
            print(f"Attempt {attempt + 1} failed. Retrying...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

