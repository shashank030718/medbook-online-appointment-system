from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from mysql.connector import Error
from database import get_db_connection
from datetime import datetime, date

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

app.secret_key = "medbook-secret-key"


@app.route("/")
def home():
    return "Welcome to MedBook!"


# -------------------------
# Patient Registration
# -------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if not name or not email or not password:
            return "All fields are required."

        if len(password) < 6:
            return "Password must contain at least 6 characters."

        hashed_password = generate_password_hash(password)

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            check_query = """
                SELECT user_id
                FROM users
                WHERE email = %s
            """

            cursor.execute(check_query, (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                return "Email already registered."

            insert_query = """
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """

            values = (
                name,
                email,
                hashed_password,
                "patient"
            )

            cursor.execute(insert_query, values)
            connection.commit()

            return redirect(url_for("login"))

        except Error as e:
            print("Database error:", e)
            return "Something went wrong. Please try again."

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template("register.html")


# -------------------------
# Patient Login
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            # ---------------------------------
            # Check Patient or Admin
            # ---------------------------------

            user_query = """
                SELECT user_id, name, email, password, role
                FROM users
                WHERE email = %s
            """

            cursor.execute(user_query, (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user["password"], password):

                session.clear()

                session["user_id"] = user["user_id"]
                session["name"] = user["name"]
                session["role"] = user["role"]

                if user["role"] == "admin":
                    return redirect(url_for("admin_dashboard"))

                elif user["role"] == "patient":
                    return redirect(url_for("patient_dashboard"))

            # ---------------------------------
            # Check Doctor
            # ---------------------------------

            doctor_query = """
                SELECT doctor_id, name, email, password
                FROM doctors
                WHERE email = %s
            """

            cursor.execute(doctor_query, (email,))
            doctor = cursor.fetchone()

            if doctor and check_password_hash(
                doctor["password"],
                password
            ):

                session.clear()

                session["doctor_id"] = doctor["doctor_id"]
                session["name"] = doctor["name"]
                session["role"] = "doctor"

                return redirect(url_for("doctor_dashboard"))

            return "Invalid email or password."

        except Error as e:
            print("Database error:", e)
            return "Something went wrong. Please try again."

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template("login.html")


# -------------------------
# Patient Dashboard
# -------------------------

@app.route("/patient/dashboard")
def patient_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "patient_dashboard.html",
        name=session["name"]
    )





@app.route("/admin/dashboard")
def admin_dashboard():

    # Check whether user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Check whether user is an admin
    if session.get("role") != "admin":
        return "Access Denied", 403

    return render_template(
        "admin_dashboard.html",
        name=session["name"]
    )



#----------------------admin doctor 

@app.route("/admin/doctors")
def admin_doctors():

    # Check login
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Check admin role
    if session.get("role") != "admin":
        return "Access Denied", 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM doctors"

        cursor.execute(query)

        doctors = cursor.fetchall()

        return render_template(
            "admin_doctors.html",
            doctors=doctors
        )

    except Error as e:
        print("Database error:", e)
        return "Something went wrong."

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()




#--------------------doctor add ---

@app.route("/admin/add-doctor", methods=["GET", "POST"])
def add_doctor():

    # Check login
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Check admin role
    if session.get("role") != "admin":
        return "Access Denied", 403

    if request.method == "POST":

        name = request.form["name"].strip()
        specialization = request.form["specialization"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        phone = request.form["phone"].strip()

        # Basic validation
        if not name or not specialization or not email or not password:
            return "All required fields must be filled."

        if len(password) < 6:
            return "Password must contain at least 6 characters."

        # Hash doctor password
        hashed_password = generate_password_hash(password)

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Check duplicate email
            check_query = """
                SELECT doctor_id
                FROM doctors
                WHERE email = %s
            """

            cursor.execute(check_query, (email,))
            existing_doctor = cursor.fetchone()

            if existing_doctor:
                return "Doctor email already exists."

            # Insert doctor
            insert_query = """
                INSERT INTO doctors
                (name, specialization, email, password, phone)
                VALUES (%s, %s, %s, %s, %s)
            """

            values = (
                name,
                specialization,
                email,
                hashed_password,
                phone
            )

            cursor.execute(insert_query, values)
            connection.commit()

            return redirect(url_for("admin_doctors"))

        except Error as e:
            print("Database error:", e)
            return "Something went wrong. Please try again."

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template("add_doctor.html")



#-----------------doctor edit
@app.route("/admin/edit-doctor/<int:doctor_id>", methods=["GET", "POST"])
def edit_doctor(doctor_id):

    # Check login
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Check admin role
    if session.get("role") != "admin":
        return "Access Denied", 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # POST → Update doctor
        if request.method == "POST":

            name = request.form["name"].strip()
            specialization = request.form["specialization"].strip()
            email = request.form["email"].strip()
            phone = request.form["phone"].strip()

            if not name or not specialization or not email:
                return "Name, specialization and email are required."

            update_query = """
                UPDATE doctors
                SET name = %s,
                    specialization = %s,
                    email = %s,
                    phone = %s
                WHERE doctor_id = %s
            """

            cursor.execute(
                update_query,
                (
                    name,
                    specialization,
                    email,
                    phone,
                    doctor_id
                )
            )

            connection.commit()

            return redirect(url_for("admin_doctors"))

        # GET → Get current doctor details
        query = """
            SELECT doctor_id, name, specialization, email, phone
            FROM doctors
            WHERE doctor_id = %s
        """

        cursor.execute(query, (doctor_id,))
        doctor = cursor.fetchone()

        if not doctor:
            return "Doctor not found.", 404

        return render_template(
            "edit_doctor.html",
            doctor=doctor
        )

    except Error as e:
        print("Database error:", e)
        return "Something went wrong. Please try again."

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()





@app.route("/admin/delete-doctor/<int:doctor_id>", methods=["POST"])
def delete_doctor(doctor_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "Access Denied", 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            DELETE FROM doctors
            WHERE doctor_id = %s
        """

        cursor.execute(query, (doctor_id,))
        connection.commit()

        return redirect(url_for("admin_doctors"))

    except Error as e:
        print("Database error:", e)
        return "Something went wrong."

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()




#doctor login -----------------------

@app.route("/doctor/dashboard")
def doctor_dashboard():

    # Check doctor login
    if "doctor_id" not in session:
        return redirect(url_for("login"))

    # Check role
    if session.get("role") != "doctor":
        return "Access Denied", 403

    return render_template(
        "doctor_dashboard.html",
        name=session["name"]
    )


#booking appointment 
@app.route("/patient/book-appointment", methods=["GET", "POST"])
def book_appointment():

    # Check whether the user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Only patients can book appointments
    if session.get("role") != "patient":
        return "Access Denied", 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------
        # POST: Book appointment
        # -------------------------
        if request.method == "POST":

            doctor_id = request.form["doctor_id"]
            appointment_date = request.form["appointment_date"]
            appointment_time = request.form["appointment_time"]
            reason = request.form["reason"].strip()

            # Basic validation
            if not doctor_id or not appointment_date or not appointment_time:
                return "Please fill in all required fields."

            # Insert appointment
            insert_query = """
                INSERT INTO appointments
                (
                    patient_id,
                    doctor_id,
                    appointment_date,
                    appointment_time,
                    reason,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            cursor.execute(
                insert_query,
                (
                    session["user_id"],
                    doctor_id,
                    appointment_date,
                    appointment_time,
                    reason,
                    "Pending"
                )
            )

            connection.commit()

            return redirect(url_for("patient_appointments"))

        # -------------------------
        # GET: Display doctors
        # -------------------------
        query = """
            SELECT doctor_id, name, specialization
            FROM doctors
        """

        cursor.execute(query)
        doctors = cursor.fetchall()

        return render_template(
            "book_appointment.html",
            doctors=doctors
        )

    except Error as e:
        print("Database error:", e)
        return "Something went wrong."

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()



@app.route("/patient/appointments")
def patient_appointments():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "patient":
        return "Access Denied", 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                a.appointment_id,
                d.name AS doctor_name,
                d.specialization,
                a.appointment_date,
                a.appointment_time,
                a.reason,
                a.status
            FROM appointments a
            JOIN doctors d
                ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s
            ORDER BY a.appointment_date DESC,
                     a.appointment_time DESC
        """

        cursor.execute(query, (session["user_id"],))

        appointments = cursor.fetchall()

        return render_template(
            "patient_appointments.html",
            appointments=appointments
        )

    except Error as e:
        print("Database error:", e)
        return "Something went wrong."

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


#doctor appointm,entr ------------


@app.route("/doctor/appointments")
def doctor_appointments():

    # Check doctor login
    if "doctor_id" not in session:
        return redirect(url_for("login"))

    # Check doctor role
    if session.get("role") != "doctor":
        return "Access Denied", 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                a.appointment_id,
                u.name AS patient_name,
                u.email AS patient_email,
                a.appointment_date,
                a.appointment_time,
                a.reason,
                a.status
            FROM appointments a
            JOIN users u
                ON a.patient_id = u.user_id
            WHERE a.doctor_id = %s
            ORDER BY a.appointment_date ASC,
                     a.appointment_time ASC
        """

        cursor.execute(
            query,
            (session["doctor_id"],)
        )

        appointments = cursor.fetchall()

        return render_template(
            "doctor_appointments.html",
            appointments=appointments
        )

    except Error as e:
        print("Database error:", e)
        return "Something went wrong."

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()





@app.route(
    "/doctor/update-appointment/<int:appointment_id>",
    methods=["POST"]
)
def update_appointment(appointment_id):

    # Check doctor login
    if "doctor_id" not in session:
        return redirect(url_for("login"))

    # Check role
    if session.get("role") != "doctor":
        return "Access Denied", 403

    status = request.form["status"]

    # Only allow valid status values
    valid_statuses = [
        "Pending",
        "Confirmed",
        "Completed",
        "Cancelled"
    ]

    if status not in valid_statuses:
        return "Invalid appointment status.", 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Important:
        # Update only appointments belonging to
        # the logged-in doctor
        query = """
            UPDATE appointments
            SET status = %s
            WHERE appointment_id = %s
            AND doctor_id = %s
        """

        cursor.execute(
            query,
            (
                status,
                appointment_id,
                session["doctor_id"]
            )
        )

        connection.commit()

        return redirect(
            url_for("doctor_appointments")
        )

    except Error as e:
        print("Database error:", e)
        return "Something went wrong."

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()



#admin visibility 


@app.route("/admin/appointments")
def admin_appointments():

    # Check login
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Only admin can access
    if session.get("role") != "admin":
        return "Access Denied", 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                a.appointment_id,

                u.name AS patient_name,

                d.name AS doctor_name,
                d.specialization,

                a.appointment_date,
                a.appointment_time,
                a.reason,
                a.status

            FROM appointments a

            JOIN users u
                ON a.patient_id = u.user_id

            JOIN doctors d
                ON a.doctor_id = d.doctor_id

            ORDER BY
                a.appointment_date DESC,
                a.appointment_time DESC
        """

        cursor.execute(query)

        appointments = cursor.fetchall()

        return render_template(
            "admin_appointments.html",
            appointments=appointments
        )

    except Error as e:
        print("Database error:", e)
        return "Something went wrong."

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()




@app.route(
    "/admin/update-appointment/<int:appointment_id>",
    methods=["POST"]
)
def admin_update_appointment(appointment_id):

    # Check login
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Only admin can access
    if session.get("role") != "admin":
        return "Access Denied", 403

    status = request.form["status"]

    valid_statuses = [
        "Pending",
        "Confirmed",
        "Completed",
        "Cancelled"
    ]

    if status not in valid_statuses:
        return "Invalid appointment status.", 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            UPDATE appointments
            SET status = %s
            WHERE appointment_id = %s
        """

        cursor.execute(
            query,
            (status, appointment_id)
        )

        connection.commit()

        return redirect(
            url_for("admin_appointments")
        )

    except Error as e:
        print("Database error:", e)
        return "Something went wrong."

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()



#report 


@app.route("/admin/reports")
def admin_reports():

    # Check login
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Only admin can access
    if session.get("role") != "admin":
        return "Access Denied", 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get total patients
        cursor.execute("""
            SELECT COUNT(*) AS total_patients
            FROM users
            WHERE role = 'patient'
        """)
        total_patients = cursor.fetchone()["total_patients"]

        # Get total doctors
        cursor.execute("""
            SELECT COUNT(*) AS total_doctors
            FROM doctors
        """)
        total_doctors = cursor.fetchone()["total_doctors"]

        # Get total appointments
        cursor.execute("""
            SELECT COUNT(*) AS total_appointments
            FROM appointments
        """)
        total_appointments = cursor.fetchone()["total_appointments"]

        # Get appointment counts by status
        cursor.execute("""
            SELECT status, COUNT(*) AS count
            FROM appointments
            GROUP BY status
        """)

        status_results = cursor.fetchall()

        # Default values
        appointment_stats = {
            "Pending": 0,
            "Confirmed": 0,
            "Completed": 0,
            "Cancelled": 0
        }

        # Fill actual values
        for row in status_results:
            if row["status"] in appointment_stats:
                appointment_stats[row["status"]] = row["count"]

        return render_template(
            "admin_reports.html",
            total_patients=total_patients,
            total_doctors=total_doctors,
            total_appointments=total_appointments,
            pending=appointment_stats["Pending"],
            confirmed=appointment_stats["Confirmed"],
            completed=appointment_stats["Completed"],
            cancelled=appointment_stats["Cancelled"]
        )

    except Error as e:
        print("Database error:", e)
        return "Something went wrong."

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.route(
    "/patient/cancel-appointment/<int:appointment_id>",
    methods=["POST"]
)
def cancel_appointment(appointment_id):

    # Check login
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Only patients can cancel
    if session.get("role") != "patient":
        return "Access Denied", 403

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Important security check:
        # The appointment must belong to the logged-in patient
        query = """
            UPDATE appointments
            SET status = 'Cancelled'
            WHERE appointment_id = %s
            AND patient_id = %s
            AND status IN ('Pending', 'Confirmed')
        """

        cursor.execute(
            query,
            (
                appointment_id,
                session["user_id"]
            )
        )

        connection.commit()

        return redirect(
            url_for("patient_appointments")
        )

    except Error as e:
        print("Database error:", e)
        return "Something went wrong."

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

# -------------------------
# Logout
# -------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)