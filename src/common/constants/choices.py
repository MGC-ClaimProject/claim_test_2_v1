from decimal import Decimal

STATUS_CHOICES = [
    ("Pending", "보류중"),
    ("In Progress", "진행중"),
    ("Completed", "완료"),
]

GENDER_CHOICES = [("Male", "남성"), ("Female", "여성")]


RELATION_CHOICES = [
    ("Self", "본인"),
    ("Parant", "부모"),
    ("Spouse", "배우자"),
    ("Child", "자녀"),
    ("Relative", "친척"),
    ("Grandparent", "조부모"),
    ("ETC", "기타"),
]

INSURANCE_TYPE_CHOICES = [
    ("LIFE", "종신보험"),
    ("INDEMNITY", "실손보험"),
    ("HEALTH", "건강종합보험"),
]

# 보험의 기존의 상태 옵션
POLICY_STATUS_CHOICES = [
    ("active", "유지(정상)"),
    ("terminated", "소멸(해약포함)"),
    ("dormant", "휴면"),
    ("matured", "만기"),
    ("lapsed", "실효"),
    ("cancelled", "해지"),
]

# ✅ 상태 매핑 딕셔너리 추가
# 내보험 찾아줌에서 검색해오는 상태의 명칭
STATUS_MAPPING = {
    "유지(정상)": "active",
    "소멸(해약포함)": "terminated",
    "휴면": "dormant",
    "만기": "matured",
    "실효": "lapsed",
    "해지": "cancelled"
}


# ✅ 상태 매핑 함수 추가
# 내보험 다보여에서 검색해오는 상태의 명칭을 기존 사용하던 명칭으로 변경해서 저장
def get_status_code(상태):
    return STATUS_MAPPING.get(상태, "pending")

CLAIM_STATUS_CHOICES = [
    ("draft", "작성중"),  # 사용자가 작성 중인 상태
    ("completed", "작성완료"),  # 작성 완료 상태
    ("sending", "발송중"),  # 발송 중 상태
    ("send_error", "발송에러"),  # 발송 에러 상태
    ("sent", "발송완료"),  # 발송 완료 상태
    ("claimed", "청구 완료"),  # 보험 청구가 완료된 상태
    ("cancelled", "청구 취소"),  # 보험 청구가 취소된 상태
    ("received", "수령 완료"),  # 보험금이 수령된 상태
]

# common/constants/choices.py

# ✅ 보험사 선택 옵션 (카테고리별)
INSURANCE_COMPANY_CHOICES = [
    (
        "생명보험",
        (
            ("Samsung Life", "삼성생명"),
            ("Kyobo Life", "교보생명"),
            ("Hanwha Life", "한화생명"),
            ("Shinhan Life", "신한라이프"),
            ("DB Life", "DB생명"),
            ("KDB Life", "KDB생명"),
            ("NH Life", "농협생명"),
            ("DGB Life", "DGB생명"),
            ("AIA Life", "AIA생명"),
            ("MetLife", "메트라이프생명"),
            ("Prudential Life", "푸르덴셜생명"),
            ("Heungkuk Life", "흥국생명"),
            ("Chubb Life", "처브라이프생명"),
            ("ABL Life", "ABL생명"),
            ("Tongyang Life", "동양생명"),
            ("Mirae Asset Life", "미래에셋생명"),
            ("IBK Pension", "IBK연금보험"),
        ),
    ),
    (
        "손해보험",
        (
            ("Samsung Fire & Marine", "삼성화재"),
            ("Hyundai Marine & Fire", "현대해상"),
            ("DB Insurance", "DB손해보험"),
            ("KB Insurance", "KB손해보험"),
            ("Meritz Fire & Marine", "메리츠화재"),
            ("Heungkuk Fire & Marine", "흥국화재"),
            ("MG Non-Life", "MG손해보험"),
            ("Hanwha General Insurance", "한화손해보험"),
            ("NH Non-Life", "농협손해보험"),
            ("AXA Direct", "악사손해보험"),
            ("Lotte Insurance", "롯데손해보험"),
            ("Carrot General Insurance", "캐롯손해보험"),
            ("AIG General Insurance", "AIG손해보험"),
            ("Chubb General Insurance", "처브손해보험"),
        ),
    ),
    (
        "기타보험",
        (
            ("Korean Federation of Community Credit", "신협공제"),
            ("National Credit Union Federation", "새마을금고공제"),
            ("Korea Teachers' Credit Union", "교직원공제회"),
            ("Post Insurance", "우체국보험"),
        ),
    ),
]


# ✅ 대한민국 은행 선택 옵션
BANK_CHOICES = [
    ("KB Kookmin Bank", "KB국민은행"),
    ("Shinhan Bank", "신한은행"),
    ("Woori Bank", "우리은행"),
    ("Hana Bank", "하나은행"),
    ("IBK Industrial Bank", "IBK기업은행"),
    ("NH Nonghyup Bank", "NH농협은행"),
    ("SC First Bank", "SC제일은행"),
    ("Citibank Korea", "씨티은행"),
    ("Daegu Bank", "대구은행"),
    ("Busan Bank", "부산은행"),
    ("Gwangju Bank", "광주은행"),
    ("Jeonbuk Bank", "전북은행"),
    ("Kyongnam Bank", "경남은행"),
    ("Kakao Bank", "카카오뱅크"),
    ("Toss Bank", "토스뱅크"),
]

# ✅ 보험사 매핑 딕셔너리
INSURANCE_COMPANY_MAPPING = {
    "삼성생명": "Samsung Life",
    "교보생명": "Kyobo Life",
    "한화생명": "Hanwha Life",
    "신한라이프": "Shinhan Life",
    "DB생명": "DB Life",
    "KDB생명": "KDB Life",
    "농협생명": "NH Life",
    "DGB생명": "DGB Life",
    "AIA생명": "AIA Life",
    "메트라이프생명": "MetLife",
    "푸르덴셜생명": "Prudential Life",
    "흥국생명": "Heungkuk Life",
    "처브라이프생명": "Chubb Life",
    "ABL생명": "ABL Life",
    "동양생명": "Tongyang Life",
    "미래에셋생명": "Mirae Asset Life",
    "IBK연금보험": "IBK Pension",
    "삼성화재": "Samsung Fire & Marine",
    "현대해상": "Hyundai Marine & Fire",
    "DB손해보험": "DB Insurance",
    "KB손해보험": "KB Insurance",
    "메리츠화재": "Meritz Fire & Marine",
    "흥국화재": "Heungkuk Fire & Marine",
    "MG손해보험": "MG Non-Life",
    "한화손해보험": "Hanwha General Insurance",
    "농협손해보험": "NH Non-Life",
    "악사손해보험": "AXA Direct",
    "롯데손해보험": "Lotte Insurance",
    "캐롯손해보험": "Carrot General Insurance",
    "AIG손해보험": "AIG General Insurance",
    "처브손해보험": "Chubb General Insurance",
    "신협공제": "Korean Federation of Community Credit",
    "새마을금고공제": "National Credit Union Federation",
    "교직원공제회": "Korea Teachers' Credit Union",
    "우체국보험": "Post Insurance",
}

import re
from difflib import get_close_matches


def get_standardized_company_name(company_name):
    """보험사 이름을 표준화된 `INSURANCE_COMPANY_CHOICES` 값으로 변환"""

    if not company_name or company_name.strip() == "":
        return "Unknown Insurance"  # ✅ 기본값 설정 (Unknown Insurance)

    # 1️⃣ 특수문자 제거 및 공백 정리
    cleaned_company_name = re.sub(r"[^\w가-힣]", "", company_name).strip()

    # 2️⃣ 정확한 매칭 확인
    if cleaned_company_name in INSURANCE_COMPANY_MAPPING:
        return INSURANCE_COMPANY_MAPPING[cleaned_company_name]

    # 3️⃣ 유사한 이름 찾기 (Levenshtein 거리 기반)
    possible_matches = get_close_matches(cleaned_company_name, INSURANCE_COMPANY_MAPPING.keys(), n=1, cutoff=0.8)
    if possible_matches:
        print(f"🔍 [유사한 매칭 발견] {company_name} → {possible_matches[0]}")
        return INSURANCE_COMPANY_MAPPING[possible_matches[0]]

    # 4️⃣ 매칭 실패 시 원래 값 반환 및 경고 출력
    print(f"⚠️ [주의] 변환되지 않은 보험사 이름: {company_name}")
    return company_name  # 매칭 실패 시 원래 값 반환

# 📌 크롤러 status 필드의 값
CRAWLER_STATUS = {
    "pending": "요청중",  # 요청이 생성됨
    "in_progress": "진행중",  # 크롤러 실행 중
    "waiting_for_verification": "인증 대기",  # 사용자의 휴대폰 인증을 기다리는 중
    "auth_pass": "인증 성공",  # 인증에 성공함
    "saving_data": "최종 데이터 저장중",  # 크롤링이 완료되어 데이터를 저장하는 중
    "completed": "성공",  # 크롤러 완료 및 데이터 저장 완료
    "failed": "실패"  # 크롤러 실행 실패
}