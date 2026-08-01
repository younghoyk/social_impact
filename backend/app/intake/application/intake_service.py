from app.calls.application import CallServiceInterface
from app.cases.application import CaseServiceInterface
from app.cases.schemas import CaseCreate
from app.intake.agent import IntakeAgentInterface
from app.intake.schemas import IntakeResult


class IntakeService:
    def __init__(
        self,
        call_service: CallServiceInterface,
        agent: IntakeAgentInterface,
        case_service: CaseServiceInterface,
    ) -> None:
        self._call_service = call_service
        self._agent = agent
        self._case_service = case_service

    def process_call(self, call_id: int) -> IntakeResult:
        """통화 종료 후 호출 (Step 2): 분석 -> 매칭 -> 서류초안 -> Case 생성."""
        transcript = self._call_service.get_transcript(call_id)
        if not transcript:
            raise ValueError(f"Call {call_id} has no transcript yet")

        elder_id = self._call_service.get_elder_id(call_id)
        if elder_id is None:
            raise ValueError(f"Call {call_id} not found")

        result = self._agent.run(transcript)

        self._case_service.create_draft(
            CaseCreate(
                elder_id=elder_id,
                call_id=call_id,
                policy_title=result.matched_policy.title,
                draft_content=result.application_draft,
            )
        )
        return result
