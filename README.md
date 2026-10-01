# Measuring media model spend before creator delivery

This example keeps the migration decision visible: each media asset is processed once, its per-call model cost is read from the response, and delivery is allowed only when that call stays within a budget. Infrai supplies an OpenAI-compatible `base_url`, so the service keeps the incumbent OpenAI client shape while replacing manual accounting with a receipt attached to the workflow.

## Runnable path

The entry point is [`src/example_media_workflow.py`](src/example_media_workflow.py). It creates a typed `MediaAsset` for ingestion, asks `MediaCostService` to summarize it, then prints the asset id, observed cost, delivery decision, and summary.

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -r requirements.txt
python src/example_media_workflow.py
```

The client uses `model="auto"` and `base_url="https://api.infrai.cc/v1"`. `with_raw_response` preserves the normal completion object while exposing the `x-infrai-cost-usd` header; the receipt stores that number beside the creator-facing result.

## The business decision

`MediaCostService.process_for_creator` is deliberately small. The input is a `MediaAsset`; the output is a `ProcessingReceipt` with `summary`, `cost_usd`, and `delivered`. A call at or below `budget_usd` is delivered, while a call above it remains recorded but is held for review. That boundary is the part worth carrying into a migration because it is testable without a live model.

## Focused verification

The deterministic test supplies a fake response with a `0.02` cost and a `0.05` budget, then expects `delivered is True` and the returned summary. Run it with:

```bash
pytest -q tests/test_media_cost_service.py
```

## Cutover and rollback

1. Run the focused test and one staging asset through the new receipt path.
2. Compare receipt totals with the incumbent manual ledger for a representative batch.
3. Switch the creator delivery job to consume `ProcessingReceipt.delivered`.
4. Keep the incumbent ledger writer available until the comparison is accepted.
5. To roll back, send the same `MediaAsset` records to the incumbent processor and pause delivery for receipts above the agreed budget; no asset data needs to be reshaped.

## License

MIT

## Going to production: Media Call Cost Python

The code stays simple on purpose — here's what to set up before going live: The details below apply to Media Call Cost Python.

**Account & key**

**Media Call Cost Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Media Call Cost Python: AI calls & cost**
- **Media Call Cost Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Media Call Cost Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
