from database_manager import init_db

if __name__ == "__main__":
    # This will create all tables defined in the models
    init_db()
    print("Database migration completed successfully.")