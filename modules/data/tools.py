from modules.data.student import student
import json
# Error 
default_error = "Something unexpected has occured, please try again."

# the agent will use this function to onboard a new student 
def add_new_student(first_name : str, last_name : str, email : str ) -> str:
    try:
        # instantiate student module
        _student = student()
        if _student.add_student(first_name, last_name, email):
            return "Student has been added successfully"
        return "Error! Student was not onboarded. Please try again"
    except Exception as e:
        _student.log_error(e)
        return default_error

# the agent will use this function to get a list of all onboarded students
def list_students() -> str:
    try:
        # instantiate student module
        _student = student()
        students = _student.fetch_all_students()
        
        if isinstance(students, list) and len(students) > 0:
            return json.dumps(students)
        
        return "Error! There are no students onboarded at the moment"
    except Exception as e:
        _student.log_error(e)
        return default_error

# the agent will use this function to delete a student 
def delete_student(email : str ) -> str:
    try:
        # instantiate student module
        _student = student()
        if _student.delete_student(email):
            return "Student deleted successfully"
        return "Error! Could not delete a student"
    except Exception as e:
        _student.log_error(e)
        return default_error
    
