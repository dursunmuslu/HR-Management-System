from datetime import date
from app.database.database import SessionLocal
from app.models.company import Company
from app.models.department import Department
from app.models.employee import Employee
from app.models.user import User
from app.models.quiz_and_shift import Quiz, ShiftSchedule
from app.security.password import hash_password
from app.security.user_role import UserRole

def verileri_doldur():
    db = SessionLocal()
    try:
        # Şirketi bul
        sirket = db.query(Company).first()
        if not sirket:
            print("HATA: Veritabanında henüz hiç şirket yok!")
            return

        print(f"[{sirket.name}] için test verileri basılıyor...")

        # 1. Departmanları Ekle
        depts = []
        for d_ad in ["Yazılım & Bilişim", "İnsan Kaynakları", "Pazarlama & Satış"]:
            dept = db.query(Department).filter(Department.company_id == sirket.id, Department.name == d_ad).first()
            if not dept:
                dept = Department(company_id=sirket.id, name=d_ad, code=d_ad[:3].upper())
                db.add(dept)
                db.flush()
            depts.append(dept)

        # 2. Hazır Personelleri Ekle
        personeller = [
            {"kadi": "ahmet.yilmaz", "ad": "Ahmet", "soyad": "Yılmaz", "unvan": "Frontend Geliştirici", "dept": depts[0].id},
            {"kadi": "ayse.kaya", "ad": "Ayşe", "soyad": "Kaya", "unvan": "İK Uzmanı", "dept": depts[1].id},
            {"kadi": "mehmet.oz", "ad": "Mehmet", "soyad": "Öz", "unvan": "Full Stack Dev", "dept": depts[0].id},
            {"kadi": "zeynep.demir", "ad": "Zeynep", "soyad": "Demir", "unvan": "Satış Temsilcisi", "dept": depts[2].id},
        ]

        for p in personeller:
            u = db.query(User).filter(User.username == p["kadi"]).first()
            if not u:
                u = User(
                    username=p["kadi"],
                    password=hash_password("123456"),
                    role=UserRole.PERSONEL.value,
                    company_id=sirket.id,
                    is_active=True,
                    must_change_password=False
                )
                db.add(u)
                db.flush()

                emp = Employee(
                    company_id=sirket.id,
                    user_id=u.id,
                    department_id=p["dept"],
                    first_name=p["ad"],
                    last_name=p["soyad"],
                    job_title=p["unvan"],
                    hire_date=date(2025, 1, 15),
                    work_email=f"{p['kadi']}@sirket.com",
                    annual_leave_balance=14
                )
                db.add(emp)

        # 3. Hazır Quizleri Ekle
        if not db.query(Quiz).filter(Quiz.company_id == sirket.id).first():
            q1 = Quiz(
                company_id=sirket.id,
                title="İş Sağlığı ve Güvenliği (İSG) Sınavı",
                description="Yıllık zorunlu temel İSG değerlendirmesi.",
                duration_minutes=10,
                questions=[
                    {
                        "text": "Acil durumda tahliye toplanma alanına nasıl gidilir?",
                        "options": ["Asansör kullanarak", "Yangın merdiveni ve acil çıkış levhalarını izleyerek", "Koşarak"],
                        "correct_index": 1
                    },
                    {
                        "text": "Bilgisayar başında 20-20-20 kuralı neyi ifade eder?",
                        "options": ["20 dakikada bir 20 saniye 20 feet (6 metre) uzağa bakmayı", "20 saat çalışmayı", "Hiç mola vermemeyi"],
                        "correct_index": 0
                    }
                ]
            )
            q2 = Quiz(
                company_id=sirket.id,
                title="KVKK ve Şirket Bilgi Güvenliği Testi",
                description="Veri gizliliği ve güvenlik kuralları testi.",
                duration_minutes=15,
                questions=[
                    {
                        "text": "Şirket şifrenizi kimlerle paylaşabilirsiniz?",
                        "options": ["Çalışma arkadaşımla", "Hiç kimseyle", "Yöneticimle"],
                        "correct_index": 1
                    }
                ]
            )
            db.add_all([q1, q2])

        # 4. Günlük Vardiya ve Mola Çizelgesi
        bugun = date.today().isoformat()
        shift = db.query(ShiftSchedule).filter(ShiftSchedule.company_id == sirket.id, ShiftSchedule.shift_date == bugun).first()
        if not shift:
            shift = ShiftSchedule(
                company_id=sirket.id,
                shift_date=bugun,
                start_time="09:00",
                end_time="18:00",
                break_1="10:30 - 10:45",
                lunch_break="12:30 - 13:00",
                break_2="15:00 - 15:15",
                break_3="16:45 - 17:00"
            )
            db.add(shift)

        db.commit()
        print("\n✅ TAMAMDIR! Bütün personeller, sınavlar ve vardiyalar yüklendi.")
        print("Giriş yapabileceğin kullanıcılar (Hepsinin şifresi: 123456):")
        for p in personeller:
            print(f"  - Kullanıcı Adı: {p['kadi']}")

    except Exception as e:
        db.rollback()
        print(f"Hata çıktı: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verileri_doldur()