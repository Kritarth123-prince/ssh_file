import os
import glob
import re
import numpy as np
import soundfile as sf
from lxml import etree

def extract_timestamps_from_xml(xml_file_path, log_file_handle):
    timestamps_list = []
    try:
        xml_tree = etree.parse(xml_file_path)
        for line in xml_tree.xpath('.//line[@timestamp]'):
            hours, minutes, seconds = map(float, line.get('timestamp').split(':'))
            total_milliseconds = int((hours * 3600 + minutes * 60 + seconds) * 1000)
            timestamps_list.append(total_milliseconds)
    except Exception as parse_error:
        log_file_handle.write(f"Error parsing XML file {xml_file_path}: {parse_error}\n")
    
    return timestamps_list

def segment_audio_file(audio_file_path, timestamps, output_directory, base_filename, log_file_handle):
    try:
        audio_data, sample_rate = sf.read(audio_file_path)
        start_sample_index = 0

        for index, end_time_ms in enumerate(timestamps):
            end_sample_index = int(end_time_ms * sample_rate / 1000)
            audio_chunk = audio_data[start_sample_index:end_sample_index]

            output_audio_file = os.path.join(output_directory, f"{base_filename}_{index + 1}.wav")
            sf.write(output_audio_file, audio_chunk, sample_rate)
            log_file_handle.write(f"Saved audio chunk: {output_audio_file} from {start_sample_index / sample_rate:.3f}s to {end_sample_index / sample_rate:.3f}s\n")
            
            # start_sample_index = end_sample_index + int(0.001 * sample_rate)    # For 1 millisecond
            start_sample_index = end_sample_index + int(0.010 * sample_rate)    # For 10 millisecond

    except FileNotFoundError as file_not_found_error:
        log_file_handle.write(f"File not found: {audio_file_path}. Error: {file_not_found_error}\n")
    except Exception as general_error:
        log_file_handle.write(f"Error while processing audio file {audio_file_path}: {general_error}\n")

def locate_corresponding_audio_file(xml_file_path, audio_directory, log_file_handle):
    """Attempt to locate the matching audio file for a given XML file within the specified audio directory."""
    base_filename = re.sub(r'_w2v|_01|\.xml$', '', os.path.basename(xml_file_path))
    log_file_handle.write(f"Looking for audio file matching: {base_filename}\n")
    
    for file_extension in ('wav', 'mp3'):
        possible_audio_file = os.path.join(audio_directory, f"{base_filename}.{file_extension}")
        if os.path.exists(possible_audio_file):
            log_file_handle.write(f"Found corresponding audio file: {possible_audio_file}\n")
            return possible_audio_file
    
    log_file_handle.write(f"No corresponding audio file found for {xml_file_path}\n")
    return None

def handle_file_processing(xml_directory, audio_directory, output_directory):
    """Iterate through each XML file and process its corresponding audio file for segmentation."""
    os.makedirs(output_directory, exist_ok=True)
    
    log_file_name = "processing_log_10's.txt"
    log_file_path = os.path.join(os.path.dirname(output_directory), log_file_name)
    with open(log_file_path, 'w') as log_file_handle:
        for xml_file_path in glob.glob(os.path.join(xml_directory, "**", "*.xml"), recursive=True):
            log_file_handle.write(f"Starting processing of: {xml_file_path}\n")
            
            audio_file_path = locate_corresponding_audio_file(xml_file_path, audio_directory, log_file_handle)
            if not audio_file_path:
                log_file_handle.write(f"No matching audio found for {xml_file_path}\n")
                continue
            
            timestamps = extract_timestamps_from_xml(xml_file_path, log_file_handle)
            if not timestamps:
                log_file_handle.write(f"No timestamps extracted from {xml_file_path}\n")
                continue
            
            # Modify the last timestamp to ensure the last audio segment captures the ending of the file
            timestamps[-1] += 1
            
            base_filename = re.sub(r'_w2v|_01$', '', os.path.splitext(os.path.basename(xml_file_path))[0])
            segment_audio_file(audio_file_path, timestamps, output_directory, base_filename, log_file_handle)

xml_directory = "DataAnnotation"
audio_directory = "Combined_Audios"
output_directory = "Chunked_Audio_10s"

if __name__ == "__main__":
    handle_file_processing(xml_directory, audio_directory, output_directory)
