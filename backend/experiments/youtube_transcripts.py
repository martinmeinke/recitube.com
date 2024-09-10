import os
import xml.etree.ElementTree as ET

from googleapiclient.discovery import build
from joblib import Memory, Parallel, delayed
from langchain.prompts import PromptTemplate
from langchain_community.llms import Replicate
from tqdm import tqdm
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)

# Set up cache directory
cache_dir = "./cache"
os.makedirs(cache_dir, exist_ok=True)
memory = Memory(cache_dir, verbose=0)

CHANNEL_ID = 'UCsXVk37bltHxD1rDPwtNM8Q' # kurzgesagt
ONLY_MANUAL_CAPTIONS = False

youtube = build("youtube", "v3", developerKey=GOOGLE_API_KEY)


def get_videos_with_manual_captions(video_ids):
    """ """
    video_ids_with_captions = []

    # Use the 'videos' API to check if captions are enabled
    request = youtube.videos().list(
        part="contentDetails",
        id=",".join(video_ids),  # Join multiple video IDs in one request
    )
    response = request.execute()

    for item in response["items"]:
        # Check if captions are available for the video
        if item["contentDetails"].get("caption") == "true":
            video_ids_with_captions.append(item["id"])

    return video_ids_with_captions


def get_all_video_ids(channel_id):
    video_ids = []

    # Get the channel's uploads playlist
    request = youtube.channels().list(part="contentDetails", id=channel_id)
    response = request.execute()
    print(response)
    uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"][
        "uploads"
    ]

    # Get videos from the uploads playlist
    next_page_token = None
    while True:
        playlist_request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        )
        playlist_response = playlist_request.execute()

        video_ids_batch = [
            item["contentDetails"]["videoId"] for item in playlist_response["items"]
        ]

        if ONLY_MANUAL_CAPTIONS:
            # Check each video's captions availability
            video_ids_batch = get_videos_with_manual_captions(video_ids_batch)

        video_ids.extend(video_ids_batch)

        next_page_token = playlist_response.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids


@memory.cache
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return video_id, transcript
    except (TranscriptsDisabled, NoTranscriptFound):
        # Catch exceptions for videos without transcripts or disabled transcripts
        print(f"Skipping video {video_id} - no transcript available.")
        return None
    except ET.ParseError as e:
        print(f"XML Parse Error for video {video_id}: {e}")
        return None
    except Exception as e:
        print(f"Error fetching transcript for video {video_id}: {e}")
        return None


@memory.cache
def summarize_transcript(transcript):
    transcript_text = " ".join([item["text"] for item in transcript])

    prompt = PromptTemplate(
        input_variables=["transcript"],
        template="Summarize the following YouTube transcript:\n\n{transcript}",
    )

    llm = Replicate(
        model="meta/meta-llama-3-8b-instruct",
        model_kwargs={"temperature": 0.75, "max_length": 500, "top_p": 1},
    )

    summary = llm.invoke(
        prompt.format(transcript=transcript_text)
    )  # raw output, no stop

    return summary


if __name__ == "__main__":
    transcripts = {}
    video_ids = get_all_video_ids(CHANNEL_ID)[:10]

    print(f"Identified {len(video_ids)} videos")

    # Function to update progress bar within joblib's Parallel
    def parallel_fetch_transcripts(video_ids, n_jobs=4):
        # Use Parallel with delayed and progress bar updating
        results = list(
            tqdm(
                Parallel(return_as="generator", n_jobs=n_jobs)(
                    delayed(get_transcript)(video_id) for video_id in video_ids
                ),
                total=len(video_ids),
            )
        )
        return [r for r in results if r is not None]

    # Fetch transcripts in parallel (adjust n_jobs for the number of workers)
    transcripts = parallel_fetch_transcripts(video_ids, n_jobs=1)
    print(f"Fetched {len(transcripts)}")

    # Summarize each transcript
    summaries = {}
    for video_id, transcript in transcripts:
        if transcript:
            summaries[video_id] = summarize_transcript(transcript)

    from pprint import pprint

    pprint(summaries)
