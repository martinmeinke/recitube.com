import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from youtube_recipe import get_transcript_service, get_ingredient_extractor, RecipesResponse, Config

EXAMPLES = [
    "gDGA1Wk8Olg",
    "6UMM_0NLVEk",
    "wF1WCnV5Cyc",
    "pCaOLQAq9KQ",
    "yL2vn0Jhduw",
    "mhDJNfV7hjk",
    "i7grGgKZqio",
    "tX2dliC5zU4",
    "UIOW18kRDEA",
    "UTV0q9qQUXY",
]

c = Config()
transcript_service = get_transcript_service(c)
ingredient_extractor = get_ingredient_extractor(c)

def fetch_and_extract(example: str) -> RecipesResponse | None:
    ts = transcript_service.get_transcript(example)
    if ts is not None:
        recipes_response = ingredient_extractor.extract(ts)
        print(recipes_response)
        return RecipesResponse(recipes=recipes_response)
    return None


if __name__ == "__main__":
    num_successful = 0
    for example in EXAMPLES:
        try:    
            r = fetch_and_extract(example)
            if r is not None:
                num_successful += 1
        except Exception as e:
            print(e)
            pass 

    print(f"Successfully extracted {num_successful}/{len(EXAMPLES)} recipes")
