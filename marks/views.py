import csv
import os
import json
import pandas as pd
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from .forms import InputMarkForm, UpdateMarkForm  # Import forms
from datetime import datetime

# Path to CSV file
CSV_FILE_PATH = os.path.join(settings.BASE_DIR, 'marks', 'data', 'students_data.csv')

# Helper function to check if the file exists
def check_csv_exists():
    return os.path.exists(CSV_FILE_PATH) and os.path.getsize(CSV_FILE_PATH) > 0

# Read CSV data
def read_csv():
    if not check_csv_exists():
        return []
    
    with open(CSV_FILE_PATH, mode='r') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

# Write data to CSV
def write_csv(data):
    fieldnames = ['student_id', 'student_name', 'gender', 'module_code', 'module_name',
                  'coursework1', 'coursework2', 'coursework3', 'total_marks', 'date_of_entry']

    normalized_data = [
        {field.strip(): value.strip() if isinstance(value, str) else value for field, value in record.items()}
        for record in data
    ]
    
    with open(CSV_FILE_PATH, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized_data)

# Home View
def home(request):
    num_students = 0
    modules = set()

    if check_csv_exists():
        with open(CSV_FILE_PATH, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                num_students += 1
                modules.add(row['module_code'])

    num_modules = len(modules)

    return render(request, "marks/home.html", {
        "num_students": num_students,
        "num_modules": num_modules,
    })

# Input Mark View
def input_mark(request):
    message = ""
    status = ""

    if request.method == 'POST':
        form = InputMarkForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            student_id = cleaned_data['student_id']
            module_code = cleaned_data['module_code']
            module_name = cleaned_data['module_name']
            coursework1 = cleaned_data['coursework1']
            coursework2 = cleaned_data['coursework2']
            coursework3 = cleaned_data['coursework3']
            gender = cleaned_data['gender']
            date_of_entry = cleaned_data['date_of_entry']

            total_marks = coursework1 + coursework2 + coursework3

            mark_data = {
                'student_id': student_id,
                'student_name': cleaned_data['student_name'],
                'gender': gender,
                'module_code': module_code,
                'module_name': module_name,
                'coursework1': coursework1,
                'coursework2': coursework2,
                'coursework3': coursework3,
                'total_marks': total_marks,
                'date_of_entry': date_of_entry
            }

            existing_data = read_csv()
            for row in existing_data:
                if row['student_id'] == student_id and row['module_code'] == module_code:
                    message = "Student ID already exists"
                    status = "error"
                    break
            else:
                with open(CSV_FILE_PATH, mode='a', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=mark_data.keys())
                    if os.path.getsize(CSV_FILE_PATH) == 0:
                        writer.writeheader()
                    writer.writerow(mark_data)

                message = "Input marks successful"
                status = "success"

        else:
            message = "Invalid form data"
            status = "error"
    else:
        form = InputMarkForm()

    return render(request, 'marks/input_mark.html', {
        'status': status,
        'message': message,
        'form': form
    })

# Update Mark View
def update_mark(request):
    message = ""
    status = ""

    if request.method == 'POST':
        form = UpdateMarkForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            student_id = cleaned_data['student_id'].strip()
            module_code = cleaned_data['module_code'].strip().lower()
            coursework1 = cleaned_data['coursework1']
            coursework2 = cleaned_data['coursework2']
            coursework3 = cleaned_data['coursework3']
            date_of_entry = cleaned_data['date_of_entry']
            date_of_entry_str = date_of_entry.strftime('%Y-%m-%d')  # Convert to string

            try:
                if not check_csv_exists():
                    message = "CSV file is missing or empty."
                    status = "error"
                else:
                    with open(CSV_FILE_PATH, mode='r') as file:
                        reader = csv.DictReader(file)
                        rows = list(reader)

                    updated = False
                    for row in rows:
                        if (
                            row['student_id'].strip() == student_id and
                            row['module_code'].strip().lower() == module_code and
                            row['date_of_entry'].strip() == date_of_entry_str
                        ):
                            row['coursework1'] = str(coursework1)
                            row['coursework2'] = str(coursework2)
                            row['coursework3'] = str(coursework3)
                            row['total_marks'] = str(coursework1 + coursework2 + coursework3)
                            updated = True
                            break

                    if updated:
                        with open(CSV_FILE_PATH, mode='w', newline='') as file:
                            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
                            writer.writeheader()
                            writer.writerows(rows)
                        message = "Marks updated successfully."
                        status = "success"
                    else:
                        message = "No matching record found for the given details."
                        status = "error"

            except FileNotFoundError:
                message = "CSV file not found."
                status = "error"

        else:
            message = "Invalid form data."
            status = "error"
    else:
        form = UpdateMarkForm()

    return render(request, "marks/update_mark.html", {
        "status": status,
        "message": message,
        "form": form,
    })

# View Mark View
def view_mark(request):
    module_code = request.GET.get('module_code')

    if not module_code:
        return render(request, 'marks/view_mark.html', {
            'status': 'error',
            'message': 'Module code is required'
        })

    marks_data = []

    try:
        with open(CSV_FILE_PATH, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if module_code.strip().lower() in row['module_code'].lower():
                    marks_data.append({
                        'student_id': row['student_id'],
                        'student_name': row['student_name'],
                        'coursework1': row['coursework1'],
                        'coursework2': row['coursework2'],
                        'coursework3': row['coursework3'],
                        'total_marks': row['total_marks']
                    })
    except FileNotFoundError:
        return render(request, 'marks/view_mark.html', {
            'status': 'error',
            'message': 'CSV file not found'
        })

    if not marks_data:
        return render(request, 'marks/view_mark.html', {
            'status': 'error',
            'message': f'No marks found for module code: {module_code}'
        })

    return render(request, 'marks/view_mark.html', {
        'marks': marks_data,
        'module_code': module_code
    })
import pandas as pd
import json
from django.shortcuts import render
from django.conf import settings
import os

def visualization(request):
    # Path to the student data CSV
    student_csv_path = os.path.join(settings.BASE_DIR, 'marks', 'data', 'students_data.csv')

    try:
        # Load CSV data and replace NaN with empty strings
        students_data = pd.read_csv(student_csv_path).fillna('')
    except FileNotFoundError:
        # Handle missing file gracefully
        students_data = pd.DataFrame()

    # If the CSV file is missing or empty, return empty data
    if students_data.empty:
        context = {
            'histogram_data': json.dumps({"labels": [], "coursework1_values": [], "coursework2_values": [], "coursework3_values": []}),
            'gender_chart_data': json.dumps({"labels": [], "values": []}),
            'module_chart_data': json.dumps({"labels": [], "values": []}),
            'registration_data': json.dumps({"labels": [], "module_data": []}),
        }
        return render(request, 'marks/visualization.html', context)

    # Average Marks Per Module for Coursework 1, 2, and 3
    histogram_data = {
        "labels": [],
        "coursework1_values": [],
        "coursework2_values": [],
        "coursework3_values": []
    }

    if all(col in students_data.columns for col in ['coursework1', 'coursework2', 'coursework3', 'module_code']):
        # Calculate average marks grouped by module_code
        module_marks = students_data.groupby('module_code')[['coursework1', 'coursework2', 'coursework3']].mean()
        histogram_data["labels"] = module_marks.index.tolist()
        histogram_data["coursework1_values"] = module_marks['coursework1'].round(2).tolist()
        histogram_data["coursework2_values"] = module_marks['coursework2'].round(2).tolist()
        histogram_data["coursework3_values"] = module_marks['coursework3'].round(2).tolist()

    # Gender Distribution
    gender_chart_data = {
        "labels": [],
        "values": []
    }

    if 'gender' in students_data.columns:
        # Normalize gender labels (capitalize "male", "female")
        students_data['gender'] = students_data['gender'].str.strip().str.capitalize()
        gender_distribution = students_data['gender'].value_counts()
        gender_chart_data["labels"] = gender_distribution.index.tolist()
        gender_chart_data["values"] = gender_distribution.tolist()

    # Module Registration Count
    module_chart_data = {
        "labels": [],
        "values": []
    }

    if all(col in students_data.columns for col in ['module_code', 'student_id']):
        module_registration_count = students_data.groupby('module_code')['student_id'].nunique()
        module_chart_data["labels"] = module_registration_count.index.tolist()
        module_chart_data["values"] = module_registration_count.tolist()

    # Monthly Registration Count (for stacked bar chart)
    registration_data = {
        "labels": [],  # This will store months
        "module_data": []  # This will store student counts per module by month
    }

    if 'date_of_entry' in students_data.columns:
        # Convert dates to datetime and drop invalid entries
        students_data['date_of_entry'] = pd.to_datetime(students_data['date_of_entry'], errors='coerce')
        valid_dates = students_data.dropna(subset=['date_of_entry'])

        if not valid_dates.empty and all(col in valid_dates.columns for col in ['student_id', 'module_name']):
            # Group by month and module_name, counting unique student_ids
            monthly_registration_count = valid_dates.groupby(
                [valid_dates['date_of_entry'].dt.to_period('M'), 'module_name']
            )['student_id'].nunique().reset_index()

            # Create labels and data for the stacked bar chart
            for period, group in monthly_registration_count.groupby('date_of_entry'):
                registration_data["labels"].append(str(period))  # Add month label
                module_counts = group.set_index('module_name')['student_id'].to_dict()  # Get counts by module
                registration_data["module_data"].append([module_counts.get(module, 0) for module in sorted(group['module_name'].unique())])
 # Prepare the Registration Data for the "Registrations Over Time" Line Chart
    registration_data = {
        "labels": [],  # This will store months
        "values": []   # This will store total student registrations per month
    }

    if 'date_of_entry' in students_data.columns:
        # Convert dates to datetime and drop invalid entries
        students_data['date_of_entry'] = pd.to_datetime(students_data['date_of_entry'], errors='coerce')
        valid_dates = students_data.dropna(subset=['date_of_entry'])

        if not valid_dates.empty:
            # Group by month, counting unique student_ids
            monthly_registration_count = valid_dates.groupby(valid_dates['date_of_entry'].dt.to_period('M'))['student_id'].nunique()

            # Prepare the data for the chart
            registration_data["labels"] = monthly_registration_count.index.astype(str).tolist()  # Convert period to string
            registration_data["values"] = monthly_registration_count.tolist()  # Count of registrations per month

    # Prepare context data for the template
    context = {
        'histogram_data': json.dumps(histogram_data),
        'gender_chart_data': json.dumps(gender_chart_data),
        'module_chart_data': json.dumps(module_chart_data),
        'registration_data': json.dumps(registration_data),
    }

    return render(request, 'marks/visualization.html', context)


# Get Stats View
def get_stats(request):
    try:
        students_data = read_csv()
        num_students = len(students_data)
        num_modules = len(set(student.get('module_code', '').strip() for student in students_data))

        return JsonResponse({'num_students': num_students, 'num_modules': num_modules})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
