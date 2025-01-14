import pandas as pd
import random
from faker import Faker

# Initialize Faker
fake = Faker()

# Medicine-related lists for fake data
medicine_names = [
    "Paracetamol", "Amoxicillin", "Ibuprofen", "Cetirizine", "Metformin", 
    "Ranitidine", "Ciprofloxacin", "Omeprazole", "Insulin", "Aspirin"
]
categories = ['Analgesic', 'Antibiotic', 'Antipyretic', 'Antidiabetic', 'Antacid', 'Antihistamine']
dosage_forms = ['Tablet', 'Capsule', 'Syrup', 'Injection', 'Ointment', 'Drops']
strengths = ['250mg', '500mg', '10mg/ml', '100mg', '1g', '5ml']
storage_temperatures = ['Room Temperature', '2–8°C', 'Below 25°C']
warehouses = ['Warehouse A', 'Warehouse B', 'Warehouse C']
suppliers = ['Supplier X', 'Supplier Y', 'Supplier Z', 'Supplier W']

# Generate dataset
enhanced_data = {
    'Medicine Name': [random.choice(medicine_names) for _ in range(200)],
    'Category': [random.choice(categories) for _ in range(200)],
    'Dosage Form': [random.choice(dosage_forms) for _ in range(200)],
    'Strength': [random.choice(strengths) for _ in range(200)],
    'Batch Number': [fake.bothify(text='BATCH-#######') for _ in range(200)],
    'Count': [random.randint(10, 500) for _ in range(200)],
    'Reorder Level': [random.randint(10, 50) for _ in range(200)],
    'Cost Price ($)': [round(random.uniform(2, 250), 2) for _ in range(200)],
    'Selling Price ($)': [round(random.uniform(10, 600), 2) for _ in range(200)],
    'Profit Margin (%)': [round(random.uniform(5, 50), 2) for _ in range(200)],
    'Discount (%)': [random.randint(0, 30) for _ in range(200)],
    'Expiry Date': [fake.date_between(start_date='today', end_date='+2y') for _ in range(200)],
    'Manufacture Date': [fake.date_between(start_date='-2y', end_date='today') for _ in range(200)],
    'Storage Temperature': [random.choice(storage_temperatures) for _ in range(200)],
    'Supplier Name': [random.choice(suppliers) for _ in range(200)],
    'Warehouse Location': [random.choice(warehouses) for _ in range(200)],
    'Regulatory Approval Number': [fake.bothify(text='FDA-########') for _ in range(200)],
    'Prescription Required': [random.choice([True, False]) for _ in range(200)],
    'Days to Expiry': [random.randint(0, 730) for _ in range(200)],
    'Units Sold': [random.randint(0, 100) for _ in range(200)],
    'Usage Instructions': [random.choice(['Take after meals', 'Take before meals', 'Use as directed']) for _ in range(200)],
    'Target Ailment': [random.choice(['Pain', 'Infection', 'Fever', 'Diabetes', 'Allergy', 'Acidity']) for _ in range(200)],
}

# Create DataFrame
enhanced_inventory_df = pd.DataFrame(enhanced_data)

# Save to CSV
enhanced_file_path = 'enhanced_medicine_inventory_dataset.csv'
enhanced_inventory_df.to_csv(enhanced_file_path, index=False)
enhanced_file_path
