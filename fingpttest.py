# Example: Using FinGPT to generate a financial report and advice

from fingpt import FinGPT  # Adjust the import according to the actual package structure

# Initialize the FinGPT model. This could involve loading pretrained weights, etc.
model = FinGPT(model_name="gpt-4-financial", device="cuda")  # or "cpu" if no GPU

# Define your financial data summary as context.
# For example, you might pass in some summary statistics computed from your transactions.
financial_context = """
Over the past month, your total income was $5,000 while your expenses were $4,200.
Your dominant expense categories were Rent, Groceries, and Utilities.
Your highest income source was your salary.
"""

# Define a prompt that asks for a report and advice.
prompt = f"""
Based on the following financial summary:
{financial_context}

Generate a report that includes:
1. A summary of income and expenses.
2. Identification of the dominant source of income and the largest expense categories.
3. Advice and recommendations on how to improve your financial health.
"""

# Generate the report using FinGPT
report = model.generate(prompt, max_tokens=500)  # Adjust max_tokens as needed

print("Generated Financial Report and Advice:")
print(report)
