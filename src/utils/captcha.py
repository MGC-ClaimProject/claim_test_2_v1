# src/utils/captcha.py

import os
import json
import time
import requests
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.crypto import get_random_string

# CAPTCHA 저장 경로 설정
CAPTCHA_IMAGE_PATH = os.path.join(settings.MEDIA_ROOT, "captcha")
CAPTCHA_TEXT_PATH = os.path.join(settings.MEDIA_ROOT, "auth_text.json")





# # ✅ 1️⃣ 보안문자(CAPTCHA) 이미지 저장
# def save_captcha_image(captcha_file, member_id):
#     """보안문자(CAPTCHA) 이미지를 'captcha_1.png' 형식으로 저장"""
#     try:
#         # ✅ 저장될 파일명 생성
#         filename = f"captcha_{member_id}.png"
#
#         # ✅ 올바른 코드: 상대 경로로 저장
#         path = default_storage.save(f"captcha/{filename}", ContentFile(captcha_file.read()))
#         return {"status": "success", "path": path}
#
#     except Exception as e:
#         return {"status": "error", "message": str(e)}


# # ✅ 2️⃣ 사용자가 입력한 보안문자 저장
# def save_captcha_text(captcha_text):
#     """사용자가 입력한 보안문자를 저장하는 함수"""
#     if len(captcha_text) == 6 and captcha_text.isdigit():
#         with open(CAPTCHA_TEXT_PATH, "w") as f:
#             json.dump({"captcha": captcha_text}, f)
#         return {"status": "success", "captcha": captcha_text}
#     return {"status": "error", "message": "Invalid captcha input"}
#
#
# # ✅ 3️⃣ 저장된 보안문자 가져오기
# def get_captcha_text():
#     """저장된 보안문자를 반환하는 함수"""
#     if os.path.exists(CAPTCHA_TEXT_PATH):
#         with open(CAPTCHA_TEXT_PATH, "r") as f:
#             return json.load(f)
#     return {"status": "pending"}


# ✅ 4️⃣ API: 크롤러가 보안문자 이미지 업로드
# @csrf_exempt
# def upload_captcha(request):
#     """크롤러가 캡처한 보안문자 이미지를 업로드하는 API"""
#     if request.method == "POST":
#         captcha_file = request.FILES.get("captcha")
#         member_id = request.POST.get("member_id")  # ✅ 멤버 ID 추가
#
#         if not captcha_file or not member_id:
#             return JsonResponse({"status": "error", "message": "Missing required parameters"}, status=400)
#
#         result = save_captcha_image(captcha_file, member_id)
#         return JsonResponse(result)
#
#     return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


# # ✅ 5️⃣ API: 사용자가 입력한 보안문자 저장
# @csrf_exempt
# def submit_captcha(request):
#     """사용자가 입력한 보안문자를 저장하는 API"""
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             captcha_text = data.get("captcha", "").strip()
#             result = save_captcha_text(captcha_text)
#             return JsonResponse(result)
#         except json.JSONDecodeError:
#             return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
#
#     return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


# # ✅ 6️⃣ API: 크롤러가 보안문자 가져오기
# def get_captcha(request):
#     """크롤러가 사용자의 보안문자 입력을 가져가는 API"""
#     return JsonResponse(get_captcha_text())
#

# # ✅ 7️⃣ 크롤러에서 보안문자 전송 함수
# def send_captcha_to_backend(file_path):
#     """크롤러가 캡처한 보안문자 이미지를 백엔드로 전송"""
#     files = {'captcha': open(file_path, 'rb')}
#     response = requests.post("http://localhost:8000/api/captcha/upload/", files=files)
#
#     if response.status_code == 200:
#         print("✅ 보안문자 이미지 전송 완료!")
#     else:
#         print(f"⚠️ 보안문자 전송 실패! 상태 코드: {response.status_code}")


# # ✅ 8️⃣ 크롤러에서 보안문자 가져오기
# def get_captcha_from_backend():
#     """백엔드에서 사용자가 입력한 보안문자를 가져옴"""
#     print("⏳ 백엔드에서 사용자의 입력을 기다리는 중...")
#     while True:
#         response = requests.get("http://localhost:8000/api/captcha/get/")
#
#         if response.status_code == 200:
#             data = response.json()
#             if "captcha" in data and len(data["captcha"]) == 6:
#                 print(f"✅ 사용자가 입력한 보안문자 수신: {data['captcha']}")
#                 return data["captcha"]
#
#         print("⌛ 입력 대기 중... (5초 후 재시도)")
#         time.sleep(5)
