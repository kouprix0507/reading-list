import streamlit as st
from supabase import create_client, Client
import datetime

# --- 初期設定 ---
st.set_page_config(page_title="多機能読書ログ", layout="wide")

# Supabase接続
url: str = st.secrets["supabase_url"]
key: str = st.secrets["supabase_key"]
supabase: Client = create_client(url, key)

# --- データベース操作 ---
def fetch_data():
    response = supabase.table("books").select("*").execute()
    return response.data

def insert_data(title, author, rating, read_date, review, category):
    data = {
        "title": title,
        "author": author,
        "rating": rating,
        "read_date": str(read_date),
        "review": review,
        "category": category
    }
    supabase.table("books").insert(data).execute()

def delete_data(book_id):
    supabase.table("books").delete().eq("id", book_id).execute()

# --- サイドバー：検索とソート (機能4) ---
st.sidebar.header("🔍 フィルタと検索")
search_query = st.sidebar.text_input("タイトル・感想で検索")
category_filter = st.sidebar.multiselect(
    "カテゴリで絞り込み",
    ["ビジネス", "小説", "技術書", "自己啓発", "漫画", "その他"],
    default=[]
)
sort_option = st.sidebar.selectbox(
    "並び替え",
    ["最新の登録順", "読了日が新しい順", "評価が高い順"]
)

# --- メイン UI ---
st.title("📚 多機能読書ログ管理")

# データの取得とフィルタリング
all_books = fetch_data()

# 検索フィルタ
display_books = [
    b for b in all_books
    if search_query.lower() in b['title'].lower() or search_query.lower() in (b['review'] or "").lower()
]

# カテゴリフィルタ (機能3)
if category_filter:
    display_books = [b for b in display_books if b.get('category') in category_filter]

# 並び替え処理 (機能4)
if sort_option == "最新の登録順":
    display_books.sort(key=lambda x: x['created_at'], reverse=True)
elif sort_option == "読了日が新しい順":
    display_books.sort(key=lambda x: x['read_date'], reverse=True)
elif sort_option == "評価が高い順":
    display_books.sort(key=lambda x: x['rating'], reverse=True)

# 集計表示
st.caption(f"該当件数: {len(display_books)} 冊")

# --- 登録フォーム (機能3：カテゴリ追加) ---
with st.expander("➕ 新しい本を登録する"):
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input("タイトル（必須）")
            author = st.text_input("著者")
        with c2:
            category = st.selectbox("カテゴリ", ["ビジネス", "小説", "技術書", "自己啓発", "漫画", "その他"])
            read_date = st.date_input("読了日", datetime.date.today())
        
        rating = st.select_slider("評価", options=[1, 2, 3, 4, 5], value=3)
        review = st.text_area("感想・メモ")
        
        if st.form_submit_button("保存する"):
            if title:
                insert_data(title, author, rating, read_date, review, category)
                st.success("保存完了！")
                st.rerun()
            else:
                st.error("タイトルは必須です")

# --- 表示エリア ---
if not display_books:
    st.info("条件に一致する本が見つかりません。")
else:
    # 2カラムでカードを表示
    cols = st.columns(2)
    for i, book in enumerate(display_books):
        with cols[i % 2].container(border=True):
            # カテゴリをバッジ風に表示
            st.markdown(f"**{book['title']}** <small>[{book.get('category', '未設定')}]</small>", unsafe_allow_html=True)
            st.caption(f"{book['author']} | {book['read_date']} 読了")
            st.write(f"{'⭐' * book['rating']}")
            
            if book['review']:
                st.info(book['review'])
            
            if st.button("削除", key=f"del_{book['id']}"):
                delete_data(book['id'])
                st.rerun()
