from examples.multi_agent.pipeline import run_sunglasses_campaign_pipeline


if __name__ == "__main__":
    results = run_sunglasses_campaign_pipeline()
    print(f"\nReport written to: {results['markdown_path']}")
