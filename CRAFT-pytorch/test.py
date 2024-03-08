"""  
Copyright (c) 2019-present NAVER Corp.
MIT License
"""

# -*- coding: utf-8 -*-
import sys
import os
import time
import argparse

import torch
import torch.backends.cudnn as cudnn
from torch.autograd import Variable


import cv2
from skimage import io
import numpy as np
import craft_utils
import imgproc
import file_utils


from craft import CRAFT

from collections import OrderedDict
def copyStateDict(state_dict):
    if list(state_dict.keys())[0].startswith("module"):
        start_idx = 1
    else:
        start_idx = 0
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = ".".join(k.split(".")[start_idx:])
        new_state_dict[name] = v
    return new_state_dict

def str2bool(v):
    return v.lower() in ("yes", "y", "true", "t", "1")

def test_net(net, image, text_threshold, link_threshold, low_text, cuda, poly, refine_net=None):
    t0 = time.time()

    # resize
    img_resized, target_ratio, size_heatmap = imgproc.resize_aspect_ratio(image, args.canvas_size, interpolation=cv2.INTER_LINEAR, mag_ratio=args.mag_ratio)
    ratio_h = ratio_w = 1 / target_ratio

    # preprocessing
    x = imgproc.normalizeMeanVariance(img_resized)
    x = torch.from_numpy(x).permute(2, 0, 1)    # [h, w, c] to [c, h, w]
    x = Variable(x.unsqueeze(0))                # [c, h, w] to [b, c, h, w]
    if cuda:
        x = x.cuda()

    # forward pass
    with torch.no_grad():
        y, feature = net(x)

    # make score and link map
    score_text = y[0,:,:,0].cpu().data.numpy()
    score_link = y[0,:,:,1].cpu().data.numpy()

    # refine link
    if refine_net is not None:
        with torch.no_grad():
            y_refiner = refine_net(y, feature)
        score_link = y_refiner[0,:,:,0].cpu().data.numpy()

    t0 = time.time() - t0
    t1 = time.time()

    # Post-processing
    boxes, polys = craft_utils.getDetBoxes(score_text, score_link, text_threshold, link_threshold, low_text, poly)

    # coordinate adjustment
    boxes = craft_utils.adjustResultCoordinates(boxes, ratio_w, ratio_h)
    polys = craft_utils.adjustResultCoordinates(polys, ratio_w, ratio_h)
    for k in range(len(polys)):
        if polys[k] is None: polys[k] = boxes[k]

    t1 = time.time() - t1

    # render results (optional)
    render_img = score_text.copy()
    render_img = np.hstack((render_img, score_link))
    ret_score_text = imgproc.cvt2HeatmapImg(render_img)

    if args.show_time : print("\ninfer/postproc time : {:.3f}/{:.3f}".format(t0, t1))

    return boxes, polys, ret_score_text

def expand_image(image, target_height):
    current_height, width, channels = image.shape
    if current_height >= target_height:
        return image
    
    # 공백을 추가할 만큼의 크기 계산
    padding_height = target_height - current_height
    
    # 공백을 추가하여 새로운 이미지 생성
    padding = np.ones((padding_height, width, channels), dtype=np.uint8) * 255  # 흰색 공백
    expanded_image = np.vstack((image, padding))
    return expanded_image


def Save_visualization_image(output_visualization_path):
    output_visualization_path = output_visualization_path
    args = parse_arguments()
    net = CRAFT()     
    # target_size = (1625, 120)
    # background_color = (238, 238, 238)
    # print('Loading weights from checkpoint (' + args.trained_model + ')')
    if args.cuda:
        net.load_state_dict(copyStateDict(torch.load(args.trained_model)))
    else:
        net.load_state_dict(copyStateDict(torch.load(args.trained_model, map_location='cpu')))

    if args.cuda:
        net = net.cuda()
        net = torch.nn.DataParallel(net)
        cudnn.benchmark = False

    net.eval()

    # LinkRefiner
    refine_net = None
    if args.refine:
        from refinenet import RefineNet
        refine_net = RefineNet()
        # print('Loading weights of refiner from checkpoint (' + args.refiner_model + ')')
        if args.cuda:
            refine_net.load_state_dict(copyStateDict(torch.load(args.refiner_model)))
            refine_net = refine_net.cuda()
            refine_net = torch.nn.DataParallel(refine_net)
        else:
            refine_net.load_state_dict(copyStateDict(torch.load(args.refiner_model, map_location='cpu')))

        refine_net.eval()
        args.poly = True

    t = time.time()

    # load data
    for k, image_path in enumerate(image_list):
        print("Test image {:d}/{:d}: {:s}".format(k+1, len(image_list), image_path), end='\r')
        image = imgproc.loadImage(image_path)

        bboxes, polys, score_text = test_net(net, image, args.text_threshold, args.link_threshold, args.low_text, args.cuda, args.poly, refine_net)

        # save score text
        filename, file_ext = os.path.splitext(os.path.basename(image_path))
        mask_file = output_visualization_path + "/res_" + filename + '_mask.jpg'
        cv2.imwrite(mask_file, score_text)

        file_utils.saveResult(image_path, image[:,:,::-1], polys, dirname=output_visualization_path)


        
    print("elapsed time : {}s".format(time.time() - t))
    
def loadGrayscaleImage(img_file):
    img = cv2.imread(img_file, cv2.IMREAD_GRAYSCALE)  # 이미지를 그레이스케일로 로드

    cv2.imshow("Grayscale Image", img)  # 흑백 이미지를 화면에 표시
    cv2.waitKey(0)  # 아무 키나 누를 때까지 대기
    cv2.destroyAllWindows()  #

def Save_segmentation_image(output_segmentation_path):
    output_segmentation_path = output_segmentation_path
    args = parse_arguments()
    net = CRAFT()     
    target_size = (1625, 120)
    background_color = (238, 238, 238)
    # print('Loading weights from checkpoint (' + args.trained_model + ')')
    if args.cuda:
        net.load_state_dict(copyStateDict(torch.load(args.trained_model)))
    else:
        net.load_state_dict(copyStateDict(torch.load(args.trained_model, map_location='cpu')))

    if args.cuda:
        net = net.cuda()
        net = torch.nn.DataParallel(net)
        cudnn.benchmark = False

    net.eval()

    # LinkRefiner
    refine_net = None
    if args.refine:
        from refinenet import RefineNet
        refine_net = RefineNet()
        # print('Loading weights of refiner from checkpoint (' + args.refiner_model + ')')
        if args.cuda:
            refine_net.load_state_dict(copyStateDict(torch.load(args.refiner_model)))
            refine_net = refine_net.cuda()
            refine_net = torch.nn.DataParallel(refine_net)
        else:
            refine_net.load_state_dict(copyStateDict(torch.load(args.refiner_model, map_location='cpu')))

        refine_net.eval()
        args.poly = True

    t = time.time()

    
    for k, image_path in enumerate(image_list):
        print("Test image {:d}/{:d}: {:s}".format(k+1, len(image_list), image_path), end='\r')
        image = imgproc.loadImage(image_path)
        

        bboxes, polys, score_text = test_net(net, image, args.text_threshold, args.link_threshold, args.low_text, args.cuda, args.poly, refine_net)
        
    
        sorted_bboxes = sorted(bboxes, key=lambda bbox: bbox[0][0])

        # sorted_bboxes = bboxes

        for bbox in sorted_bboxes:
            bbox[0][0] -= 0
            # bbox[0][1] = 5 
            bbox[1][0] += 0
            # bbox[1][1] = 5
            bbox[2][0] += 5
            # bbox[2][1] = 120
            bbox[3][0] -= 5              
            # bbox[3][1] = 120  
        

        merged_bboxes = []
        i = 0  # 반복문 인덱스 초기화

        while i < len(sorted_bboxes) - 1:
            current_bbox = sorted_bboxes[i]
            next_bbox = sorted_bboxes[i + 1]
            # print((next_bbox[0][0] - current_bbox[1][0]),(next_bbox[1][0] - current_bbox[0][0]))

            if (next_bbox[0][0] - current_bbox[1][0]) < -3 and (next_bbox[1][   0] - current_bbox[0][0]) <80:
                # Bounding box가 중첩되지 않으면 current_bbox를 결과에 추가
                print(f"current{current_bbox},\n next{next_bbox}")
                print((next_bbox[0][0] - current_bbox[1][0]) , (next_bbox[1][0] - current_bbox[0][0]))
                merged_bbox = [
                    [min(current_bbox[0][0], next_bbox[0][0]), min(current_bbox[0][1], next_bbox[0][1])],
                    [max(current_bbox[1][0], next_bbox[1][0]), max(current_bbox[1][1], next_bbox[1][1])],
                    [max(current_bbox[2][0], next_bbox[2][0]), max(current_bbox[2][1], next_bbox[2][1])],
                    [min(current_bbox[3][0], next_bbox[3][0]), min(current_bbox[3][1], next_bbox[3][1])]
                ]
                # print(merged_bbox)
                merged_bboxes.append(merged_bbox)
                i += 2  # 병합되면 다음 반복은 건너뛰기
            else:
                # 현재 bbox와 다음 bbox를 병합하지 않고 그대로 추가
                merged_bboxes.append(current_bbox)
                i += 1  # 다음 반복으로 이동

        # 남은 마지막 bounding box 추가
        if i == len(sorted_bboxes) - 1:
            merged_bboxes.append(sorted_bboxes[-1])

        # for k, bbox in enumerate(merged_bboxes):
        #     print(k, bbox)


        for bbox in merged_bboxes:
            if (bbox[1][0]-bbox[0][0])>63 :
                bbox[0][0] -= 1
                # bbox[0][1] = 0 
                bbox[1][0] += -1
                # bbox[1][1] = 0
                bbox[2][0] += -1
                # bbox[2][1] = 120
                bbox[3][0] -= 1              
                # bbox[3][1] = 120     
                
                
        # print(f"before merged_bboxes  : \n {merged_bboxes}")

                
        grouped_by_y = {}
        current_group_y = None

        for i, bbox in enumerate(merged_bboxes):
            y_value = round(bbox[3][1])  # 소수점 이하 값을 반올림하여 정수 형태로 변환
            if current_group_y is None or abs(y_value - current_group_y) > 35:
                current_group_y = y_value

            if current_group_y not in grouped_by_y:
                grouped_by_y[current_group_y] = []

            grouped_by_y[current_group_y].append({'index': i, 'box': bbox})

        # 인접한 그룹들을 병합하는 로직 추가
        merged_grouped_by_y = {}
        for y_group, group in sorted(grouped_by_y.items()):
            merged = False
            for merged_group_y, merged_group in merged_grouped_by_y.items():
                if abs(merged_group_y - y_group) <= 10:
                    merged_grouped_by_y[merged_group_y] += group
                    merged = True
                    break
            if not merged:
                merged_grouped_by_y[y_group] = group
                
                
        sorted_word_info = OrderedDict()

        # 각 그룹을 정렬하고 정렬된 결과를 삽입합니다.
        for y_group, group in merged_grouped_by_y.items():
            sorted_group = sorted(group, key=lambda x: x['box'][0][0])  
            sorted_word_info[y_group] = sorted_group

        # # 정렬된 결과 출력
        # for y_group, group in sorted_word_info.items():
        #     print(f"Y Group: {y_group}")
        #     for item in group:
        #         print(f"Index: {item['index']}, Box: {item['box']}")
        #     print()
            
            



        # 그룹 해제 후 박스들만 남기기
        boxes_only = []
        for y_group, group in sorted_word_info.items():
            for item in group:
                boxes_only.append(item['box'])

        # 박스들만 남긴 상태에서 정렬된 결과 출력
        # for box in boxes_only:
        #     print(f"Box: {box}")
            
        sorted_merged_bboxes = boxes_only
        
        # print(f"after merged_bboxes  : \n {merged_bboxes}")
        
        
        
            
        # sorted_bboxes = sorted(bboxes, key=lambda bbox: bbox[0][0])
            
        # 각 단어의 정보를 저장할 리스트 초기화
        word_info_list = []

        # 단어 정보 저장
        for i, box in enumerate(polys if args.poly else sorted_merged_bboxes):
            # 좌표 값을 정수로 변환
            box_flat = [int(val) for sublist in box for val in sublist]

            # 단어 이미지 자르기
            word_image = image[box_flat[1]:box_flat[5], box_flat[0]:box_flat[2]].copy()

            # 단어 정보 추가
            word_info_list.append({
                'index': i,
                'box': box_flat,
                'image': word_image
            })


        # print(f"word_info_list : \n {word_info_list}")
        # 각 단어의 x축 값 기준으로 정렬
        
        sorted_word_info = word_info_list
        
        # print(f"after_word_info_list : \n {sorted_word_info}")
        
        
        if args.fitsize:
            for i, word_info in enumerate(sorted_word_info):
                box = word_info['box']
                word_image = word_info['image']

                # 이미지의 가로세로 크기 확인
                image_height, image_width, _ = word_image.shape

                if image_width > 30 and image_height > 30:
                    # 결과 이미지 저장
                    result_filename = os.path.join(output_segmentation_path, f"word_{k}_{i}.jpg")
                    cv2.imwrite(result_filename, word_image)

                            
        else :
            # 정렬된 단어 이미지를 순차적으로 저장
            for i, word_info in enumerate(sorted_word_info):
                box = word_info['box']
                word_image = word_info['image']

                # 새로운 결과 이미지 생성
                result_image = np.ones((target_size[1], target_size[0], 3), dtype=np.uint8) * background_color

                # 삽입 위치 계산
                x_offset = (target_size[0] - word_image.shape[1]) // 2
                y_offset = (target_size[1] - word_image.shape[0]) // 2

                # 중앙에 이미지 삽입
                result_image[y_offset:y_offset+word_image.shape[0], x_offset:x_offset+word_image.shape[1]] = word_image

                # 결과 이미지 저장
                result_filename = os.path.join(output_segmentation_path, f"word_{k}_{i}.jpg")
                cv2.imwrite(result_filename, result_image)

                # 이미지 크기를 세로를 이미지의 높이로 변경
                box[5] = box[1] + target_size[1]
            
        
        
    print("elapsed time : {}s".format(time.time() - t))

    
def parse_arguments():

    parser = argparse.ArgumentParser(description='CRAFT Text Detection')
    script_directory = os.path.dirname(__file__)

    parser.add_argument('-f','--fitsize',default=False, action='store_true', help='fullsize or fitsize')
    parser.add_argument('--trained_model', default='model/craft_mlt_25k.pth', type=str, help='pretrained model')
    parser.add_argument('--text_threshold', default=0.7, type=float, help='text confidence threshold')
    parser.add_argument('--low_text', default=0.3, type=float, help='text low-bound score')## 높을수록 한글자씩 boxing    0.4 아래부터 글자영역 합쳐짐
    parser.add_argument('--link_threshold', default=0.9, type=float, help='link confidence threshold') ## 더 split 미세하게 자르기 
    parser.add_argument('--cuda', default=True, type=str2bool, help='Use cuda for inference')
    parser.add_argument('--canvas_size', default=1280, type=int, help='image size for inference')
    parser.add_argument('--mag_ratio', default=1.5, type=float, help='image magnification ratio')## 이미지 확대
    parser.add_argument('--poly', default=False, action='store_true', help='enable polygon type')
    parser.add_argument('--show_time', default=False, action='store_true', help='show processing time')
    parser.add_argument('--test_folder', default='input/', type=str, help='folder path to input images')
    parser.add_argument('--refine', default=False, action='store_true', help='enable link refiner')
    parser.add_argument('--refiner_model', default='weights/craft_refiner_CTW1500.pth', type=str, help='pretrained refiner model')

    return parser.parse_args()

    
    

if __name__ == '__main__':
    args = parse_arguments()
    
    image_list, _, _ = file_utils.get_files(args.test_folder)
    output_visualization_path = './output_visualization/'
    output_segmentation_path = './output_segmentation/'

    for folder in [output_visualization_path, output_segmentation_path]:
        os.makedirs(folder, exist_ok=True)

    # Save_visualization_image(output_visualization_path)
    Save_segmentation_image(output_segmentation_path)
    
    
    
    
    