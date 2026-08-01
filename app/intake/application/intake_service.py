from app.calls.application import CallServiceInterface
from app.cases.application import CaseServiceInterface
from app.cases.schemas import CaseCreate
from app.elders.application import ElderServiceInterface
from app.elders.domain import Elder
from app.intake.agent import IntakeAgentInterface
from app.intake.schemas import EligibilityFilter, IntakeResult


def _eligibility_from_elder(elder: Elder) -> EligibilityFilter:
    """어르신 프로필 -> 매칭 필터. 기초생활수급/국가유공자처럼 전용 bool 필드가 없는
    조건은 vulnerability_types 자유 문자열에서 키워드로 판단한다."""
    is_basic_livelihood_recipient = any("기초생활수급자" in v for v in elder.vulnerability_types)

    return EligibilityFilter(
        age=elder.age,
        region_code=elder.address_code,
        is_basic_livelihood_recipient=is_basic_livelihood_recipient,
        is_veteran=elder.veteran_status,
        long_term_care_grade=elder.long_term_care_grade,
        household_type=elder.household_type,
        income_percentile=elder.income_percentile,
        disability_status=elder.disability_status,
        vulnerability_types=elder.vulnerability_types,
        full_name=elder.full_name,
        birth_date=elder.birth_date,
        phone_number=elder.phone_number,
        address=elder.address or "",
    )


class IntakeService:
    def __init__(
        self,
        call_service: CallServiceInterface,
        elder_service: ElderServiceInterface,
        agent: IntakeAgentInterface,
        case_service: CaseServiceInterface,
    ) -> None:
        self._call_service = call_service
        self._elder_service = elder_service
        self._agent = agent
        self._case_service = case_service

    def process_call(self, call_id: int) -> IntakeResult:
        """통화 종료 후 호출 (Step 2): 분석 -> 자격필터+매칭 -> 서류초안 -> Case 생성."""
        transcript = self._call_service.get_transcript(call_id)
        if not transcript:
            raise ValueError(f"Call {call_id} has no transcript yet")

        elder_id = self._call_service.get_elder_id(call_id)
        if elder_id is None:
            raise ValueError(f"Call {call_id} not found")

        elder = self._elder_service.get(elder_id)
        if elder is None:
            raise ValueError(f"Elder {elder_id} not found")

        result = self._agent.run(transcript, _eligibility_from_elder(elder))

        self._case_service.create_draft(
            CaseCreate(
                elder_id=elder_id,
                call_id=call_id,
                policy_title=result.matched_policy.title,
                draft_content=result.application_draft,
            )
        )
        return result
