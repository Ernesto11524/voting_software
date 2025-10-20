import csv
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_software.settings')
django.setup()

from django.contrib.auth.models import User

csv_path = r'C:\Users\Ernest Mpiani\Downloads\names_and_staff_numbers.csv'

try:
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            staff_id = row['S-ID- NO'].strip()
            name = row['NAME OF STAFF'].strip()
            if not staff_id or not name:
                continue  # skip rows with missing data

            # Split name: first word is first name, rest is last name
            name_parts = name.split()
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

            # Create user if not exists
            if not User.objects.filter(username=staff_id).exists():
                user = User.objects.create_user(
                    username=staff_id,
                    first_name=first_name,
                    last_name=last_name,
                    password='defaultpassword123'
                )
                print(f'Created user: {staff_id} - {first_name} {last_name}')
            else:
                print(f'User already exists: {staff_id}')
except FileNotFoundError:
    print(f'File not found: {csv_path}')