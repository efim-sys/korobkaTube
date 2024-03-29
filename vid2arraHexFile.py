import cv2

import time

import numpy as np

from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename

Tk().withdraw()

framesInFile = 10                         # Кол-во кадров в 1 файле ktube

def minmax(v):                            # Часть алгоритма дизеринга
    if v > 255:
        v = 255
    if v < 0:
        v = 0
    return v

def dithering_gray(inMat, samplingF):     # Алгоритм дизеригна из Википедии
    h = inMat.shape[0]
    w = inMat.shape[1]
    for y in range(0, h-1):
        for x in range(1, w-1):
            old_p = inMat[y, x]
            new_p = np.round(samplingF * old_p/255.0) * (255/samplingF)
            inMat[y, x] = new_p
            quant_error_p = old_p - new_p
            inMat[y, x+1] = minmax(inMat[y, x+1] + quant_error_p * 7 / 16.0)
            inMat[y+1, x-1] = minmax(inMat[y+1, x-1] + quant_error_p * 3 / 16.0)
            inMat[y+1, x] = minmax(inMat[y+1, x] + quant_error_p * 5 / 16.0)
            inMat[y+1, x+1] = minmax(inMat[y+1, x+1] + quant_error_p * 1 / 16.0)
    return inMat

print("Выберите видео: ")
vidname=askopenfilename()
print("Выберите выходную папку: ")
dirname=askdirectory()

cap = cv2.VideoCapture(vidname)

length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
length = length - length % framesInFile

print(length)

startTime = time.time()

for n in range(0, length, framesInFile):
    file=open(dirname+"/"+str(n//framesInFile)+".ktube",  "w+b")     # Создаем файл с возможность записи в битах
    for i in range(framesInFile):
      print("Processing: "+ str(n+i), str('{0:.1f}'.format((n+i) / length * 100)) + "%")
      cap.set(cv2.CAP_PROP_POS_FRAMES, n+i)                # Находим в видео нужный кадр
      ret, image = cap.read()
      image = cv2.resize(image, (128, 64))                 # Масштабируем кадр
      gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # Преобразовываем в оттенки серого
      dithering_image = dithering_gray(gray_image.copy(), 1)  # Применяем дизеринг
      width=dithering_image.shape[1]
      height=dithering_image.shape[0]
      out = []
      for x in range(height):
          for y in range(0, width, 8):
              a = ""
              for r in range(8):
                  a += str(dithering_image[x][y+r] // 255)
              out.append(int(a, 2))
      file.write(bytearray(out))
    file.close()

elapsedTime = time.time() - startTime

print("Done!")
print("total time:", elapsedTime, "seconds")
print("avg fps:", length / elapsedTime)