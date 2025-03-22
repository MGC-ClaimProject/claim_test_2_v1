import json
import os
import uuid

import requests
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import status
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from datetime import datetime
from django.core.cache import cache

from common.constants.choices import get_status_code, get_standardized_company_name, INSURANCE_COMPANY_CHOICES
from insurances.models import Insurance, CrawlerTask
from members.models import Member
# from utils.captcha import get_captcha_text, submit_captcha


User = get_user_model()



# --------------------------------------
# 내보험 다보여 싸이트용 크롤러 뷰 - 복잡
# --------------------------------------
# 📌 크롤링 실행 요청 API (프론트 → 백엔드 → Flask) 응답은 모든 상황이 끝난후 받을수 있음
class CallCrawlerAPIView(APIView):
    """
    사용자가 보험 조회를 시작하면 크롤러를 호출하는 API
    """
    permission_classes = [AllowAny]

    def remove_captcha(self, member_id):
        """
        기존 보안문자 이미지 파일을 삭제하는 함수
        """
        try:
            captcha_filename = f"captcha/captcha_{member_id}.png"
            captcha_path = os.path.join(settings.MEDIA_ROOT, "captcha", captcha_filename)

            if os.path.exists(captcha_path):
                os.remove(captcha_path)
                print(f"🗑️ 기존 보안문자 삭제 완료: {captcha_path}")
            else:
                print(f"⚠️ 삭제할 보안문자가 없음: {captcha_path}")

        except Exception as e:
            print(f"⚠️ 보안문자 삭제 중 오류 발생: {str(e)}")

    # 1️⃣ 크롤링 시작
    def post(self, request, member_id, *args, **kwargs):
        """
        크롤러 호출 (보험 조회 시작)
        """
        if not member_id:
            return Response({"message": "member_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 기존 보안문자 삭제
        self.remove_captcha(member_id)

        # ✅ 크롤러 요청 데이터 준비
        url = f"{settings.ALL_CRAWLER_API_URL}"

        data = {
            "member_id": member_id,
            "desired_id": request.data.get("desired_id"),  # 희망 ID 추가
            "name": request.data.get("name"),
            "phone1": request.data.get("phone1"),
            "phone2": request.data.get("phone2"),
            "phone3": request.data.get("phone3"),
            "birth": request.data.get("birth"),
            "gender": request.data.get("gender"),
            "carrier": request.data.get("carrier"),
            "access_token": request.data.get("access_token"),
        }

        try:
            # ✅ 크롤러 실행
            response = requests.post(url, json=data, timeout=300)

            # ⚠️ 크롤링이 끝난 후 응답을 받을 수 있음
            return Response(response.json(), status=response.status_code)
        except requests.Timeout:
            return Response({"message": "크롤러 요청 시간이 초과되었습니다."}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.RequestException as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 2️⃣ 프론트에서 GET 요청이 들어오면 성공 여부를 응답함 - 200/400
    def get(self, request, member_id, *args, **kwargs):
        """
        프론트에 인증 결과를 제공하는 API.
        AUTH_TEXT 파일에서 해당 member_id의 데이터를 확인하여,
          - "captcha_result"가 200이면 HTTP 200 (성공)
          - "captcha_result"가 400이면 HTTP 400 (실패)
        결과가 준비되지 않았으면 최대 5분 동안 기다린 후, 결과가 나오면 응답합니다.
        """
        filename = "auth_text.json"
        relative_path = os.path.join("captcha", filename)
        full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        if not os.path.exists(full_path):
            return Response({"msg": "인증 데이터 파일이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        member_key = str(member_id)
        timeout = 5  # 5분
        import time
        start_time = time.time()

        while True:
            try:
                with open(full_path, "r", encoding="utf-8") as file:
                    auth_data = json.load(file)
                if member_key not in auth_data:
                    # 아직 데이터가 없다면 1초 후 재시도
                    if time.time() - start_time > timeout:
                        return Response({"msg": "인증 데이터 대기 시간 초과"}, status=status.HTTP_408_REQUEST_TIMEOUT)
                    time.sleep(1)
                    continue

                captcha_result = auth_data[member_key].get("captcha_result")
                if captcha_result == 200:
                    return Response({"status": "success", "captcha_result": captcha_result}, status=status.HTTP_200_OK)
                elif captcha_result == 400:
                    return Response({"status": "fail", "captcha_result": captcha_result},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    # 아직 결과가 준비되지 않은 경우
                    if time.time() - start_time > timeout:
                        return Response({"msg": "인증 결과 대기 시간 초과"}, status=status.HTTP_408_REQUEST_TIMEOUT)
                    time.sleep(1)
            except json.JSONDecodeError:
                return Response({"msg": "인증 데이터 파일이 손상되었습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"msg": f"서버 오류: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 3️⃣ 프론트에서 보안문자 텍스트를 저장 (patch 요청)
    def patch(self, request, member_id, *args, **kwargs):
        """
        프론트에서 보안문자, 문자 인증번호, 이메일 인증번호 입력을 받아
        {member_id: "1", captcha_text: "123123", sms_text: "321232", email_text: "444444"}
        형식으로 JSON 파일에 저장하는 API
        """
        captcha_text = request.data.get("captcha_text", "")
        sms_text = request.data.get("sms_text", "")
        email_text = request.data.get("email_text", "")

        # 세 값 모두 빈 문자열이면 오류 반환
        if not (captcha_text or sms_text or email_text):
            return Response({"message": "보안문자, 문자, 이메일 인증 값이 없습니다."},
                            status=status.HTTP_400_BAD_REQUEST)

        # 저장할 JSON 파일 경로 (예: MEDIA_ROOT/captcha/auth_text.json)
        filename = "auth_text.json"
        relative_path = os.path.join("captcha", filename)
        full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        # 기존 JSON 파일 읽기 (없으면 빈 딕셔너리 생성)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as file:
                try:
                    auth_data = json.load(file)
                except json.JSONDecodeError:
                    auth_data = {}
        else:
            auth_data = {}

        # member_id에 해당하는 데이터 업데이트
        auth_data[str(member_id)] = {
            "captcha_text": captcha_text,
            "sms_text": sms_text,
            "email_text": email_text
        }

        try:
            with open(full_path, "w", encoding="utf-8") as file:
                json.dump(auth_data, file, ensure_ascii=False, indent=4)
            print(f"✅ 보안문자 저장 완료: {auth_data[str(member_id)]} (member_id: {member_id})")
            return Response({"status": "success", "message": "보안문자 데이터가 저장되었습니다."},
                            status=status.HTTP_200_OK)
        except Exception as e:
            print(f"⚠️ 보안문자 저장 중 오류 발생: {str(e)}")
            return Response({"message": "서버 오류 발생"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class CaptchaCrawlerAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, member_id, *args, **kwargs):
        """
        크롤러에 보안문자를 제공하는 API
        """
        # ✅ 보안문자 JSON 파일 경로
        captcha_filename = "auth_text.json"
        captcha_relative_path = os.path.join("captcha", captcha_filename)  # MEDIA_ROOT 하위 경로
        captcha_full_path = os.path.join(settings.MEDIA_ROOT, captcha_relative_path)

        # ✅ JSON 파일이 존재하는지 확인
        if not os.path.exists(captcha_full_path):
            return Response({"msg": "보안문자 데이터 파일이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ JSON 파일 읽기
        try:
            with open(captcha_full_path, "r", encoding="utf-8") as file:
                captcha_data = json.load(file)

            # ✅ 요청된 member_id에 해당하는 보안문자 값 찾기
            captcha_text = captcha_data.get(str(member_id))

            if not captcha_text:
                return Response({"msg": "해당 member_id에 대한 보안문자가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            return Response({"status": "ready", "captcha_text": captcha_text}, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            return Response({"msg": "보안문자 데이터 파일이 손상되었습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"msg": f"서버 오류: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
def parse_date(date_str):
    """문자열 날짜를 변환하고, 변환 실패 시 None을 반환"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        print(f"⚠️ [날짜 변환 오류] '{date_str}' 변환 실패")
        return None  # 변환 실패 시 None 반환


# --------------------------------------
# 내보험 보여줌 싸이트용 크롤러 뷰 - 간단
# --------------------------------------
class SimpleCallCrawlerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, member_id, *args, **kwargs):
        """
        크롤러 호출 (보험 조회 시작)
        """
        if not member_id:
            return Response({"message": "member_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 크롤러 요청 데이터 준비
        url = f"{settings.SIMPLE_CRAWLER_API_URL}"
        # ✅ Task ID 생성
        task_id = str(uuid.uuid4())

        # ✅ CrawlerTask 저장 (pending 상태)
        crawler_task = CrawlerTask.objects.create(
            task_id=task_id,
            member_id=member_id,
            status="pending"
        )

        data = {
            "task_id": task_id,
            "member_id": member_id,
            "name": request.data.get("name"),
            "phone1": request.data.get("phone1"),
            "phone2": request.data.get("phone2"),
            "phone3": request.data.get("phone3"),
            "birth": request.data.get("birth"), # 6자리
            "id_back": request.data.get("id_back"), #7자리
            "carrier": request.data.get("carrier"),
            # "access_token": request.data.get("access_token"),
        }
        try:
            # ✅ 크롤러 실행 요청
            response = requests.post(url, json=data, timeout=5)  # 비동기 요청 (응답을 기다리지 않음)
            response_data = response.json()


            # ✅ task_id를 응답에 포함 (클라이언트가 상태 조회 가능)
            return Response(response_data, status=response.status_code)

        except requests.RequestException as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




#  크롤러 상태 조회
# 🔄 크롤러 상태 업데이트 API
class CrawlerStatusAPIView(APIView):
    permission_classes = [AllowAny]
    """
    크롤러 실행 상태 조회 및 업데이트 API
    """

    def get(self, request, task_id, *args, **kwargs):
        """
        크롤러 실행 상태 조회 API
        """
        try:
            task = CrawlerTask.objects.get(task_id=task_id)
            return Response({
                "task_id": str(task.task_id),
                "status": task.status,
                "result_data": task.result_data if task.status == "completed" else None
            }, status=status.HTTP_200_OK)
        except CrawlerTask.DoesNotExist:
            return Response({"message": "해당 task_id를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        """
        크롤러 상태 업데이트 API (PATCH)
        """
        return self.update_status(request)

    def post(self, request, *args, **kwargs):
        """
        크롤러 상태 업데이트 API (POST)
        """
        return self.update_status(request)

    def update_status(self, request):
        """
        상태 업데이트 로직 (POST & PATCH 공통 사용)
        """
        task_id = request.data.get("task_id")
        status_value = request.data.get("status")
        result_data = request.data.get("result_data", None)  # 크롤러가 결과 데이터를 보낼 수도 있음

        if not task_id or not status_value:
            return Response({"message": "task_id와 status가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            task = CrawlerTask.objects.get(task_id=task_id)
            task.status = status_value

            # ✅ 크롤러가 완료되면 result_data도 저장 (옵션)
            if status_value == "completed" and result_data:
                self.save_insurance_data(task.member_id, result_data)
                task.result_data = result_data  # 예: JSON 데이터 저장

            task.save()  # ✅ DB 업데이트
            cache.set(task_id, status_value, timeout=1800)  # ✅ 상태 저장 (30분 유지)
            return Response({
                "task_id": task_id,
                "status": task.status,
                "result_data": task.result_data if task.status == "completed" else None
            }, status=status.HTTP_200_OK)

        except CrawlerTask.DoesNotExist:
            return Response({"message": "해당 task_id를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    def save_insurance_data(self, member_id, result_data):
        from rest_framework.generics import get_object_or_404
        from django.db import transaction
        import json

        member = get_object_or_404(Member, id=member_id)

        # result_data가 dict 형태이고 "insurance_data" 키가 있다면 해당 값을 사용
        if isinstance(result_data, dict) and "insurance_data" in result_data:
            insurance_list = result_data["insurance_data"]
        elif isinstance(result_data, str):
            try:
                # 비표준 JSON (단일 인용부호 사용) 보정
                if result_data.startswith("{'") or result_data.startswith("['"):
                    result_data = result_data.replace("'", "\"")
                insurance_list = json.loads(result_data)["insurance_data"]
            except Exception as e:
                raise ValueError("result_data는 리스트 형식이어야 합니다. (디코딩 실패)") from e
        elif isinstance(result_data, list):
            insurance_list = result_data
        else:
            raise ValueError("result_data는 리스트 형식이어야 합니다.")

        # 보험 항목이 dict인지 확인 (문자열인 경우 디코딩 시도)
        processed_list = []
        for insurance in insurance_list:
            if isinstance(insurance, dict):
                processed_list.append(insurance)
            elif isinstance(insurance, str):
                try:
                    processed_insurance = json.loads(insurance.replace("'", "\""))
                    processed_list.append(processed_insurance)
                except Exception as e:
                    print(f"보험 항목 디코딩 실패: {e}")
                    continue
            else:
                continue
        insurance_list = processed_list

        # 신규 보험 항목의 policy_number 집합 생성
        new_policy_numbers = set()
        for insurance in insurance_list:
            policy_number = insurance.get("policy_number")
            if policy_number:
                new_policy_numbers.add(policy_number)

        with transaction.atomic():
            for insurance in insurance_list:
                policy_number = insurance.get("policy_number")
                if not policy_number:
                    continue

                relation = insurance.get("contract_relation")
                # 관계에 따른 holder, insured 할당
                if relation == "계약자/피보험자":
                    holder_value = member.name
                    insured_value = member.name
                elif relation == "보험계약자":
                    holder_value = member.name
                    insured_value = None
                elif relation == "피보험자":
                    holder_value = None
                    insured_value = member.name
                elif relation == "계약자/수익자":
                    holder_value = member.name
                    insured_value = None
                else:
                    holder_value = None
                    insured_value = None

                defaults = {
                    "company": insurance.get("company"),
                    "type": insurance.get("contract_type"),
                    "policy_name": insurance.get("policy_name"),
                    "premium": insurance.get("premium"),
                    "start_date": insurance.get("start_date"),
                    "end_date": insurance.get("end_date"),
                    "payment_term": insurance.get("payment_term"),
                    "is_renewable": insurance.get("is_renewable", False),
                    "status": insurance.get("status"),
                    "contract_relation": insurance.get("contract_relation"),
                    "branch": insurance.get("branch"),
                    "phone_number": insurance.get("phone_number"),
                    "holder": holder_value,
                    "insured": insured_value,
                }

                Insurance.objects.update_or_create(
                    member=member,
                    policy_number=policy_number,
                    defaults=defaults
                )

            # 기존 DB에 저장된 보험 중, result_data에 없는 policy_number 삭제
            deleted_count, _ = Insurance.objects.filter(member=member) \
                .exclude(policy_number__in=new_policy_numbers).delete()

        print(f"✅ 보험 데이터 업데이트 완료. 삭제된 데이터: {deleted_count}건")

# # 📌 JSON 데이터를 읽어 DB에 저장
# class SaveDataAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         json_filename = request.data.get("json_filename")
#         member_id = request.data.get("member_id")
#
#         if not json_filename or not member_id:
#             return Response({"message": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)
#
#         full_json_path = os.path.join(settings.MEDIA_ROOT, "insurances_list_simple", json_filename)
#
#         if not os.path.exists(full_json_path):
#             return Response({"message": "JSON file not found"}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             with open(full_json_path, "r", encoding="utf-8") as file:
#                 insurance_data = json.load(file)
#
#             # ✅ 멤버 조회
#             try:
#                 member = Member.objects.get(id=member_id)
#             except Member.DoesNotExist:
#                 return Response({"message": "Member not found"}, status=status.HTTP_400_BAD_REQUEST)
#
#             with transaction.atomic():
#                 for insurance in insurance_data:
#                     policy_number = insurance.get("policy_number", "").strip()
#
#                     # ✅ 보험 기간 변환 (문자열 → 날짜)
#                     def parse_date(date_str):
#                         try:
#                             return datetime.strptime(date_str, "%Y-%m-%d").date()
#                         except (ValueError, TypeError):
#                             print(f"⚠️ [날짜 변환 오류] '{date_str}' 변환 실패")
#                             return None  # 변환 실패 시 None 반환
#
#                     start_date = parse_date(insurance.get("start_date"))
#                     end_date = parse_date(insurance.get("end_date"))
#
#                     # ✅ 보험사 이름 변환
#                     original_company = insurance.get("company", "").strip()
#                     standardized_company = get_standardized_company_name(original_company)
#
#                     # ✅ 보험 상품명 확인 및 기본값 설정
#                     policy_name = insurance.get("policy_name", "").strip()
#                     if not policy_name:
#                         print(f"⚠️ [경고] policy_name이 비어 있음. policy_number: {policy_number}")
#                         policy_name = "Unknown Policy"  # 기본값 설정
#
#                     # ✅ Django Choices 필드에 존재하는 값인지 확인
#                     valid_companies = [item[0] for category in INSURANCE_COMPANY_CHOICES for item in category[1]]
#                     if standardized_company not in valid_companies:
#                         print(f"⚠️ [오류] 변환된 보험사 '{standardized_company}'가 유효한 값이 아닙니다.")
#                         standardized_company = "Unknown Insurance"  # 기본값 설정
#
#                     # ✅ 디버깅 로그 (DB 저장 전)
#                     print(f"""
#                     🔍 [디버깅] DB 저장 시도:
#                     - policy_number: {policy_number}
#                     - company: {standardized_company}
#                     - policy_name: {policy_name}
#                     - start_date: {start_date}
#                     - end_date: {end_date}
#                     """)
#
#                     try:
#                         obj, created = Insurance.objects.update_or_create(
#                             member=member,
#                             policy_number=policy_number,
#                             defaults={
#                                 "company": standardized_company,
#                                 "policy_name": policy_name,  # ✅ 기본값 보장
#                                 "status": insurance.get("status", "pending"),
#                                 "contract_relation": insurance.get("contract_relation", ""),
#                                 "start_date": start_date,
#                                 "end_date": end_date,
#                                 "branch": insurance.get("branch", ""),
#                                 "phone_number": insurance.get("phone_number", ""),
#                                 "updated_at": now(),
#                             }
#                         )
#
#                         # ✅ 데이터가 생성되었는지, 업데이트되었는지 확인
#                         if created:
#                             print(f"✅ [성공] 새 보험 데이터 추가: {policy_number}")
#                         else:
#                             print(f"✅ [성공] 기존 보험 데이터 업데이트: {policy_number}")
#
#                     except IntegrityError as e:
#                         print(f"❌ [오류] DB 저장 중 IntegrityError 발생: {str(e)}")
#
#             return Response({"message": "Insurance data successfully saved to DB"}, status=status.HTTP_200_OK)
#
#         except json.JSONDecodeError:
#             return Response({"message": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
#
#         except Exception as e:
#             print(f"❌ [오류] 저장 중 오류 발생: {str(e)}")
#             return Response({"message": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        try:
#             # ✅ 크롤러 실행 요청
#             response = requests.post(url, json=data, timeout=5)  # 비동기 요청 (응답을 기다리지 않음)
#             response_data = response.json()
#
#             # ✅ task_id를 응답에 포함 (클라이언트가 상태 조회 가능)
#             return Response(response_data, status=response.status_code)
#
#         except requests.RequestException as e:
#             return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




