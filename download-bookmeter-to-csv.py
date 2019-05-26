# coding: UTF-8
import csv
import time
import requests
from bs4 import BeautifulSoup

# 読書メータの本を格納するDTO
class Book(object):
    def __init__(self, title, auther, readed_date, page):
        self.title = title
        self.auther = auther
        self.readed_date = readed_date
        self.page = page

# 次のページを返す
def get_next_page(current_page, soup_res):

    # ページ一覧を取得する
    pagination_list = []
    pl = soup_res.find_all("a", class_="bm-pagination__link")
    for l in pl:
        pagination_list.append([l.string, l.get("href")])

    # 次のページへ移動するかどうかの判定
    next_page_no = None
    for pagination in pagination_list:
        if str(current_page) in pagination:
            next_page_no = pagination[1]
    return(next_page_no)

# TODO: 設定ファイルとして外だししたい
user = ""
password = ""

url_base = "https://bookmeter.com"
url_login = "https://bookmeter.com/login"
login_info = {
    "session[email_address]": user,
    "session[password]": password,
    "utf8": "✓",
    "session[keep]": "0"
}

# authenticity_tokenの取得
session = requests.session()
r = session.get(url_login)
soup = BeautifulSoup(r.text, "lxml")
auth_token = soup.find(attrs={'name': 'authenticity_token'}).get('value')
login_info['authenticity_token'] = auth_token


# login
res = session.post(url_login, data=login_info)
res.raise_for_status()


books_list = []
current_pagination = 1

# 読んだ本ページへ。URLは自分のやつを入れる
next_url = "https://bookmeter.com/users/117579/books/read?display_type=list"


while True:
    time.sleep(30)
    res = session.get(next_url)
    res.raise_for_status
    s = BeautifulSoup(res.text, "lxml")

    # 読んだ本の取得
    books_s = s.select("li.group__book")
    for b in books_s:
        t = b.find("div", class_="detail__title").find("a").string
        d = b.find("div", class_="detail__date").string
        a = b.find("ul", class_="detail__authors").find("a").string
        p = b.find("div", class_="detail__page").string

        l = Book(t,a,d,p)
        books_list.append(l)

    # 次のページが有るのか
    current_pagination = current_pagination + 1
    next_url = get_next_page(current_pagination,s)
    if next_url is not None:
        next_url = url_base + next_url
        continue
    break

# output
with open("book.csv", "w", newline="") as f:
    writer = csv.writer(f)
    for b in books_list:
        writer.writerow([b.readed_date, b.title,b.auther,b.page])
        print(b.title, b.auther, b.readed_date, b.page)
f.close()

