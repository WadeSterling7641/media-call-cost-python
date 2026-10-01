"""Runnable entry point for one asset ingestion, processing, and delivery decision."""

from media_cost_service import MediaAsset, MediaCostService


def main() -> None:
    asset = MediaAsset(
        asset_id="clip-2026-09-09-01",
        title="Launch interview",
        transcript="The team explains how the new camera workflow helps creators publish faster.",
    )
    receipt = MediaCostService().process_for_creator(asset)
    print(f"asset={receipt.asset_id} cost_usd={receipt.cost_usd:.6f} delivered={receipt.delivered}")
    print(receipt.summary)


if __name__ == "__main__":
    main()
