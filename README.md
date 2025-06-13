# venv
```
source testenv/bin/activate
deactivate
```

# Back End

```
uvicorn main:app --reload
```

# SQL
```
cd code/backend
sqlite3 db.sqlite3
```
# github
## …or create a new repository on the command line
```
git init
git add .
git add .gitignore
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/yixiang-liao/BinMusic.git
git push -u origin main
```
## …or push an existing repository from the command line
```
git remote add origin https://github.com/yixiang-liao/BinMusic.git
git branch -M main
git push -u origin main
```

# 刪除._開頭的檔案
```
find . -name '._*' -type f -delete
```