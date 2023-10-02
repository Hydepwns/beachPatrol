from langchain.prompts import PromptTemplate
from twspace_dl.api import API
from twspace_dl.cookies import load_cookies
from twspace_dl.twspace import Twspace
from twspace_dl.twspace_dl import TwspaceDL
import json
import time
import random
import os
import subprocess
import openai
import threading
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()


def download_twitter_space_direct(space_url, cookie_file, output_format="/tmp/spaces/%(creator_name)s-%(creator_id)s-%(title)s-%(id)s"):
    API.init_apis(load_cookies(cookie_file))
    twspace = Twspace.from_space_url(space_url)

    # Initialize TwspaceDL with a specific output format
    twspace_dl = TwspaceDL(twspace, output_format)

    # This will now use the custom output format you provided
    file_save_path = twspace_dl.filename + ".m4a"

    try:
        twspace_dl.download()
        twspace_dl.embed_cover()
    except KeyboardInterrupt:
        print("Download Interrupted by user")
    finally:
        twspace_dl.cleanup()

    if os.path.exists(file_save_path):
        return file_save_path
    else:
        return None


def monitor_twitter_spaces(user_ids, cookies_path, interval=10, variance=5):
    while True:
        for user_id in user_ids:
            log_prefix = f"[{time.strftime('%m/%d/%y %H:%M:%S')}] [tw_space@{user_id}] "

            print(f"{log_prefix} [VRB] Start trying with cookies...")
            space_url = f"https://twitter.com/{user_id}"
            download_twitter_space_direct(space_url, cookies_path)

            sleep_time = interval + random.randint(-variance, variance)
            print(f"{log_prefix} [VRB] Sleep {sleep_time} sec.")
            time.sleep(sleep_time)


def chunk_file_if_needed(file_path, max_size_mb=25):
    # Check the file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

    if file_size_mb <= max_size_mb:
        # If size is below threshold, return the original path in a list
        return [file_path]
    else:
        # If file needs chunking
        # Calculate segment time (as an estimate for now)
        # This is a basic approach. Ideally, we might want to adjust based on file bitrate
        duration = get_audio_duration(file_path)
        estimated_segment_time = int(duration * (max_size_mb / file_size_mb))

        # Create the directory to store segments
        base_name = os.path.basename(file_path).rsplit('.', 1)[0]
        segments_dir = f"/tmp/spaces/{base_name}/segments"
        os.makedirs(segments_dir, exist_ok=True)

        # Split the file into chunks
        os.system(
            f"ffmpeg -i {file_path} -f segment -segment_time {estimated_segment_time} -c copy {segments_dir}/segment%09d.mp3")

        # Return the list of chunk file paths
        return [os.path.join(segments_dir, f) for f in os.listdir(segments_dir) if f.startswith("segment")]


def get_audio_duration(file_path):
    # Using ffprobe to get the duration of the audio
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {file_path}"
    result = subprocess.check_output(cmd, shell=True)
    return float(result)


def transcribe_segments(segments, prompt):
    """
    Transcribe the audio segments using OpenAI's Whisper API.

    :param segments: List of paths to audio segment files.
    :param prompt: A prompt to provide context for the transcription.
    :return: A dictionary with segment paths as keys and their transcriptions as values.
    """

    openai.api_key = os.getenv("OPENAI_API_KEY")
    transcript = ""
    for segment in segments:
        with open(segment, "rb") as audio_file:
            res = openai.Audio.transcribe("whisper-1", audio_file)
            transcript += str(res['text'])

    return transcript


prompt_template = """
    You are an analytics professional at Lido Finance, a Liquid Staking protocol for Ethereum. You are given a transcript of Twitter Spaces in the crypto/web3 space that may or may not be related to Lido.
    Given the transcript, you are writing structured notes in markdown format. Think of your notes as key takeaways, TLDRs, and executive summaries.

    Your notes should be concise, detailed, and structured by topics. You know what information is especially important, and what is less important.
    
    Here is the transcript:
    {text}
    
    YOUR NOTES:"""

refine_template = """
    You are an analytics professional at Lido Finance, a Liquid Staking protocol for Ethereum. You are given a transcript of Twitter Spaces in the crypto/web3 space that may or may not be related to Lido.
    Given the transcript, you are refining structured notes in markdown format. Think of your notes as key takeaways, TLDRs, and executive summaries.

    Here is the existing note:
    {existing_answer}
    
    We have the opportunity to refine the existing note (only if needed) with some more context below:
    -----
    {text}
    -----
    
    Given the new context, refine the original note to make it more complete.
    If the context isn't useful, return the original summary.

    Your notes should be concise, detailed, and structured by topics. You know what information is especially important, and what is less important.

    Use markdown formatting to its fullest to produce visually appealing, structured notes.
    """

prompt = PromptTemplate.from_template(prompt_template)
refine_prompt = PromptTemplate.from_template(refine_template)


def summarize_transcript(transcript):
    try:
        doc = Document(page_content=transcript)

        # Summarize the document
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=40000, chunk_overlap=500, length_function=len, is_separator_regex=False)
        docs = text_splitter.split_documents([doc])
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
        chain = load_summarize_chain(llm, chain_type="refine",
                                     question_prompt=prompt,
                                     refine_prompt=refine_prompt,
                                     return_intermediate_steps=True,
                                     input_key="input_documents",
                                     output_key="output_text")

        result = chain({"input_documents": docs}, return_only_outputs=True)

        return result["output_text"]

    except Exception as e:
        print(f"Error summarizing transcript: {e}")
        return "Error summarizing transcript"


def process_twitter_space(space_url, cookies_path):
    transcript_location = download_twitter_space_direct(
        space_url, cookies_path)
    chunks = chunk_file_if_needed(transcript_location)
    transcript = transcribe_segments(
        chunks, "Twitter Space about Crypto, Web3, Liquid Staking, and Lido Finance")
    summary = summarize_transcript(transcript)

    return summary
