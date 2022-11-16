import os
import io
import sys
from pathlib import Path
from pydub import AudioSegment

# google module
dir_path = os.path.dirname(os.path.realpath(__file__))
credential_path = f"{dir_path}/client_service_key.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path  # 'client_service_key.json' 
set_language_code = 'zh-TW' # en-US zh-TW（cmn-Hant-TW）

## v1
from google.cloud import speech
from google.cloud import speech_v1 as speech
speech_client_v1 = speech.SpeechClient()

## v2
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
speech_client_v2 = SpeechClient()

# paramter
output_text_filepath = ''

# subtitle count
count_row = 0

def init():
    """note"""

def main():
    """note"""

    global output_text_filepath

    ## Step 1. Load the media files
    ### MP3
    audio_filename = 'test_60min.mp3'
    media_file_name_mp3 = f"{dir_path}/01_data/{audio_filename}"
    filename = get_filename(audio_filename)

    # output text init
    output_text_filepath = f"{dir_path}/02_output/{filename}.txt"

    # init
    print(f"[INFO][txt] {output_text_filepath}")
    with open(output_text_filepath, 'w', encoding='utf-8') as init_file:
        init_file.write('')
    init_file.close()

    print("[INFO] Audio is analyzing and outputing.")
    # v1
    audio_list = slice_audio(media_file_name_mp3)
    for audio in audio_list:
        res1 = example_v1_1(audio)
        
        # output
        tmp_audio_filname = get_filename(audio)
        tmp_time_now = tmp_audio_filname.split('__')[1]
        output_text(res1, tmp_time_now)

    # v2
    # project_id = 'voice2word'
    # recognizer_id = 0
    # res2 = example_v2_1(project_id, recognizer_id,media_file_name_mp3)


def slice_audio(filepath):
    """note"""
    tmp_filename = get_filename(filepath)
    tmp_list = []
    
    #m seconds
    time_range = 2 * 60
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

def get_time(seconds):
    """
        return '00:03:15,904'
       
        parameter
        ---------
        1.seconds
    """
    seconds = int(seconds)

    tmp_hour = time_start//3600 if seconds >= 3600 else 0
    tmp_minute = (seconds - tmp_hour*3600)//60 if seconds - tmp_hour*3600 >= 60 else 0
    tmp_second = (seconds - tmp_hour*3600 - tmp_minute*60) if seconds - tmp_hour*3600 - tmp_minute*60 >= 0 else 0
    
    return f"{tmp_hour:02}:{tmp_minute:02}:{tmp_second:02},000"

def get_time_range(time_start, time_end):
    """
        return '00:03:15,904 --> 00:03:19,240'

        parameter
        ---------
        1.time_start: seconds
        2.time_end: seconds
    """

    tmp_start = get_time(time_start)
    tmp_end = get_time(time_end)

    return f"{tmp_start} --> {tmp_end}\n"

def get_filename(filepath):
    """note"""
    file_path = Path(filepath)
    file_name_no_extension = file_path.stem
    return file_name_no_extension

def example_v1_1(filepath):
    """
        File Size: < 10mbs, length < 1 minute
    """

    # read mp3 voice
    with open(filepath, 'rb') as f1:
        byte_data_mp3 = f1.read()


    ## Step 2. Configure Media Files Output
    # Config
    config_mp3 = speech.RecognitionConfig(
        sample_rate_hertz=48000,
        enable_automatic_punctuation=True,
        language_code=set_language_code,
        use_enhanced=True
    )

    # Audio
    audio_mp3 = speech.RecognitionAudio(content=byte_data_mp3)

    ## Step 3. Transcribing the RecognitionAudio objects
    # google cloud speech to text: recognize long_running_recognize
    operation = speech_client_v1.long_running_recognize(
        config=config_mp3,
        audio=audio_mp3
    )
    response = operation.result(timeout=90)
    
    return response.results

def example_v2_1(project_id, recognizer_id, audio_file):
    """google speech to text v2"""

    # Instantiates a client
    # client = SpeechClient()

    request = cloud_speech.CreateRecognizerRequest(
        parent=f"projects/{project_id}/locations/global",
        recognizer_id=recognizer_id,
        recognizer=cloud_speech.Recognizer(
            language_codes=[speech_client_v2], model="latest_long"
        ),
    )

    # Creates a Recognizer
    operation = speech_client_v2.create_recognizer(request=request)
    recognizer = operation.result()

    # Reads a file as bytes
    with io.open(audio_file, "rb") as f:
        content = f.read()

    config = cloud_speech.RecognitionConfig(auto_decoding_config={})

    request = cloud_speech.RecognizeRequest(
        recognizer=recognizer.name, config=config, content=content
    )

    # Transcribes the audio into text
    response = speech_client_v2.recognize(request=request)

    return response.results

def output_text(response_results, time_now):
    """note"""
    global count_row

    # write
    with open(output_text_filepath, 'a', encoding='utf-8') as txt_file:

        time_start = int(time_now)
        time_end = int(time_now)
        for result in response_results:
            tmp_time = result.result_end_time.seconds
            tmp_transcript = result.alternatives[0].transcript
            tmp_confidence = result.alternatives[0].confidence
            
            if time_end > time_start:
                time_start += tmp_time
            time_end += tmp_time

            # row index
            txt_file.write(count_row)
            
            # time
            tmp_time_range = get_time_range(time_start, time_end)
            txt_file.write(tmp_time_range)
            
            # confidence rate
            txt_file.write(f"[{tmp_confidence:.2%}]")
            txt_file.write("\n")

            for sentence in tmp_transcript.split("，"):
                txt_file.write(f"{sentence}\n")
            txt_file.write("\n")

            count_row += 1

    txt_file.close()
    print(f"[INFO] {time_now}...finished.")

# ----------------------------------------------------------------
if __name__ == "__main__":

    try:
        init()

        main()

    except Exception as err:
        print(f"[ERROR] {err}")