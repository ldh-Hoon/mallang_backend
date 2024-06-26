import glob
import os

def rename_wav_to_mp3(folder_path):
    # 폴더 내의 모든 WAV 파일 경로를 찾기
    wav_files = glob.glob(os.path.join(folder_path, '**', '*.wav'), recursive=True)
    
    for wav_file in wav_files:
        # MP3 파일 경로 생성 (같은 폴더, 같은 이름으로)
        mp3_file = os.path.splitext(wav_file)[0] + '.mp3'
        
        # 파일명 변경
        os.rename(wav_file, mp3_file)
        print(f"'{wav_file}' 파일이 '{mp3_file}'로 이름이 변경되었습니다.")

# 특정 폴더 경로
folder_path = "./books"

# 함수 호출
rename_wav_to_mp3(folder_path)
