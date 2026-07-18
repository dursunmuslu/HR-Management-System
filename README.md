# HR Management System

Modern web teknolojileri kullanılarak geliştirilen Full Stack İnsan Kaynakları Yönetim Sistemi. Proje; kullanıcı doğrulama, rol tabanlı yetkilendirme, personel yönetimi ve izin yönetimi süreçlerini REST API mimarisi ile yönetmektedir.

---

## Canlı Demo

**Frontend**

https://HR-MANAGEMENT-FRONTEND-URL

**Backend API**

https://hr-management-api-6rpx.onrender.com

**Swagger**

https://hr-management-api-6rpx.onrender.com/docs

---

# Kullanılan Teknolojiler

## Backend

- FastAPI
- Python
- SQLAlchemy ORM
- Pydantic
- JWT Authentication
- Passlib (Password Hashing)
- PostgreSQL
- Uvicorn
- RESTful API
- CORS Middleware

## Frontend

- Angular 19
- TypeScript
- Angular Standalone Components
- Angular Router
- Angular Material
- RxJS
- SCSS
- Reactive Forms
- HttpClient

## Veritabanı

- PostgreSQL

## Deployment

- Render
- Vercel

## Version Control

- Git
- GitHub

---

# Özellikler

## Kimlik Doğrulama

- JWT Authentication
- Login
- Password Hashing
- Protected Routes
- Token Based Authorization

## Rol Yönetimi

- Admin
- Employee
- Role Update
- Yetki Kontrolü

## Personel Yönetimi

- Personel Listeleme
- Personel Oluşturma
- Personel Güncelleme
- Personel Silme
- Kullanıcı Hesabı Oluşturma

## İzin Yönetimi

- İzin Talebi Oluşturma
- Bekleyen Talepler
- Onaylanan Talepler
- Reddedilen Talepler
- Yönetici Onay Sistemi

## Dashboard

- Toplam Personel
- Bekleyen İzin Sayısı
- Onaylanan İzinler
- Reddedilen İzinler
- Genel İstatistikler

---

# Proje Mimarisi

```
HR-Management-System
│
├── backend
│   ├── app
│   │   ├── routers
│   │   ├── models
│   │   ├── schemas
│   │   ├── services
│   │   ├── database
│   │   ├── core
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend
│   ├── src
│   ├── public
│   ├── angular.json
│   ├── package.json
│   └── tsconfig.json
│
├── docker-compose.yml
└── README.md
```

---

# Kurulum

## Repository

```bash
git clone https://github.com/dursunmuslu/HR-Management-System.git

cd HR-Management-System
```

---

## Backend

```bash
cd backend

python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Kurulum

```bash
pip install -r requirements.txt
```

Çalıştırma

```bash
uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

ng serve
```

Frontend

```
http://localhost:4200
```

---

## Docker

```bash
docker compose up -d
```

---

# API Dokümantasyonu

Swagger

```
/docs
```

ReDoc

```
/redoc
```

---

# Güvenlik

- JWT Authentication
- Password Hashing
- Role Based Authorization
- RESTful API
- CORS Configuration
- Input Validation
- Protected Endpoints

---

# Geliştirme Sürecinde Kullanılan Yaklaşımlar

- Katmanlı Mimari (Layered Architecture)
- REST API Tasarımı
- Dependency Injection
- Repository Pattern
- DTO (Pydantic Schemas)
- Reactive Programming (RxJS)
- Component Based Architecture
- Responsive UI Design

---

# Gelecekte Planlanan Özellikler

- Dosya Yükleme
- E-posta Bildirimleri
- Audit Log
- Maaş Yönetimi
- Mesai Takibi
- Çoklu Dil Desteği
- Dark Mode

---

# Geliştirici

**Dursun MUSLU**

GitHub

https://github.com/dursunmuslu

---

# Lisans

Bu proje eğitim ve portföy amacıyla geliştirilmiştir.
