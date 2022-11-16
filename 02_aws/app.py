"""
  Speech to Text by Amazon Transcribe
  1. setup aws configuration
  2. pip install 

  Runtime
  ------------
  20 m Audio Mp3:  4 mins.
   1 h Audio Mp3: 12 mins.
   4 h Audio Mp3: 48 mins.
"""
# Custom
from modules.custom_waiter import CustomWaiter, WaitState
from modules import utils
# Basic
import requests
from botocore.exceptions import ClientError
import logging
import os

import sys
import time
import boto3
s3_resource = boto3.resource('s3')
transcribe_client = boto3.client('transcribe')

from pydub import AudioSegment

# Parameter
# ----------------------------------------
dir_path = os.path.dirname(os.path.realpath(__file__))
path_input = f'{dir_path}/01_data'
path_output = f'{dir_path}/02_output'
bucket_name = f'speech-to-text-amazontranscribe-api'

srt_filepath = ""
text_filepath = ""

# Log
logger = logging.getLogger(__name__)
# create file handler that logs debug and higher level messages
fh = logging.FileHandler(f'{dir_path}/log/{utils.get_date()}.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers(asctime name levelname message)
formatter = logging.Formatter('[%(asctime)s] %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

# Classes
# ----------------------------------------


class TranscribeCompleteWaiter(CustomWaiter):
    """
    Waits for the transcription to complete.
    """

    def __init__(self, client):
        super().__init__(
            'TranscribeComplete', 'GetTranscriptionJob',
            'TranscriptionJob.TranscriptionJobStatus',
            {'COMPLETED': WaitState.SUCCESS, 'FAILED': WaitState.FAILURE},
            client)

    def wait(self, job_name):
        self._wait(TranscriptionJobName=job_name)


class VocabularyReadyWaiter(CustomWaiter):
    """
    Waits for the custom vocabulary to be ready for use.
    """

    def __init__(self, client):
        super().__init__(
            'VocabularyReady', 'GetVocabulary', 'VocabularyState',
            {'READY': WaitState.SUCCESS}, client)

    def wait(self, vocabulary_name):
        self._wait(VocabularyName=vocabulary_name)

# Modules
# ----------------------------------------

# snippet-start:[python.example_code.transcribe.StartTranscriptionJob]
def start_job(
        job_name, media_uri, media_format, language_code, transcribe_client,
        vocabulary_name=None):
    """
    Starts a transcription job. This function returns as soon as the job is started.
    To get the current status of the job, call get_transcription_job. The job is
    successfully completed when the job status is 'COMPLETED'.
    :param job_name: The name of the transcription job. This must be unique for
                     your AWS account.
    :param media_uri: The URI where the audio file is stored. This is typically
                      in an Amazon S3 bucket.
    :param media_format: The format of the audio file. For example, mp3 or wav.
    :param language_code: The language code of the audio file.
                          For example, en-US or ja-JP
    :param transcribe_client: The Boto3 Transcribe client.
    :param vocabulary_name: The name of a custom vocabulary to use when transcribing
                            the audio file.
    :return: Data about the job.
    """
    try:
        job_args = {
            'TranscriptionJobName': job_name,
            'Media': {'MediaFileUri': media_uri},
            'MediaFormat': media_format,
            'LanguageCode': language_code,
            'Subtitles': {
                'Formats': ['srt'],
                'OutputStartIndex': 0
            }, }
        if vocabulary_name is not None:
            job_args['Settings'] = {'VocabularyName': vocabulary_name}
        response = transcribe_client.start_transcription_job(**job_args)
        job = response['TranscriptionJob']
        logger.info("Started transcription job %s.", job_name)
    except ClientError:
        logger.exception("Couldn't start transcription job %s.", job_name)
        raise
    else:
        return job


# snippet-start:[python.example_code.transcribe.GetTranscriptionJob]
def get_job(job_name, transcribe_client):
    """
    Gets details about a transcription job.
    :param job_name: The name of the job to retrieve.
    :param transcribe_client: The Boto3 Transcribe client.
    :return: The retrieved transcription job.
    """
    try:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name)
        job = response['TranscriptionJob']
        logger.info("Got job %s.", job['TranscriptionJobName'])
    except ClientError:
        logger.exception("Couldn't get job %s.", job_name)
        raise
    else:
        return job
# snippet-end:[python.example_code.transcribe.GetTranscriptionJob]

# snippet-start:[python.example_code.transcribe.DeleteTranscriptionJob]


def delete_job(job_name, transcribe_client):
    """
    Deletes a transcription job. This also deletes the transcript associated with
    the job.
    :param job_name: The name of the job to delete.
    :param transcribe_client: The Boto3 Transcribe client.
    """
    try:
        transcribe_client.delete_transcription_job(
            TranscriptionJobName=job_name)
        logger.info("Deleted job %s.", job_name)
    except ClientError:
        logger.exception("Couldn't delete job %s.", job_name)
        raise
# snippet-end:[python.example_code.transcribe.DeleteTranscriptionJob]

def slice_audio(filepath):
    """
        Split a audio file into multiple tracks every 20 mins
    """
    tmp_filename = utils.get_filename(filepath)
    tmp_list = []
    
    #m seconds
    time_range = 20 * 60 # 20 mins
    t1 = 0 
    t2 = 0
    newAudio = AudioSegment.from_mp3(filepath)
    
    # length
    time_max = newAudio.duration_seconds
    while t2 < time_max:
        t1 = t2 if t2 > 0 else 0
        t2 = t2 +  time_range if t2 +  time_range < time_max else time_max
        newAudio_part = newAudio[int(t1*1000):int(t2*1000)]
        newAudio_part_path = f"{dir_path}/tmp/{tmp_filename}__{int(t1)}__{int(t2)}.mp3"
        newAudio_part.export(newAudio_part_path, format="mp3") #Exports to a new file
        tmp_list.append(newAudio_part_path)

    return tmp_list


# ----------------------------------------------------------
def init():
    """nothing to do"""


def main(media_object_key):
    """Use the Amazon Transcribe service."""
    global srt_filepath, text_filepath

    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s: %(message)s')

    logger.info('-'*88)
    logger.info("Amazon Transcribe Start!")
    logger.info('-'*88)

    # Get bucket
    try:
        bucket = s3_resource.Bucket(bucket_name)
    # Create bucket
    except:
        bucket = s3_resource.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': transcribe_client.meta.region_name})
    logger.info(f"bucket: {bucket_name}.")

    # Transcribe Audio
    media_file_name = f"{path_input}/{media_object_key}"

    # init file
    srt_filepath = f'{path_output}/{media_object_key}.srt'
    with open(srt_filepath, "w", encoding='utf-8') as file:
        file.write('')
    file.close()
    text_filepath = f'{path_output}/{media_object_key}.txt'
    with open(text_filepath, "w", encoding='utf-8') as file:
        file.write('')
    file.close()

    logger.info(f"Spliting media file {media_file_name}.")
    audio_list = slice_audio(media_file_name)
    for audio in audio_list:
        tmp_filename = f'{utils.get_filename(audio)}.mp3'
        analysis_audio(bucket, bucket_name, audio, tmp_filename)


def analysis_audio(bucket, bucket_name, media_file_name, media_object_key):
    """note"""

    # Upload to S3
    logger.info(f"Uploading media file {media_file_name}.")
    bucket.upload_file(media_file_name, media_object_key)
    media_uri = f's3://{bucket.name}/{media_object_key}'

    # Create job
    job_name_simple = f'{media_object_key}-{time.time_ns()}'
    logger.info(f"Starting transcription job {job_name_simple}.")

    # Start job
    start_job(
        # en-US zh-TW
        job_name_simple, f's3://{bucket_name}/{media_object_key}', 'mp3', 'zh-TW',
        transcribe_client)
    transcribe_waiter = TranscribeCompleteWaiter(transcribe_client)
    transcribe_waiter.wait(job_name_simple)

    # Get job
    job_simple = get_job(job_name_simple, transcribe_client)

    # Get Subtitle
    response_srt = requests.get(job_simple['Subtitles']['SubtitleFileUris'][0])
    with open(srt_filepath, "a", encoding='utf-8') as file:
        file.write(response_srt.content.decode('utf-8'))
    file.close()
    logger.info(f'saved: {srt_filepath}')

    # Get Text
    response_text = requests.get(job_simple['Transcript']['TranscriptFileUri']).json()
    with open(text_filepath, "a", encoding='utf-8') as file:
        file.write(response_text['results']['transcripts'][0]['transcript'])
    file.close()
    logger.info(f'saved: {text_filepath}')


# ----------------------------------------------------------------
if __name__ == "__main__":

    try:
        if len(sys.argv[1:]) != 1:
            raise Exception("Args is not correct.")
        
        filename = sys.argv[1]
        init()

        main(filename)

    except Exception as err:
        logger.error(f"[ERROR] {err}")
