import pandas as pd

rag = pd.read_csv('results/eval_rag_FULL_20260421_173405.csv')
temporal = rag[rag['category']=='TEMPORAL'].copy()

def extract_state(text):
    states = ['Iowa','Illinois','California','Oklahoma','Kansas',
              'Washington','Georgia','Florida','Mississippi','Wisconsin','Nebraska']
    for s in states:
        if s.lower() in str(text).lower():
            return s
    return 'Unknown'

temporal['q_state'] = temporal['question'].apply(extract_state)
temporal['ctx_state'] = temporal['context_retrieved'].apply(extract_state)
temporal['state_mismatch'] = temporal['q_state'] != temporal['ctx_state']

print('=== State Mismatch Analysis ===')
print(f'Total temporal: {len(temporal)}')
print(f'State mismatch cases: {temporal["state_mismatch"].sum()}')
print(f'Mismatch rate: {temporal["state_mismatch"].mean()*100:.1f}%')
print()
both = temporal[temporal['state_mismatch'] & temporal['hallucinated']]
print(f'Wrong state AND hallucinated: {len(both)}')
print(f'RAG temporal failure rate: {len(both)/len(temporal)*100:.1f}%')
temporal.to_csv('results/temporal_analysis.csv', index=False)
print('Saved: results/temporal_analysis.csv')
