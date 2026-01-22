import streamlit as st
from supabase import create_client, Client
import datetime

# --- 初期設定 ---
st.set_page_config(page_title="マイ読書ログ", layout="centered")

# Supabase接続設定
# ローカルでは .streamlit/secrets.toml、Cloudでは管理画面から読み込みます
url: str = st.secrets["supabase_url"]
key: str = st.secrets["supabase_key"]
supabase: Client = create_client(url, key)

# --- 関数定義 ---
def fetch_books():
    """本の一覧を最新順に取得"""
    response = supabase.table("books").select("*").order("created_at", desc=True).execute()
    return response.data

def add_book(title, author, rating, read_date, review):
    """新しい本を登録"""
    data = {
        "title": title,
        "author": author,
        "rating": rating,
        "read_date": str(read_date),
        "review": review
    }
    supabase.table("books").insert(data).execute()

def delete_book(book_id):
    """本を削除"""
    supabase.table("books").delete().eq("id", book_id).execute()

# --- メイン UI ---
st.title("📚 マイ読書ログ管理")

# --- 1. 集計エリア ---
books_data = fetch_books()
total_books = len(books_data)

if total_books > 0:
    avg_rating = sum(book['rating'] for book in books_data) / total_books
    
    col1, col2 = st.columns(2)
    col1.metric("累計読書数", f"{total_books} 冊")
    col2.metric("平均評価", f"★ {avg_rating:.1f}")
else:
    st.info("まだ登録された本がありません。")

st.divider()

# --- 2. 登録フォーム ---
with st.expander("➕ 新しい本を登録する"):
    with st.form("add_form", clear_on_submit=True):
        title = st.text_input("タイトル（必須）")
        author = st.text_input("著者名")
        rating = st.slider("評価", 1, 5, 3)
        read_date = st.date_input("読了日", datetime.date.today())
        review = st.text_area("一言感想")
        
        submitted = st.form_submit_button("保存する")
        if submitted:
            if title:
                add_book(title, author, rating, read_date, review)
                st.success("登録しました！")
                st.rerun() # 再読み込み
            else:
                st.error("タイトルを入力してください。")

# --- 3. ログの表示 ---
st.subheader("📖 読書ログ一覧")

for book in books_data:
    with st.container():
        # カード形式で表示
        cols = st.columns([0.7, 0.3])
        with cols[0]:
            st.markdown(f"### {book['title']}")
            st.caption(f"著者: {book['author']} | 読了日: {book['read_date']}")
        with cols[1]:
            st.markdown(f"### {'⭐' * book['rating']}")
        
        st.write(book['review'])
        
        # 削除ボタン
        if st.button(f"削除", key=f"del_{book['id']}", type="secondary"):
            delete_book(book['id'])
            st.warning(f"「{book['title']}」を削除しました。")
            st.rerun()
        
        st.divider()
        