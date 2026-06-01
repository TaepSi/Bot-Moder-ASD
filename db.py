from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_bad_words():
    res = supabase.table("bad_words").select("word").execute()
    return [x["word"] for x in res.data]


def add_report(chat_id, reporter_id, text, reason):
    supabase.table("reports").insert({
        "chat_id": chat_id,
        "reporter_id": reporter_id,
        "message_text": text,
        "reason": reason
    }).execute()