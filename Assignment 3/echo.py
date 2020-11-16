import io
from google.cloud import speech,texttospeech,translate_v2
import sounddevice as sd
import numpy as np


NUM_CHANNELS = 1
FS = 22100
GC_CREDENTIALS = './credentials.json'


def record2file(filename, seconds=5):
    from scipy.io.wavfile import write

    myrecording = sd.rec(int(seconds * FS), samplerate=FS, channels=1, dtype=np.int16)
    print("Started recording, speak for 5 seconds")

    sd.wait()  # Wait until recording is finished
    write(filename, FS, myrecording)  # Save as WAV file

    print("Recording Finished")


def speech2text(filename, language):
    client = speech.SpeechClient.from_service_account_json(GC_CREDENTIALS)
    with io.open(filename, "rb") as f:
        audio = speech.RecognitionAudio(content=f.read())
    config = speech.RecognitionConfig(sample_rate_hertz=FS, language_code=language, audio_channel_count=1)
    response = client.recognize(config=config, audio=audio)

    results = [x.alternatives[0].transcript for x in response.results]
    return results[0]


def text2speech(text, language, output_file):
    client = texttospeech.TextToSpeechClient.from_service_account_json(GC_CREDENTIALS)
    input_ = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code=language)

    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                                            effects_profile_id=['headphone-class-device'])

    response = client.synthesize_speech(input=input_, voice=voice,audio_config=audio_config)
    with open(output_file, "wb") as f:
        f.write(response.audio_content)

    print("Speech written to the output file '{}'".format(output_file))

    return response.audio_content


if __name__ == '__main__':


    record_file = 'tmp_record.wav'
    output_file = 'output.wav'

    # record to the file
    record2file(record_file)

    # Arabic speech to text
    arabic_text = speech2text(record_file, 'ar-AE')
    print("Arabic Transcript :: ", arabic_text, sep='\n')
    print('')

    translation_client = translate_v2.Client.from_service_account_json(GC_CREDENTIALS)

    # Translate Arabic to English
    ar_en_translation = translation_client.translate(arabic_text,source_language='ar',target_language='en')["translatedText"]
    print("Arabic to English Translation :: ", ar_en_translation , sep = '\n')
    print('')

    # Translate English back to arabic
    en_ar_translation = translation_client.translate(ar_en_translation,source_language="en",target_language="ar")["translatedText"]
    print("English Translation to Arabic Back Translation :: ", en_ar_translation , sep = '\n')
    print('')


    # Arabic text to speech
    res_voice = text2speech(en_ar_translation, 'ar', output_file)





