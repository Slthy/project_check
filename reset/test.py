import pymysql

def test_mysql_connection():
    # Replace these with your actual AWS RDS details
    db_host = "regs26-borsato.cng0skw0wk8a.us-east-1.rds.amazonaws.com"
    db_port = 3306  # Default MySQL port
    db_name = "university"
    db_user = "birdsarenotreal"
    db_pass = "birdsarenotreal123"

    print(f"Attempting to connect to {db_host}...")

    try:
        # connect_timeout=10 ensures the script doesn't hang forever if blocked by a firewall
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_pass,
            connect_timeout=10
        )
        
        # Test the connection by grabbing the DB version
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        db_version = cursor.fetchone()
        
        print("✅ Connection successful!")
        print(f"MySQL Database Version: {db_version[0]}")
        
        cursor.close()
        connection.close()

    except pymysql.MySQLError as e:
        print("❌ Connection failed!")
        print(e)

if __name__ == "__main__":
    test_mysql_connection()