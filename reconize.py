import pytesseract
from PIL import Image, ImageGrab
# import win32gui, win32api, win32con
import cv2
import numpy as np

def fetch_image():
    grab_image = ImageGrab.grabclipboard()
    return grab_image

def get_board(n):
    imgOriginal = fetch_image()
    img = cv2.cvtColor(np.array(imgOriginal), cv2.COLOR_RGB2BGR)
    # cv2.imshow('img', img)
    print("识别X所在位置：")
    extra = get_extra_hint(img,n)
    print("识别数字（OCR）：")
    row,col = get_number_hint(img,n)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return row,col,extra

def get_extra_hint(img,n):
    extra_hint_img = img[773:773+886,174:174+886]
    extra_hint_binary = get_board_binary(extra_hint_img)
    extra_hint = []
    size = 886//n
    for i in range(n):
        for j in range(n):
            area = extra_hint_binary[i*size+5:(i+1)*size-5,j*size+5:(j+1)*size-5]
            if np.sum(area) < (size-10)**2*255*0.98:
                extra_hint.append((i, j))
                # cv2.imshow('area', area)
    print(extra_hint)
    # cv2.imshow('extra_hint_binary', extra_hint_binary)
    return extra_hint

def get_number_hint(img,n):
    # print(img.shape)
    row_hints_img = img[609:609+166,174:174+886]
    col_hints_img = img[773:773+886, 10:10+166]
    size = 886//n
    # cv2.imshow('row_hints_img', row_hints_img)
    # cv2.imshow('col_hints_img', col_hints_img)
    #backgroundcolor: #2B3A71（43,58,113）
    row_hints_binary = get_number_binary(row_hints_img)
    col_hints_binary = get_number_binary(col_hints_img)
    # cv2.imshow('row_hints_binary', row_hints_binary)
    # cv2.imshow('col_hints_binary', col_hints_binary)
    #divide into n parts
    row_hints = []
    col_hints = []
    for i in range(n):
        print('\r{}%'.format(i*100//n), end='')
        row_hint_binary = row_hints_binary[:,i*size:(i+1)*size]
        col_hint_binary = col_hints_binary[i*size:(i+1)*size,:]
        
        row_hints.append(divide_with_contour(row_hint_binary, 1,n))
        col_hints.append(divide_with_contour(col_hint_binary, 0,n))
    print('\r', end='')
    print(row_hints)
    print(col_hints)
    return row_hints, col_hints

def divide_with_contour(img, sortkey, n):
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    current_hint = []
    # i = 0
    filtered_rect = []
    size = 886//n
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w < size * 0.15 or w > size *0.68 or \
            h < size * 0.15 or h > size *0.68 or \
            w*h < 0.043*size*size or x < 1 or y < 1:
            continue
        filtered_rect.append((x, y, w, h))
    filtered_rect.sort(key=lambda x: (x[sortkey],x[1-sortkey]))
    #print(filtered_rect)
    adhesive = -100
    merged_rect = []
    for x, y, w, h in filtered_rect:
        if (x if sortkey == 0 else y) - adhesive < 4 and len(merged_rect) > 0 and merged_rect[-1][2] < size * 0.388:
            # print('merge',x, y, w, h, merged_rect[-1])
            merged_rect[-1] = (
                min(merged_rect[-1][0], x), 
                min(merged_rect[-1][1], y), 
                max(merged_rect[-1][0]+merged_rect[-1][2], x+w)-min(merged_rect[-1][0], x), 
                max(merged_rect[-1][1]+merged_rect[-1][3], y+h)-min(merged_rect[-1][1], y)
            )
        else:
            merged_rect.append((x, y, w, h))
        adhesive = x + w if sortkey==0 else y

    for x, y, w, h in merged_rect:
        current_hint_binary = img[y-4:y+h+8, x-4:x+w+8]
        # cv2.imshow('current_hint_binary'+str(i), current_hint_binary)
        def recognize_and_check(current_hint_binary):
            current_hint_number = recognize_number(current_hint_binary).replace('\n', '').replace('g', '9')
            if current_hint_number == '' or current_hint_number.isdigit() == False or \
                    int(current_hint_number) > 15 or current_hint_number == '0':
                print('error2',x, y, w, h, current_hint_number)
                return -1
            else:
                return current_hint_number
        current_hint_number = recognize_and_check(current_hint_binary)
        if current_hint_number == -1:
            current_hint_binary = cv2.dilate(current_hint_binary, np.ones((2,2),np.uint8), iterations=1)
            current_hint_number = recognize_and_check(current_hint_binary)
            if current_hint_number == -1:
                print('error',x, y, w, h, current_hint_number)
                cv2.imshow('current_hint_binary', current_hint_binary)
                cv2.imshow('img', img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                print('dilate ',x, y, w, h, current_hint_number)

        current_hint.append(int(current_hint_number))
        adhesive = x + w if sortkey==0 else y
    return current_hint

def recognize_number(img):
    #img2 = Image.fromarray(img)
    text = pytesseract.image_to_string(img, lang='eng', config='--psm 7 -c tessedit_char_whitelist=0123456789g')
    return text

def get_board_binary(img):
    #198,229,255
    backgroundcolor = np.array([255,229,198])
    diff = np.array([40,40,40])
    binary = cv2.inRange(img, backgroundcolor - diff, backgroundcolor + diff)
    return binary

def get_number_binary(img):
    backgroundcolor = np.array([113,58,43])
    diff = np.array([40,40,40])
    binary = cv2.inRange(img, backgroundcolor - diff, backgroundcolor + diff)
    # binary = cv2.dilate(binary, np.ones((2,2),np.uint8), iterations=1)
    # cv2.imshow('binary', binary)
    return binary


if __name__ == '__main__':
    get_board(15)
    cv2.waitKey(0)
    cv2.destroyAllWindows()