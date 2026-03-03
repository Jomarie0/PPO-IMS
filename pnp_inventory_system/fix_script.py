# Read the current file
with open('assets/views.py', 'r') as f:
    content = f.read()

# Replace the problematic lines
fixed_content = content.replace(
    "        kwargs['user'] = self.request.user\n        return kwargs",
    "        kwargs['user'] = self.request.user\n        kwargs['is_update'] = True\n        return kwargs"
)

# Write back to file
with open('assets/views.py', 'w') as f:
    f.write(fixed_content)

print("Fixed the get_form_kwargs method")
