from passlib.context import CryptContext

def generate_admin_password_hash():
    """
    生成并打印 'Admin.123' 密码的 bcrypt 哈希值。
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("Admin.123")
    print(f"生成的 'Admin.123' 密码哈希值为: {hashed_password}")
    print("请将此哈希值复制到 backend/init.sql 文件中替换 'YOUR_ACTUAL_HASH_FOR_Admin.123'。")

if __name__ == "__main__":
    generate_admin_password_hash() 