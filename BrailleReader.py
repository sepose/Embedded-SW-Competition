import pytesseract
import cv2
from picamera2 import Picamera2,Preview
from gtts import gTTS
import playsound
import os
import re
from jamo import h2j, j2hcj
from unicode import join_jamos
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests
import time
from bs4 import BeautifulSoup
import speech_recognition as sr
import pyaudio

# 이승찬,방유성,남혜원,정윤아
# 점자 번역 및 송출 스피커

braille_dict_Start = {
#여기서 부터는 초성입니다.
    "⠈" : "ㄱ", "⠉" : "ㄴ","⠊" : "ㄷ","⠐" : "ㄹ", "⠑" : "ㅁ","⠘" : "ㅂ",
    "⠠" : "ㅅ", "⠨" : "ㅈ", "⠰" : "ㅊ","⠋" : "ㅋ", "⠓" : "ㅌ", "⠙" : "ㅍ",
    "⠚" : "ㅎ"}

braille_double_dict_Start = {
    "⠈" : "ㄲ", "⠊" : "ㄸ", "⠘" : "ㅃ", "⠠" : "ㅆ", "⠨" : "ㅉ"
    }

braille_dict_Middle = {
#여기서 부터는 중성입니다.
    "⠣" : "ㅏ", "⠜" : "ㅑ", "⠎" : "ㅓ","⠱" : "ㅕ", "⠥" : "ㅗ", "⠬" : "ㅛ",
    "⠍" : "ㅜ", "⠩" : "ㅠ", "⠪" : "ㅡ","⠕" : "ㅣ", "⠗" : "ㅐ", "⠝" : "ㅔ",
    "⠌" : "ㅖ", "⠧" : "ㅘ", "⠽" : "ㅚ","⠏" : "ㅝ", "⠺" : "ㅢ"}

braille_dict_Middle_Plus = {'⠜' : "ㅒ",'⠧' : "ㅙ", '⠏' : "ㅞ", '⠍' : "ㅟ"}

braille_dict_End = {
#여기서 부터는 종성입니다.
    "⠁" : "ㄱ", "⠒" : "ㄴ", "⠔" : "ㄷ","⠂" : "ㄹ", "⠢" : "ㅁ", "⠃" : "ㅂ",
    "⠄" : "ㅅ", "⠶" : "ㅇ", "⠅" : "ㅈ", "⠆" : "ㅊ", "⠖" : "ㅋ", "⠦" : "ㅌ",
    "⠲" : "ㅍ", "⠴" : "ㅎ" }

braille_dict_Type_1 = {
    "⠹" : "억","⠾" : "언", "⠞" : "얼", "⠡" : "연",
    "⠳" : "열", "⠻" : "영", "⠭" : "옥","⠷" : "온", "⠿" : "옹", "⠛" : "운", 
    "⠯" : "울", "⠵" : "은", "⠮" : "을","⠟" : "인", "⠸⠎" : "것"
    }

braille_dict = {
#여기서 부터는 초성입니다.
    "⠈" : "ㄱ", "⠉" : "ㄴ","⠊" : "ㄷ","⠐" : "ㄹ", "⠑" : "ㅁ","⠘" : "ㅂ",
    "⠠" : "ㅅ", "⠨" : "ㅈ", "⠰" : "ㅊ","⠋" : "ㅋ", "⠓" : "ㅌ", "⠙" : "ㅍ",
    "⠚" : "ㅎ",
#여기서 부터는 중성입니다.
    "⠣" : "ㅏ", "⠜" : "ㅑ", "⠎" : "ㅓ","⠱" : "ㅕ", "⠥" : "ㅗ", "⠬" : "ㅛ",
    "⠍" : "ㅜ", "⠩" : "ㅠ", "⠪" : "ㅡ","⠕" : "ㅣ", "⠗" : "ㅐ", "⠝" : "ㅔ",
    "⠌" : "ㅖ", "⠧" : "ㅘ", "⠽" : "ㅚ","⠏" : "ㅝ", "⠺" : "ㅢ",
#여기서 부터는 종성입니다.
    "⠁" : "ㄱ", "⠒" : "ㄴ", "⠔" : "ㄷ","⠂" : "ㄹ", "⠢" : "ㅁ", "⠃" : "ㅂ",
    "⠄" : "ㅅ", "⠶" : "ㅇ", "⠅" : "ㅈ", "⠆" : "ㅊ", "⠖" : "ㅋ", "⠦" : "ㅌ",
    "⠲" : "ㅍ", "⠴" : "ㅎ"}

#여기서 부터는 1종 약자입니다.
Type_1_dict = {
    # 단일 초성과 모양이 같다. 몇 개 빼고
    "⠫" : "ㄱㅏ", "⠉" : "ㄴㅏ", "⠊" : "ㄷㅏ", "⠑" : "ㅁㅏ", "⠘" : "ㅂㅏ", "⠇" : "ㅅㅏ",
    "⠨" : "ㅈㅏ", "⠋" : "ㅋㅏ", "⠓" : "ㅌㅏ", "⠙" : "ㅍㅏ", "⠚" : "ㅎㅏ",
    # 뒤에 모음이 붙어 나오면 사용 불가
    # 줄바꿈시 가능 => 인식 라이브러리 줄바꿈 인식 안하므로 상관x

    # 여기서부터는 중성 약어
    "⠣" : "ㅇㅏ", "⠜" : "ㅇㅑ", "⠎" : "ㅇㅓ","⠱" : "ㅇㅕ", "⠥" : "ㅇㅗ", "⠬" : "ㅇㅛ",
    "⠍" : "ㅇㅜ", "⠩" : "ㅇㅠ", "⠪" : "ㅇㅡ","⠕" : "ㅇㅣ", "⠗" : "ㅇㅐ", "⠝" : "ㅇㅔ",
    "⠌" : "ㅇㅖ", "⠧" : "ㅇㅘ", "⠽" : "ㅇㅚ","⠏" : "ㅇㅝ", "⠺" : "ㅇㅢ",

    "⠹" : "억","⠾" : "언", "⠞" : "얼", "⠡" : "연",
    "⠳" : "열", "⠻" : "영", "⠭" : "옥","⠷" : "온", "⠿" : "옹", "⠛" : "운",    
    "⠯" : "울", "⠵" : "은", "⠮" : "을","⠟" : "인", "⠸⠎" : "것"}

Type_1_Middle_Plus_dict = {'⠜' : "ㅇㅒ",'⠧' : "ㅇㅙ", '⠏' : "ㅇㅞ", '⠍' : "ㅇㅟ"}

Type_1_double_dict = {
    "⠫" : "ㄲㅏ", "⠊" : "ㄸㅏ","⠘" : "ㅃㅏ", "⠇" : "ㅆㅏ", "⠨" : "ㅉㅏ", "⠸⠎" : "껏"
    }

Type_Junc_1_dict = {
    "⠣" : "ㅏ", "⠜" : "ㅑ", "⠎" : "ㅓ","⠱" : "ㅕ", "⠥" : "ㅗ", "⠬" : "ㅛ",
    "⠍" : "ㅜ", "⠩" : "ㅠ", "⠪" : "ㅡ","⠕" : "ㅣ", "⠗" : "ㅐ", "⠝" : "ㅔ",
    "⠌" : "ㅖ", "⠧" : "ㅘ", "⠽" : "ㅚ","⠏" : "ㅝ", "⠺" : "ㅢ",
    "⠹" : "ㅓㄱ","⠾" : "ㅓㄴ", "⠞" : "ㅓㄹ", "⠡" : "ㅕㄴ",
    "⠳" : "ㅕㄹ", "⠻" : "ㅕㅇ", "⠭" : "ㅗㄱ","⠷" : "ㅗㄴ", "⠿" : "ㅗㅇ", "⠛" : "ㅜㄴ", 
    "⠯" : "ㅜㄹ", "⠵" : "ㅡㄴ", "⠮" : "ㅡㄹ","⠟" : "ㅣㄴ"
    }
    
Type_Junc_1_dict_End = {
    "⠹" : "ㅓㄱ","⠾" : "ㅓㄴ", "⠞" : "ㅓㄹ", "⠡" : "ㅕㄴ",
    "⠳" : "ㅕㄹ", "⠻" : "ㅕㅇ", "⠭" : "ㅗㄱ","⠷" : "ㅗㄴ", "⠿" : "ㅗㅇ", "⠛" : "ㅜㄴ", 
    "⠯" : "ㅜㄹ", "⠵" : "ㅡㄴ", "⠮" : "ㅡㄹ","⠟" : "ㅣㄴ"
    }

Type_Num_dict = {
    "⠁" : "1", "⠃" : "2", "⠉" : "3", "⠙" : "4", "⠑" : "5", "⠋" : "6",
    "⠛" : "7", "⠓" : "8", "⠊" : "9", "⠐" : ",", "⠚" : "0", "⠤" : "-", "-" : "-"
    }
""""⠠" : "연결표","""
Type_Num_Exc_dict = {
    "⠉" : "ㄴ", "⠊" : "ㄷ", "⠑" : "ㅁ", "⠋" : "ㅋ", "⠓" : "ㅌ", "⠙" : "ㅍ",
    "⠚" : "ㅎ", "⠛" : "운"
    }

Type_Giho_dict = {
    ".⠦" : "?.", "⠲" : ".", "⠖" : "!", "⠦" : "\"", "⠴" : "\"", "⠐" : ","
    }

Type_C_dict = {
    "⠎" : "그래서", "⠉" : "그러나", "⠒" : "그러면", "⠢" : "그러므로", "⠝" : "그런데",
    "⠥" : "그리고","⠱" : "그리하여"
    }
    
Type_C_list = [
    "⠎", "⠉", "⠒","⠢","⠝","⠥","⠱"
    ]

url = "https://angelina-reader.ru/"
r = sr.Recognizer()
CVCam =  Picamera2()
CVCam.start()

def conv(Str):
    
    Str = "⠀⠀⠀" + Str + "⠀⠀⠀"
    
    #기호 점자 번역
    
    Str = Str.replace("⠤","-")         
    Str = Str.replace("⠈⠔","~")
    Str = Str.replace("⠦⠆","[")
    Str = Str.replace("⠰⠴","]")
    Str = Str.replace("⠐⠂",":")
    Str = Str.replace("⠦⠄","(")
    Str = Str.replace("⠰⠦","『")
    Str = Str.replace("⠴⠆","』")
    Str = Str.replace("⠐⠦","「")
    Str = Str.replace("⠴⠂","」")
    
    # 받침 점자 대체
    Str = Str.replace("⠒⠴", "ㄶ")
    Str = Str.replace("⠁⠁","ㄲ")
    Str = Str.replace("⠁⠄","ㄳ")
    Str = Str.replace("⠒⠅","ㄵ")
    Str = Str.replace("⠂⠁","ㄺ")
    Str = Str.replace("⠂⠢","ㄻ")
    Str = Str.replace("⠂⠃","ㄼ")
    Str = Str.replace("⠂⠄","ㄽ")
    Str = Str.replace("⠂⠦","ㄾ")
    Str = Str.replace("⠂⠲","ㄿ")
    Str = Str.replace("⠂⠴","ㅀ")
    Str = Str.replace("⠃⠄","ㅄ") 

    countEqual = 0

    newstr = ""
    i = 0;
    j=0
    while i < len(Str):
        
        
        if Str[i] == '⠒':
            j=i
            while Str[j] == '⠒':
                j+=1
                countEqual += 1
                
                if countEqual>5:
                    i = j
            
            countEqual = 0
        
        # 숫자 점자 인식 및 번역
        if Str[i] == '⠼':          
           i = i + 1;
           while 1:
                # 숫자 후 뛰어쓰기 시 숫자번역 모드 해제
                if Str[i] == ' ' or Str[i] == '⠀':
                    i = i + 1
                    break
                
                # 숫자 점자를 번역하고 숫자 점자가 아닐 시 숫자번역 모드 해제
                else:
                    if Str[i] in Type_Num_dict: 
                        newstr += Type_Num_dict.get(Str[i],"")                    
                        i += 1            
                    else:
                        if Str[i] in braille_dict_Middle:
                            newstr += "ㅇ"
                        break 
 
        # 기호 예외 처리 시작
        
        # 'ㄹ'과 쉼표 구분   추후 기호 예외 처리와 연계
        if Str[i] == '⠐':
            if Str[i+1] in Type_Junc_1_dict:
                newstr += braille_dict_Start.get(Str[i],"")
                i = i + 1
                
            else:
                newstr += Type_Giho_dict.get(Str[i],"")
                i = i+1
        
        # '.'과 종성'ㅍ'를 구분
        if Str[i] == '⠲' and (Str[i+1] == " " or Str[i+1] == "⠀" 
                              or Str[i+1] == "\n" or Str[i-1] in Type_Num_dict):
            newstr += "."
            i += 1
            
                    
        # 기호 예외 처리 끝
        
        
        if Str[i] == '⠸' and Str[i+1] == "⠎":
            if Str[i-1] == '⠠':
                newstr += Type_1_double_dict.get(Str[i+1],"")
                i+=2
            else:
                i += 2
                newstr += "것"
                
        
        # '그래서' 등의 부사 번역
        if Str[i] == '⠁' and Str[i+1] in Type_C_dict:
            if Str[i+2] == ' ' or Str[i+2]== '⠀':
                i += 1
                newstr += Type_C_dict.get(Str[i],"")
                i += 1
        
        # 초성 쌍자음
        if Str[i] == '⠠' and (Str[i+1] in braille_double_dict_Start or Str[i+1] in Type_1_double_dict):
            if Str[i+2] in braille_dict_Middle:
                if Str[i+3] == '⠌':
                    newstr += braille_double_dict_Start.get(Str[i+1],"") + braille_dict_Middle.get(Str[i+2],"") + "ㅆ"
                    i += 4
                    
                else:
                    newstr += braille_double_dict_Start.get(Str[i+1],"") + braille_dict_Middle.get(Str[i+2],"")
                    i += 3
                    
                    
            elif Str[i + 2] in Type_Junc_1_dict:
                newstr += braille_double_dict_Start.get(Str[i+1],"")
                i+=2
                
            else:
                
                newstr += Type_1_double_dict.get(Str[i+1],"")
                i += 2
            continue    
                
        if Str[i] in Type_1_dict:               # 1종 약어 번역
        
        
            # 모음을 생략한 자음 초성 다음에 종성 'ㅆ'이 올 때
            if Str[i] in braille_dict_Start and Str[i+1] == '⠌':
                newstr += Type_1_dict.get(Str[i],"") + "ㅆ"
                i += 2
                continue
        
            # 모음 뒤에 '-'가 오지 않고 바로 붙는 'ㅖ' 혹은 받침 종성'ㅆ'의 구분 
            if Str[i] == '⠌' and Str[i-1] in braille_dict_Middle:
                newstr += "ㅆ"     
            
        
            # 모음 앞이 자음 초성이 아닐 때 'ㅇ' 추가
            elif not Str[i-1] in braille_dict_Start and Str[i] in braille_dict_Middle:
                
                # 'ㅒ', 'ㅙ', 'ㅞ', 'ㅟ' 번역    추후 1종 약어와 연계
                if Str[i-1] in ['⠜','⠧','⠏','⠍']:
                    if Str[i] =='⠗':
                        newstr = newstr [: -1]
                        newstr += braille_dict_Middle_Plus.get(Str[i-1],"")
                        i += 1
                        continue
                
                
                newstr += Type_1_dict.get(Str[i],"")
                i+=1
                continue
        
            # 자음 + 모음 or 약어 결합 
            elif not Str[i + 1] in braille_dict_Middle and not Str[i+1] in Type_Junc_1_dict :
                if not Str[i] in Type_Junc_1_dict:
                    newstr += Type_1_dict.get(Str[i],"")
                else: 
                    if Str[i-1] in braille_dict_Start:
                        newstr += Type_Junc_1_dict.get(Str[i],"")
                    else : newstr += Type_1_dict.get(Str[i],"")
            
            # 종성 후 모음이 올 때 모음에 ㅇ 붙여 약어화
            elif Str[i-1] in braille_dict_End and Str[i] in braille_dict_Middle :
                newstr += Type_1_dict.get(Str[i],"")
                
            # 종성 후 'ㄱㅏ','ㄴㅏ' 등의 약어가 올 때 'ㅏ'를 붙여 약어화
            elif Str[i-1] in braille_dict_End and not Str[i+1] in braille_dict_Middle :
                if not Str[i+1] in braille_dict_Type_1:
                    newstr += Type_1_dict.get(Str[i],"")
                else : newstr += braille_dict.get(Str[i],"")
            
            # 'ㅇ'이나 'ㅏ'를 붙이는 약어가 아닐 때 단 자모음으로 출력
            elif Str[i] in braille_dict:
                newstr += braille_dict.get(Str[i],"")
            
            # 특정 모음이 모음 뒤에 연속으로 올 때
            elif Str[i] in braille_dict_Middle and Str[i+1] == '⠤' and Str[i+2] == '⠌':
                newstr += braille_dict_Middle.get(Str[i],"")
                i += 2
                continue
            
            # 초성 뒤에 받침이 있는 '억'등의 약어가 올 때 결합
            elif Str[i] in braille_dict_Start and Str[i+1] in Type_Junc_1_dict:
                newstr += braille_dict_Start.get(Str[i],"") + Type_Junc_1_dict.get(Str[i+1],"")
                i+=2
                continue
            
            else:
                if Str[i-1] in braille_dict_Start and Str[i] in Type_Junc_1_dict:
                    newstr += Type_Junc_1_dict.get(Str[i],"")
                else:
                    newstr += Type_1_dict.get(Str[i],"")
                

        # 약어가 아닐 때 단일 문자 출력
        elif Str[i] in braille_dict:
            newstr += braille_dict.get(Str[i],"")
            
        # 의외의 예외 처리
        else:
            newstr += Str[i]
        i += 1

    
    newstr = join_jamos(newstr)

    newstr = newstr.replace('셩','성')
    newstr = newstr.replace('쎵','썽')
    newstr = newstr.replace('졍','정')
    newstr = newstr.replace('쪙','쩡')
    newstr = newstr.replace('쳥','청')

    return newstr

#def showimg(image):
    
    #cv2.imshow("test",image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    
def binary_img(image):
    
    ret, dst = cv2.threshold(image, 130, 255, cv2.THRESH_BINARY)
    return dst
    
def readimg(image):
    
    sentence = pytesseract.image_to_string(image,lang='kor')
    return sentence

def readbraille(path):
    
    tempimg = cv2.imread(path)
    binaryimg = binary_img(tempimg)
    cv2.imwrite(path,binaryimg)

    chrome_service = Service('/usr/lib/chromium-browser/chromedriver')
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(service=chrome_service,options=options)
    driver.get(url)
    driver.page_source
    driver.find_element(By.XPATH,value='/html/body/div[2]/div[1]/div/main/div[1]/div[5]/div[1]/label').click()
    driver.find_element(By.XPATH,value='/html/body/div[2]/div[1]/div/main/div[1]/div[6]/div[2]/label').click()
    driver.find_element(By.CSS_SELECTOR,value="input[type='file']").send_keys(path)
    time.sleep(0.5)
    html = BeautifulSoup(requests.get(driver.current_url).content,"html.parser")
    driver.quit()
    braille = html.find_all("tt")
    
    if not braille[1]:
        return '에러 발생'
    else:
        return re.sub('[/,t,<,>]','',str(braille[1]))

def say(msg):
    
    if msg == "":
        say("발견된 글자가 없습니다.")
    else:   
        msg = gTTS(msg,lang = 'ko')
        msg.save('msg.mp3')
        playsound.playsound('msg.mp3')
        os.remove('msg.mp3')
    
def captureimg():
    
    say("곧 문서 촬영을 시작합니다.")

    time.sleep(2)
    CVCam.capture_file(r"/home/well/Desktop/capstone/Embedded/braille.jpg")
    imgpath = r"/home/well/Desktop/capstone/Embedded/braille.jpg"
    img = cv2.imread(r"/home/well/Desktop/capstone/Embedded/braille.jpg")
    img = cv2.rotate(img,cv2.ROTATE_90_COUNTERCLOCKWISE)
    cv2.imwrite(imgpath,img)
    playsound.playsound('shutter.mp3')
    print("사진촬영 완료")
    say("사진 찍기에 성공하였습니다.")
    
    return 1 , img, imgpath

def waiting():
    
   say("알림음 이후 문서를 해석하려면 해석시작 이라고 말하세요.")

   while(1):
    
       with sr.Microphone() as source:
           
           playsound.playsound('recordstart.mp3')
           r.adjust_for_ambient_noise(source)
           audio = r.listen(source)
           
           try:
            
             startvoice = r.recognize_google(audio,language='ko-KR')
             print('당신이 한말 : {}'.format(startvoice))
          
           except:
             startvoice = "알수없음"
        
           if ("해석" in startvoice) or ("시작" in startvoice) :
               print("해석을 시작합니다")
               break
               
           elif startvoice != "알수없음":
               say("문서를 해석하려면 해석시작 이라고 말하세요.")
               
# 여기서부터 함수가 아닌 실제 작동하는 코드부분입니다.

while(1):
            
   waiting()
   success, Obtainedimg, Obtainedpath = captureimg()

   helpmessage = """ 알림음 이후에 분석 방법을 말해주세요.
                 점자를 분석 하시려면 점자 분석 이라고 말 하시고,
                 한글을 분석 하시려면 한글 분석 이라고 말 하세요."""

   if success == 1:
   
      say(helpmessage)
   
      while(1):
       
         print("분석방법 선택")
   
         with sr.Microphone() as source:
             
             r.adjust_for_ambient_noise(source)
             playsound.playsound('recordstart.mp3')
             audio = r.listen(source)
       
             try:
           
               choice = r.recognize_google(audio,language='ko-KR')
               print('당신이 한말 : {}'.format(choice))
         
             except:
                 choice = "알수없음"
           
   
         if "한글" in choice:
       
             say("이미지속 글자를 분석합니다.")
             detected = readimg(Obtainedimg).rstrip()
             say(detected)
             break
       
         elif "점자" in choice:
       
             say("이미지속 점자를 분석합니다.")
             detectedB = readbraille(Obtainedpath)
             sentence = conv(detectedB).replace("\n", " ")
             say(sentence)
             break
       
         else:
             say("알림음 이후 다시 말해주세요.")
       
   say("메인 메뉴로 이동합니다.")




