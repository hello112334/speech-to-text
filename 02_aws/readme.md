# AWS Transcibe

## Execute command

python app.py {audio-file}

> 01_data/{audio-file}

## Price

|  Time  |  USD  |  JPY  |
| ---- | ---- | ---- |
|  1 min  |  0.024  |    3.6  |
|  1 hour |  1.440  |  216.0  |
|  4 hour |  5.760  |  864.0  |

## Quotas

The following quotas cannot be changed:
Description: Quota

01. Audio file length: 4:00:00 (four) hours (14,400 seconds)
02. Audio stream duration: 4:00:00 (four) hours (14,400 seconds)
03. Audio file size: 2 GB
04. Audio file size (call analytics): 500 MB
05. Size of a custom vocabulary: 50 KB
06. Length of a custom vocabulary phrase: 256 characters
07. Size of a custom vocabulary filter: 50 KB
08. Number of custom vocabulary filters: 100
09. Number of channels for channel identification: 2
10. Number of days job records are retained: 90
11. Minimum audio file duration: 500 milliseconds (ms)

## How to use

1. Download this folder
2. Download ffmpeg and ffprobe to the folder <https://sourceforge.net/projects/ffmpeg-windows-builds/>.
3. Singup a aws account
4. Create a IAM user with access key and secret access key
5. Setup credentials in .aws
6. python app.py audio-file.mp3
