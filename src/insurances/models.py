import uuid

from common.constants.choices import (
    INSURANCE_COMPANY_CHOICES,
    INSURANCE_TYPE_CHOICES,
    POLICY_STATUS_CHOICES,
    RELATION_CHOICES, CRAWLER_STATUS  # 계약관계에 사용
)
from django.db import models
from members.models import Member


class Insurance(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="insurances",
        verbose_name="관리자",
    )
    company = models.CharField(
        max_length=50,
        choices=[(item[0], item[1]) for category in INSURANCE_COMPANY_CHOICES for item in category[1]],
        blank=True,
        null=True,
        verbose_name="보험사",
    )
    type = models.CharField(
        max_length=20,
        choices=INSURANCE_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name="보험 종류",
    )
    holder = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="계약자"
    )
    insured = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="피보험자"
    )
    policy_name = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="보험 이름"
    )
    policy_number = models.CharField(
        max_length=50, unique=True, verbose_name="증권번호"
    )
    premium = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="보험료"
    )
    start_date = models.DateField(blank=True, null=True, verbose_name="보험 시작일")
    end_date = models.DateField(blank=True, null=True, verbose_name="보험 종료일")
    payment_term = models.IntegerField(blank=True, null=True, verbose_name="납입 기간")
    is_renewable = models.BooleanField(default=False, verbose_name="갱신 여부")
    status = models.CharField(
        max_length=20,
        choices=POLICY_STATUS_CHOICES,
        default="active",
        verbose_name="유지 상태",
    )
    contract_relation = models.CharField(
        max_length=50,
        choices=RELATION_CHOICES,
        blank=True,
        null=True,
        verbose_name="계약 관계",
    )
    branch = models.CharField(
        max_length=300, blank=True, null=True, verbose_name="담당점포"
    )
    phone_number = models.CharField(
        max_length=50, blank=True, null=True, default="TEMP12345", verbose_name="전화번호"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "보험 계약"
        verbose_name_plural = "보험 계약들"

    def __str__(self):
        return f"{self.policy_name or self.company} - {self.holder}"


class CrawlerTask(models.Model):
    task_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    member_id = models.IntegerField()
    status = models.CharField(max_length=30, choices=CRAWLER_STATUS, default="pending")  # "pending", "in_progress", "completed", "failed"
    result_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task_id} - {self.status}"