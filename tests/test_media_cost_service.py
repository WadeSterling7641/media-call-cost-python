from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.media_cost_service import MediaAsset, MediaCostService


@dataclass
class FakeHeaders:
    values: dict[str, str]

    def get(self, key: str, default: str = "") -> str:
        return self.values.get(key, default)


@dataclass
class FakeMessage:
    content: str


@dataclass
class FakeChoice:
    message: FakeMessage


@dataclass
class FakeResponse:
    choices: list[FakeChoice]


class FakeRaw:
    headers = FakeHeaders({"x-infrai-cost-usd": "0.02"})

    def parse(self) -> FakeResponse:
        return FakeResponse([FakeChoice(FakeMessage("A concise creator summary."))])


class FakeCompletions:
    class _Raw:
        def create(self, **_: object) -> FakeRaw:
            return FakeRaw()

    with_raw_response = _Raw()


class FakeClient:
    class _Chat:
        completions = FakeCompletions()

    chat = _Chat()


def test_delivery_is_allowed_when_call_cost_is_within_budget() -> None:
    service = MediaCostService(client=FakeClient(), budget_usd=0.05)  # type: ignore[arg-type]
    receipt = service.process_for_creator(MediaAsset("a1", "Interview", "A transcript."))
    assert receipt.cost_usd == 0.02
    assert receipt.delivered is True
    assert receipt.summary == "A concise creator summary."
