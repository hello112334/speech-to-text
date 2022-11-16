# Google Cloud

Cloud speech-to-text

## Execute command

python app.py {audio-file}
> 01_data/{audio-file}

## How to use

1. Download this folder
2. Download ffmpeg and ffprobe to the folder <https://sourceforge.net/projects/ffmpeg-windows-builds/>.
3. Singup a google cloud account <https://cloud.google.com/>
4. Create a project and activate *Cloud Speech-to-Text API*
5. Create a service key(json) on google cloud console and download it
6. Install Python and libraries if necessary
7. Execute app.py

## Price

- 0-60 Minutes: Free
- Over 60 Minutes

|  Time  |  USD  |  JPY  |
| ---- | ---- | ---- |
|  1 min  |  0.024  |    3.6  |
|  1 hour |  1.440  |  216.0  |
|  4 hour |  5.760  |  864.0  |

READ MORE: <https://cloud.google.com/speech-to-text/pricing>.

## Quotas

- Audio lengh
  - Synchronous Requests:  ~1 Minute
  - Asynchronous Requests: ~480 Minutes*
  - Streaming Requests: ~5 Minutes**

> *Audio longer than ~1 minute must use the uri field to reference an audio file in Google Cloud Storage.
> **If you need to stream content for more than 5 minutes, see the endless streaming tutorial.

- Audio size
There is a limit of 10 MB on all single requests sent to the API using local files.

READ MORE: <https://cloud.google.com/speech-to-text/quotas>.

## Support Languages

READ MORE: <https://cloud.google.com/speech-to-text/docs/languages>.
