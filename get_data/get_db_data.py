# main.py
from db.session import SessionLocal
from db.model.artists import Artist

# 建立 Session
db = SessionLocal()

# 查詢所有使用者
artist = db.query(Artist).all()
for user in artist:
    print(user.name)

# 結束 Session
db.close()
