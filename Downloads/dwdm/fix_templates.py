#!/usr/bin/env python3
"""Script to replace all plotly_dark templates with adaptive templates"""

# Read the file
with open('/Users/saaralvarunie/Downloads/dwdm/src/app.py', 'r') as f:
    content = f.read()

# Replace all occurrences
content = content.replace("template='plotly_dark'", "template=get_plotly_template()")

# Write back
with open('/Users/saaralvarunie/Downloads/dwdm/src/app.py', 'w') as f:
    f.write(content)

print("✅ Successfully replaced all plotly_dark templates with get_plotly_template()")
print("📊 The visualizations will now adapt to both light and dark modes!")
