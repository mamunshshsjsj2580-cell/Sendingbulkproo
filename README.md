# 📧 Gmail Bulk Sender Pro v5.0

**আলটিমেট ইমেইল মার্কেটিং অটোমেশন টুল**

## ✨ ফিচার

### 🔐 অথেন্টিকেশন
- ✅ Desktop Google API OAuth
- ✅ মাল্টি-একাউন্ট সাপোর্ট
- ✅ Secure Token Storage
- ✅ Automatic Token Refresh

### 📬 সেন্ডিং
- ✅ 5 পারালাল টাস্ক
- ✅ 520 ইমেইল প্রতি টাস্ক
- ✅ পারটুন 2600 ইমেইল দৈনিক
- ✅ অটো-ডিলে (অ্যান্টি-ডিটেকশন)
- ✅ রিয়েল-টাইম লগিং

### 🎯 ক্যাম্পেইন
- ✅ প্রি-বিল্ট প্রিসেট
- ✅ কাস্টম সাবজেক্ট/বডি
- ✅ ডাইনামিক ভেরিয়েবল সাপোর্ট
- ✅ HTML/প্লেইন টেক্সট সাপোর্ট

### 📊 রিপোর্টিং
- ✅ লাইভ ড্যাশবোর্ড
- ✅ সাক্সেস/ফেইলার ট্র্যাকিং
- ✅ CSV এক্সপোর্ট
- ✅ বিস্তারিত লগ

### 🛡️ অ্যান্টি-ডিটেকশন
- ✅ র্যান্ডম ডিলে
- ✅ কাস্টম হেডার
- ✅ র্যান্ডম Message-ID
- ✅ ভেরী মেইলার সিগনেচার

## 🚀 ইনস্টলেশন

### প্রয়োজনীয়তা
- Python 3.8+
- pip
- Gmail Desktop OAuth Credentials

### স্টেপ 1: রিপোজিটরি ক্লোন করুন

```bash
git clone https://github.com/mamunshshsjsj2580-cell/Sendingbulkproo.git
cd Sendingbulkproo
```

### স্টেপ 2: পরিবেশ সেটআপ করুন

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate  # Windows
```

### স্টেপ 3: প্যাকেজ ইনস্টল করুন

```bash
pip install -r requirements.txt
```

### স্টেপ 4: Google OAuth সেটআপ করুন

1. [Google Cloud Console](https://console.cloud.google.com/) এ যান
2. নতুন প্রজেক্ট তৈরি করুন
3. Gmail API এনাবল করুন
4. OAuth 2.0 ক্রেডেনশিয়াল (Desktop App) তৈরি করুন
5. `credentials.json` ডাউনলোড করুন

### স্টেপ 5: অ্যাপ চালান

```bash
python main.py
```

## 📖 ব্যবহার

### অ্যাকাউন্ট যোগ করুন

1. **📧 অ্যাকাউন্ট** ট্যাবে খুলুন
2. **📁 credentials.json ইমপোর্ট করুন** ক্লিক করুন
3. আপনার `credentials.json` ফাইল সিলেক্ট করুন
4. Gmail এ লগইন করুন এবং অনুমতি দিন
5. অ্যাকাউন্ট যোগ হয়ে যাবে

### ক্যাম্পেইন তৈরি করুন

1. **🚀 ক্যাম্পেইন** ট্যাবে যান
2. অ্যাকাউন্ট সিলেক্ট করুন
3. প্রিসেট বা কাস্টম সাবজেক্ট/বডি সেট করুন
4. ইমেইল লিস্ট পেস্ট করুন (প্রতি লাইনে একটি)
5. **✅ সেন্ড শুরু করুন** ক্লিক করুন

### ড্যাশবোর্ড চেক করুন

1. **📊 ড্যাশবোর্ড** ট্যাবে যান
2. রিয়েল-টাইম সংখ্যা দেখুন
3. **🔄 রিফ্রেশ** ক্লিক করুন আপডেটের জন্য

## ⚙️ কনফিগারেশন

`config.json` সম্পাদনা করুন:

```json
{
  "gmail": {
    "max_daily_limit": 2600,
    "max_workers": 5,
    "emails_per_task": 520,
    "delay_min": 1.0,
    "delay_max": 3.0
  }
}
```

## 🎯 প্রিসেট টাইপ

### Sales (বিক্রয়)
- "Special Offer Just For You! 🎁"
- "50% OFF - Exclusive Deal"

### Newsletter (নিউজলেটার)
- "Monthly Newsletter - {month}"
- "Weekly Digest - Week {week}"

### Notification (নোটিফিকেশন)
- "Important Account Update"
- "Action Required - Verify Your Account"

### Invoice (ইনভয়েস)
- "Your Receipt #{invoice_id}"
- "Payment Confirmation - Invoice #{invoice_id}"

## 🐛 ট্রাবলশুটিং

### সমস্যা: "Invalid credentials.json"
**সমাধান:** Desktop App type নির্বাচন করুন, Web App নয়

### সমস্যা: "Gmail API not enabled"
**সমাধান:** Google Cloud Console-এ Gmail API এনাবল করুন

### সমস্যা: "Rate Limited"
**সমাধান:** ডিলে বৃদ্ধি করুন বা কম অ্যাকাউন্ট ব্যবহার করুন

## 📞 সাপোর্ট

সমস্যা বা সাজেশনের জন্য:
- GitHub Issues খুলুন
- বিস্তারিত এরর লগ প্রদান করুন

## ⚖️ লাইসেন্স

MIT License - বিস্তারিত `LICENSE` ফাইল দেখুন

## ⭐ স্টার দিন

প্রজেক্ট পছন্দ হলে **⭐ star** দিন!

---

**Made with ❤️ by the community**
