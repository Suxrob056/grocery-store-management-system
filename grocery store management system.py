import sqlite3
from datetime import datetime
import os
from PIL import Image, ImageDraw, ImageFont

def connect_db():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    # Mahsulotlar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)
    # Savdo tarixi jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            sale_date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def mahsulot_qoshish(nomi, narxi, miqdor):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", (nomi, narxi, miqdor))
    conn.commit()
    conn.close()
    print(f"\n✅ '{nomi}' mahsuloti muvaffaqiyatli qo'shildi!")

def mahsulot_korsatish():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    print("\n" + "="*50)
    print(f"{'ID':<5} {'Mahsulot nomi':<20} {'Narxi (so\'m)':<15} {'Miqdori':<10}")
    print("="*50)
    if not products:
        print("Bazada hech qanday mahsulot yo'q")
    else:
        for m in products:
            print(f"{m[0]:<5} {m[1]:<20} {m[2]:<15.2f} {m[3]:<10}")
    print("="*50)

def mahsulot_qidirish(kalit_soz):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f"%{kalit_soz}%",))
    products = cursor.fetchall()
    conn.close()
    
    print("\n" + "="*50)
    print(f"Qidiruv natijalari ('{kalit_soz}'):")
    print(f"{'ID':<5} {'Mahsulot nomi':<20} {'Narxi (so\'m)':<15} {'Miqdori':<10}")
    print("="*50)
    if not products:
        print("Bunday mahsulot topilmadi.")
    else:
        for m in products:
            print(f"{m[0]:<5} {m[1]:<20} {m[2]:<15.2f} {m[3]:<10}")
    print("="*50)

# Chekni rasm ko'rinishida yaratish funksiyasi
def chek_rasmini_yaratish(nomi, sanash, narxi, total_price, sale_date):
    width = 300
    height = 380
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    
    # Shriftlarni sozlash (Windows uchun Arial, topilmasa standart)
    try:
        font_title = ImageFont.truetype("arial.ttf", 14)
        font_text = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
        
    # Matnlarni rasmga chizish
    y = 20
    draw.text((100, y), "SAVDO CHEKI", fill="black", font=font_title)
    y += 35
    draw.text((20, y), "-" * 48, fill="black", font=font_text)
    y += 20
    draw.text((20, y), "Do'kon: Oziq-ovqat Do'koni", fill="black", font=font_text)
    y += 25
    draw.text((20, y), f"Sana va vaqt: {sale_date}", fill="black", font=font_text)
    y += 25
    draw.text((20, y), "-" * 48, fill="black", font=font_text)
    y += 25
    draw.text((20, y), f"Mahsulot: {nomi}", fill="black", font=font_text)
    y += 25
    draw.text((20, y), f"Dona narxi: {narxi:,.2f} so'm", fill="black", font=font_text)
    y += 25
    draw.text((20, y), f"Miqdori: {sanash} ta", fill="black", font=font_text)
    y += 25
    draw.text((20, y), "-" * 48, fill="black", font=font_text)
    y += 25
    draw.text((20, y), f"Jami summa: {total_price:,.2f} so'm", fill="black", font=font_title)
    y += 35
    draw.text((110, y), "Xaridingiz uchun rahmat!", fill="black", font=font_text)
    
    # Faylga saqlash
    filename = "savdo_cheki.png"
    image.save(filename)
    print(f"\n🖼️ Chek rasm ko'rinishida saqlandi: '{filename}'")
    
    # Rasmni avtomatik ochish (Windows uchun)
    try:
        os.startfile(filename)
    except AttributeError:
        # Mac yoki Linux uchun
        pass

def mahsulot_sotish(mahsulot_id, sanash):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, price, quantity FROM products WHERE id = ?", (mahsulot_id,))
    product = cursor.fetchone()

    if not product:
        print("\n❌ Bunday ID ga ega mahsulot topilmadi!")
        conn.close()
        return

    nomi, narxi, aksiya = product
    if aksiya < sanash:
        print(f"\n⚠️ Omborda yetarli mahsulot yo'q! Hozirda bor: {aksiya} ta")
    else:
        yangi_aksiya = aksiya - sanash
        cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (yangi_aksiya, mahsulot_id))
        
        total_price = narxi * sanash
        sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Savdoni tarixga yozish
        cursor.execute("INSERT INTO sales (product_name, quantity, total_price, sale_date) VALUES (?, ?, ?, ?)", 
                       (nomi, sanash, total_price, sale_date))
        conn.commit()
        
        print(f"\n🛒 Savdo bajarildi!")
        print(f"Mahsulot: {nomi} | Soni: {sanash} ta | Jami summa: {total_price:.2f} so'm")
        
        # Rasm chekni chaqirish
        chek_rasmini_yaratish(nomi, sanash, narxi, total_price, sale_date)

    conn.close()

def yangilash_zaxirasi(mahsulot_id, yangi_miqdor):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET quantity = quantity + ? WHERE id = ?", (yangi_miqdor, mahsulot_id))
    conn.commit()
    conn.close()
    print("\n✅ Mahsulot miqdori yangilandi!")

def mahsulot_tahrirlash(mahsulot_id, yangi_nomi, yangi_narxi):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name = ?, price = ? WHERE id = ?", (yangi_nomi, yangi_narxi, mahsulot_id))
    conn.commit()
    conn.close()
    print("\n✅ Mahsulot ma'lumotlari muvaffaqiyatli tahrirlandi!")

def mahsulot_ochirish(mahsulot_id):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (mahsulot_id,))
    conn.commit()
    conn.close()
    print("\n🗑️ Mahsulot bazadan o'chirildi!")

def savdo_tarixini_korsatish():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales")
    sales = cursor.fetchall()
    conn.close()
    
    print("\n" + "="*70)
    print(f"{'ID':<5} {'Mahsulot nomi':<20} {'Soni':<8} {'Jami summa':<15} {'Sana va Vaqt':<20}")
    print("="*70)
    if not sales:
        print("Hozircha savdo tarixi mavjud emas.")
    else:
        for s in sales:
            print(f"{s[0]:<5} {s[1]:<20} {s[2]:<8} {s[3]:<15.2f} {s[4]:<20}") # s[1]:<20 Ikkinchi element (s[1]) chapga tekislangan, kengligi 20 belgi
    print("="*70)

def main():
    connect_db()

    while True:
        print("\n=== OZIQ-OVQAT DO'KONI BOSHQARUV TIZIMI ===")
        print("1. Mahsulotlar ro'yxatini ko'rish")
        print("2. Yangi mahsulot qo'shish")
        print("3. Mahsulot sotish (POS)")
        print("4. Ombor qoldig'ini to'ldirish")
        print("5. Mahsulotni qidirish")
        print("6. Mahsulotni tahrirlash")
        print("7. Mahsulotni o'chirish")
        print("8. Savdo tarixini ko'rish")
        print("9. Chiqish")

        tanlov = input("Tanlovingizni kiriting (1-9): ").strip()

        if tanlov == '1':
            mahsulot_korsatish()
        elif tanlov == '2':
            nomi = input("Mahsulot nomi: ").strip()
            try:
                narxi = float(input("Narxi: "))
                miqdor = int(input("Miqdori (dona/kg): "))
                mahsulot_qoshish(nomi, narxi, miqdor)
            except ValueError:
                print("\n❌ Xatolik: Narx va miqdorga faqat raqam kiritishingiz kerak!")
        elif tanlov == '3':
            try:
                m_id = int(input("Sotilayotgan mahsulot ID si: "))
                sanash = int(input("Nechta sotilmoqda: "))
                mahsulot_sotish(m_id, sanash)
            except ValueError:
                print("\n❌ Xatolik: ID va sanashni to'g'ri kiriting!")
        elif tanlov == '4':
            try:
                m_id = int(input("Mahsulot ID si: "))
                qoshish_soni = int(input("Qancha qo'shmoqchisiz: "))
                yangilash_zaxirasi(m_id, qoshish_soni)
            except ValueError:
                print("\n❌ Xatolik: Noto'g'ri raqam kiritildi!")
        elif tanlov == '5':
            kalit_soz = input("Qidirilayotgan mahsulot nomi: ").strip()
            mahsulot_qidirish(kalit_soz)
        elif tanlov == '6':
            try:
                m_id = int(input("Tahrirlanadigan mahsulot ID si: "))
                yangi_nomi = input("Yangi nomi: ").strip()
                yangi_narxi = float(input("Yangi narxi: "))
                mahsulot_tahrirlash(m_id, yangi_nomi, yangi_narxi)
            except ValueError:
                print("\n❌ Xatolik: Noto'g'ri qiymat kiritildi!")
        elif tanlov == '7':
            try:
                m_id = int(input("O'chiriladigan mahsulot ID si: "))
                confirm = input("Haqiqatan ham o'chirmoqchimisiz? (ha/yo'q): ").strip().lower()
                if confirm == 'ha':
                    mahsulot_ochirish(m_id)
                else:
                    print("\nO'chirish bekor qilindi.")
            except ValueError:
                print("\n❌ Xatolik: ID butun raqam bo'lishi kerak!")
        elif tanlov == '8':
            savdo_tarixini_korsatish()
        elif tanlov == '9':
            print("\nTizimdan chiqildi. Xayr!")
            break
        else:
            print("\n❌ Noto'g'ri buyruq! Qaytadan urinib ko'ring.")

if __name__ == "__main__":
    main()