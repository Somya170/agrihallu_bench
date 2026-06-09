with open('paper/agrihallubench_draft.md', 'r') as f:
    content = f.read()

# Section 4.3 ko References ke baad se nikaal ke Section 4 mein daalo
multimodel_text = content.split('## 4.3 Multi-Model Comparison')[1].split('## References')[0]
references_text = content.split('## References')[1]

# Remove displaced section
content = content.replace('## 4.3 Multi-Model Comparison' + multimodel_text, '')

# Fix references
content = content.replace('## References' + references_text, '')

# Section 4 ke end mein add karo — before Section 5
content = content.replace(
    '## 5. Error Analysis',
    '## 4.3 Multi-Model Comparison' + multimodel_text + '\n---\n\n## 5. Error Analysis'
)

# References wapas add karo
content = content.rstrip() + '\n\n## References' + references_text

with open('paper/agrihallubench_draft.md', 'w') as f:
    f.write(content)

words = len(content.split())
sections = [l.strip() for l in content.split('\n') if l.startswith('## ')]
print(f"Total words: {words}")
print("\n=== Final Structure ===")
for s in sections:
    print(s)
