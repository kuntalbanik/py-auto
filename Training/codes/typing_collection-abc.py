'''
সহজ কথায়: collections.abc ব্যবহার করা হয় স্ট্যান্ডার্ড ডেটা স্ট্রাকচারের (যেমন List, Dict) ভেতরের ডেটা টাইপ বোঝাতে, আর typing ব্যবহার করা হয় জটিল লজিক (যেমন Function, Optional, Any) হ্যান্ডেল করতে। [python The typing / collections.abc]




১. রিয়েল-ওয়ার্ল্ড প্রোজেক্টে collections.abc এর ব্যবহারধরা যাক, আপনি একটি E-commerce Website বা Banking Application বানাচ্ছেন। সেখানে ডাটাবেজ থেকে অনেকগুলো প্রোডাক্ট বা ইউজারের ডেটা একসাথে নিয়ে কাজ করতে হয়। কোথায় ব্যবহার হয়: যখন আপনি নিশ্চিত করতে চান যে আপনার ফাংশনটি একটি নির্দিষ্ট ধরণের কালেকশন (যেমন কেবল রিড-অনলি লিস্ট বা ডিকশনারি) রিসিভ করবে।রিয়েল এক্সাম্পল (API Response handling):



Sequence: এটি দিয়ে বোঝানো হয় যে ইনপুট হিসেবে এমন কিছু আসবে যা ইনডেক্স (0, 1, 2) মেনে চলে। যেমন: List বা Tuple।

Mapping: এটি দিয়ে বোঝানো হয় যে ইনপুট হিসেবে কোনো Key-Value পেয়ার আসবে। যেমন: Dictionary।

Iterable: এটি দিয়ে বোঝানো হয় যে ইনপুটটিকে লুপ (for loop) চালানো যাবে।




from collections.abc import Sequence, Mapping

# ডাটাবেজ থেকে ইউজারদের লিস্ট রিড করার জন্য (Sequence ব্যবহার করা নিরাপদ)
def process_user_profiles(users: Sequence[Mapping[str, str]]) -> None:
    for user in users:
        print(f"User Name: {user['name']}")

# প্রোজেক্টে ব্যবহার:
db_data = [
    {"name": "Asif", "email": "asif@email.com"},
    {"name": "Sultana", "email": "sultana@email.com"}
]
process_user_profiles(db_data)


:::  এখানে Sequence ব্যবহার করার সুবিধা হলো, ফাংশনটি list বা tuple দুই ধরনের ডেটাই গ্রহণ করতে পারবে।


==============================================================

২. রিয়েল-ওয়ার্ল্ড প্রোজেক্টে typing এর ব্যবহারধরা যাক, আপনি একটি User Authentication System বা Payment Gateway Integration-এর কাজ করছেন। এখানে অনেক সময় ডেটা মিসিং থাকতে পারে বা কোনো ফাংশনকে অন্য ফাংশনে পাস করতে হতে পারে।কোথায় ব্যবহার হয়: যখন ফাংশনের রিটার্ন টাইপ ফিক্সড থাকে না (যেমন কখনো স্ট্রিং, কখনো None) কিংবা অ্যাডভান্সড লজিক থাকে [python The typing / collections.abc]।রিয়েল এক্সাম্পল (User Authentication):



Callable: যখন কোনো ফাংশনের ভেতরে অন্য আরেকটি ফাংশনকে আর্গুমেন্ট (যেমন: Callback Function) হিসেবে পাস করতে হয়।

Any: যখন কোনো ভেরিয়েবলে যেকোনো ধরণের ডেটা (String, Int, Object) আসতে পারে এবং টাইপ নির্দিষ্ট করা সম্ভব হয় না।

Literal: যখন কোনো ভেরিয়েবলের মান শুধুমাত্র কয়েকটি নির্দিষ্ট ফিক্সড ভ্যালুর একটি হতে পারবে।




# পাইথন ৩.১০+ ভার্সনে typing মডিউলের অনেক ফিচার সরাসরি সিম্বল (যেমন '|') দিয়ে করা যায়
def get_user_role(user_id: int) -> str | None:
    # ডাটাবেজে ইউজার খোঁজা হচ্ছে
    user_exists = True 
    if user_exists:
        return "Admin"
    return None # ইউজার না থাকলে None রিটার্ন করবে

# typing থেকে Callable এর রিয়েল ব্যবহার (Payment Success Callback)
from typing import Callable

def process_payment(amount: float, on_success: Callable[[str], None]) -> None:
    # পেমেন্ট প্রসেস হওয়ার লজিক...
    transaction_id = "TXN12345"
    on_success(transaction_id) # পেমেন্ট সফল হলে এই ফাংশনটি রান করবে




১. collections.abc ব্যবহার করবেন: যখন ফাংশনের আর্গুমেন্টে List, Dict, Set, বা Tuple এর মতো কালেকশন নিয়ে কাজ করবেন [python The typing / collections.abc]। 

পাইথন ৩.৯+ এর পর থেকে বড় প্রোজেক্টে টাইপ হিন্টিংয়ের জন্য collections.abc.Sequence বা collections.abc.Mapping ব্যবহার করাটাই বেস্ট প্র্যাকটিস [python The typing / collections.abc]।


২. typing ব্যবহার করবেন: যখন আপনার Any (যেকোনো টাইপ), Callable (ফাংশন পাস করা), বা Literal (নির্দিষ্ট কিছু ফিক্সড ভ্যালু) এর মতো জটিল টাইপ চেকিংয়ের প্রয়োজন হবে [python The typing / collections.abc]।



নোট: পাইথন ৩.১০+ ভার্সন থেকে Optional বা Union এর কাজগুলো এখন সরাসরি | (Pipe) অপারেটর দিয়ে করা যায় (যেমন: str | None), তাই সেগুলোর জন্য এখন আর typing মডিউল লাগে না।


================================================================================

'''