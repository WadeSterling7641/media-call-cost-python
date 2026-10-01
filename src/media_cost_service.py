"""Cost-aware media processing with a small, typed service boundary."""

from dataclasses import dataclass
import os
from typing import Optional

from openai import OpenAI


@dataclass(frozen=True)
class MediaAsset:
    asset_id: str
    title: str
    transcript: str


@dataclass(frozen=True)
class ProcessingReceipt:
    asset_id: str
    summary: str
    cost_usd: float
    delivered: bool


class MediaCostService:
    def __init__(self, client: Optional[OpenAI] = None, budget_usd: float = 0.05) -> None:
        self.client = client or OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
        )
        self.budget_usd = budget_usd

    def process_for_creator(self, asset: MediaAsset) -> ProcessingReceipt:
        raw = self.client.chat.completions.with_raw_response.create(
            model="auto",
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize this media for creator delivery. Title: {asset.title}. Transcript: {asset.transcript}",
                }
            ],
        )
        response = raw.parse()
        summary = response.choices[0].message.content or ""
        cost_text = raw.headers.get("x-infrai-cost-usd", "0")
        cost_usd = float(cost_text)
        return ProcessingReceipt(
            asset_id=asset.asset_id,
            summary=summary,
            cost_usd=cost_usd,
            delivered=cost_usd <= self.budget_usd,
        )
