from app.db import get_db_connection

# -------------------- COMPANIES --------------------

def get_all_companies():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM companies ORDER BY company_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def create_company(data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO companies (company_name, company_number, company_director, company_phone_number, company_email, company_address)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING company_id
    """, (
        data.company_name,
        data.company_number,
        data.company_director,
        data.company_phone_number,
        data.company_email,
        data.company_address
    ))
    company_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return company_id

# -------------------- OPERATORS --------------------

def get_all_operators():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM operators ORDER BY operator_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def create_operator(data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO operators (operator_name, identify_id)
        VALUES (%s, %s) RETURNING operator_id
    """, (data.operator_name, data.identify_id))
    operator_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return operator_id

# -------------------- COMPUTERS --------------------

def get_all_computers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM computers ORDER BY computer_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def create_computer(data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO computers (computer_guid, computer_mac_address)
        VALUES (%s, %s) RETURNING computer_id
    """, (data.computer_guid, data.computer_mac_address))
    computer_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return computer_id

# -------------------- SOFTWARES --------------------

def get_all_softwares():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM softwares ORDER BY software_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def create_software(data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO softwares (software_name, price)
        VALUES (%s, %s) RETURNING software_id
    """, (data.software_name, data.price))
    software_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return software_id

# -------------------- LICENSES --------------------

def get_all_licenses():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM licenses ORDER BY license_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def create_license(data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO licenses (
            company_id, operator_id, computer_id, software_id,
            expire_date, paid, stayed, status, license_status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING license_id
    """, (
        data.company_id, data.operator_id, data.computer_id, data.software_id,
        data.expire_date, data.paid, data.stayed, data.status, data.license_status
    ))
    license_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return license_id
