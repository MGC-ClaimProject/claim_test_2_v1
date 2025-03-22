import json
from datetime import datetime
from insurances.models import Insurance
from members.models import Member
from django.db import transaction
from common.constants.choices import INSURANCE_COMPANY_CHOICES, get_status_code

def map_company_name(한글_이름):
    for category in INSURANCE_COMPANY_CHOICES:
        for eng, kor in category[1]:
            if kor == 한글_이름:
                return eng
    return None

def import_insurance_data(json_file_path, member_id):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            insurance_data = json.load(file)

        member = Member.objects.get(id=member_id)

        insurance_list = []
        for item in insurance_data:
            start_date, end_date = item["보험기간"].split(" ~ ")
            company_eng = map_company_name(item.get("보험사", ""))
            if not company_eng:
                continue  # 매핑 실패 시 스킵

            # ✅ 상태 매핑은 get_status_code로 변경
            status_code = get_status_code(item.get("계약상태", ""))

            insurance = Insurance(
                member=member,
                company=company_eng,
                policy_name=item.get("상품명", ""),
                policy_number=item.get("증권번호", ""),
                status=status_code,
                contract_relation=item.get("계약관계", ""),
                branch=item.get("담당점포", ""),
                phone_number=item.get("전화번호", "").replace(" ", "").replace("-", ""),
                start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
                end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
            )
            insurance_list.append(insurance)

        with transaction.atomic():
            Insurance.objects.bulk_create(insurance_list)

        return {"message": "Insurance data imported successfully", "status": "success"}

    except FileNotFoundError:
        return {"message": "File not found", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}
