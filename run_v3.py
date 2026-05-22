import os, time
from dotenv import load_dotenv
load_dotenv()
import src.evaluator as ev

os.makedirs("results", exist_ok=True)

print("=== V3 Real Dataset Evaluation ===")
df = ev.evaluate_model(
    "datasets/agrihallu_v3_real.json",
    model="llama-3.1-8b-instant"
)

ts  = time.strftime("%Y%m%d_%H%M%S")
out = f"results/eval_v3_baseline_{ts}.csv"
df.to_csv(out, index=False)
print(f"\nSaved: {out}")
ev.print_report(df, "llama-3.1-8b-instant")
