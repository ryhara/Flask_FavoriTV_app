# Flask FavoriTV app

お気に入りのTV番組登録・管理アプリ

ユーザー機能、パブリックユーザーのお気に入り閲覧、番組登録・検索、出演者情報編集など

## Version
- Python 3.10.6
- Flask 2.3.2
- Werkzeug 2.3.6
- Bootstrap 5.0.2
- Font Awesome 5.15.4
- sqlite3

## images
<p align="center">
  <img src="static/report/home.png" alt="static/report/home.png" width="200"/>
  <img src="static/report/login.png" alt="static/report/login.png" width="200"/>
  <img src="static/report/signup.png" alt="static/report/signup.png" width="200"/>
  <img src="static/report/mypage.png" alt="static/report/mypage.png" width="200"/>
  <img src="static/report/mypage_edit.png" alt="static/report/mypage_edit.png" width="200"/>
  <img src="static/report/my_program.png" alt="static/report/my_program.png" width="200"/>
  <img src="static/report/program_show_favorite.png" alt="static/report/program_show_favorite.png" width="200"/>
  <img src="static/report/program_show_not.png" alt="static/report/program_show_not.png" width="200"/>
  <img src="static/report/program_new.png" alt="static/report/program_new.png" width="200"/>
  <img src="static/report/program_edit.png" alt="static/report/program_edit.png" width="200"/>
  <img src="static/report/program_search.png" alt="static/report/program_search.png" width="200"/>
  <img src="static/report/perform_new.png" alt="static/report/perform_new.png" width="200"/>
  <img src="static/report/perform_edit.png" alt="static/report/perform_edit.png" width="200"/>
  <img src="static/report/user_index.png" alt="static/report/user_index.png" width="200"/>
  <img src="static/report/user_show.png" alt="static/report/user_show.png" width="200"/>
 
 
</p>

## Usage
```
git clone https://github.com/ryhara/Flask_FavoriTV_app.git
```

mac or linux

```
python3 -m venv venv
. venv/bin/activate
pip install Flask
flask run
```

windows
```
py -3 -m venv venv
venv/Scripts/activate
pip install Flask
flask run
```
https://msiz07-flask-docs-ja.readthedocs.io/ja/latest/installation.html


### Initialize database
```
sqlite3 database.db < sql/insert.sql
```

## References
- [https://github.com/FujikiLab/dm_app](https://github.com/FujikiLab/dm_app)
- [https://msiz07-flask-docs-ja.readthedocs.io/ja/latest/installation.html](https://msiz07-flask-docs-ja.readthedocs.io/ja/latest/installation.html)
- [Bootstrap](https://getbootstrap.jp/)
- [Font awesome](https://fontawesome.com/)
- [いらすとや](https://www.irasutoya.com/)
- [TVer](https://tver.jp/)
- [番組表 Gガイド](https://bangumi.org/)
