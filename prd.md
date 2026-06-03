# PRD – GPS Tracking Link Platform (Django)

## Project Overview

Platform web berbasis Django yang memungkinkan administrator membuat link tracking unik. Saat link dibuka, pengguna wajib memberikan izin lokasi GPS untuk melanjutkan. Setelah lokasi diperoleh, sistem menyimpan data kunjungan lengkap untuk keperluan monitoring dan analisis.

---

# Technology Stack

## Backend

* Django 5+
* Django REST Framework
* PostgreSQL
* Celery (optional)
* Redis (optional)

## Frontend

* Django Templates
* Bootstrap 5
* HTMX (optional)
* JavaScript ES6

## Maps

* Leaflet.js
* OpenStreetMap

## Deployment

* Docker
* Gunicorn
* Nginx
* PostgreSQL

---

# User Roles

## Super Admin

Memiliki akses penuh:

* Dashboard
* Tracking Links
* Tracking Results
* Analytics
* Export Data
* Settings

---

# Menu Structure

## Dashboard

URL:

/dashboard

Menampilkan statistik sistem.

### Cards

* Total Tracking Links
* Total Hits
* Unique Visitors
* Today's Hits
* Active Links

### Charts

* Daily Visits
* Top Countries
* Top Cities

### Live Activity

Daftar hit terbaru.

---

## Tracking Links

URL:

/tracking-links

### Features

* Create Link
* Search Link
* Filter Status
* Copy Link
* Disable Link
* Delete Link

### Table

| Name | Code | Created | Hits | Status | Action |

---

## Create Link

URL:

/tracking-links/create

### Form Fields

#### Link Name

Contoh:

* Interview Tracking
* Attendance Tracking
* Delivery Confirmation

#### Description

Optional.

#### Expired Date

Optional.

#### Active

Boolean.

#### Require GPS

Default TRUE.

#### Success Redirect URL

Optional.

Contoh:

https://google.com

Jika berhasil tracking, user diarahkan ke URL ini.

---

## Tracking Results

URL:

/tracking-results

### Filters

* Date Range
* Link
* Country
* City
* IP Address

### Table

| Date | Link | IP | Country | City | Device | Action |

---

# Detail Tracking Result

URL:

/tracking-results/{id}

## General Information

* Visit Time
* Tracking Link
* Referrer

## Network Information

* IP Address
* ISP
* ASN

## Device Information

* Browser
* Browser Version
* Operating System
* Device Type
* Screen Resolution
* Language

## GPS Information

* Latitude
* Longitude
* Accuracy

## Location Information

* Country
* Province
* City
* District
* Full Address

## Map

Leaflet Map

Menampilkan marker lokasi visitor.

---

# Visitor Flow

## Generated Link

Contoh:

https://domain.com/t/ABC123XYZ

---

## Open Link

User membuka link.

---

## Permission Screen

Halaman:

Location Required

Pesan:

This page requires location access to continue.

Button:

Allow Location

---

## GPS Request

JavaScript:

navigator.geolocation.getCurrentPosition()

---

## Success

Jika lokasi diperoleh:

POST data ke API:

/api/track/

Data:

* latitude
* longitude
* accuracy

---

## Denied

Jika user menolak:

Tampilkan:

Location permission is required.

Button:

Try Again

Konten tidak dapat diakses.

Catatan:
Browser tidak mengizinkan website memaksa pengguna menekan "Allow". Aplikasi hanya dapat memblokir akses sampai izin diberikan.

---

# Django Apps Structure

## apps/accounts

Authentication.

Models:

* User

Views:

* Login
* Logout

---

## apps/dashboard

Dashboard analytics.

Views:

* DashboardView

---

## apps/tracking

Core tracking system.

Models:

* TrackingLink
* TrackingHit

Views:

* CreateLinkView
* LinkListView
* ResultListView
* ResultDetailView

---

## apps/api

REST API.

Endpoints:

POST /api/track/

GET /api/results/

GET /api/stats/

---

# Database Design

## tracking_links

id

uuid

name

description

code

require_gps

redirect_url

is_active

created_at

expired_at

created_by

---

## tracking_hits

id

tracking_link_id

ip_address

latitude

longitude

accuracy

country

province

city

district

full_address

isp

asn

browser

browser_version

os

device_type

language

screen_width

screen_height

referrer

visited_at

---

# API Endpoints

## Create Tracking Data

POST

/api/track/

Request:

{
"code": "ABC123",
"latitude": -6.21462,
"longitude": 106.84513,
"accuracy": 8
}

Response:

{
"success": true
}

---

## Dashboard Stats

GET

/api/dashboard/stats/

Response:

{
"total_links": 120,
"total_hits": 5240,
"today_hits": 84
}

---

# Dashboard Widgets

## Latest Hits

Menampilkan 20 hit terakhir.

## Visitor Map

Leaflet Fullscreen Map.

## Top Cities

Ranking kota.

## Top Countries

Ranking negara.

## Most Accessed Links

Top tracking links.

---

# Export Features

## CSV Export

* All Results
* Filtered Results

## Excel Export

* All Results
* Filtered Results

---

# Security

* Login Required
* CSRF Protection
* Rate Limiting
* HTTPS Required
* Audit Logs
* Soft Delete

---

# UI Pages

templates/

├── base.html

├── dashboard/

│   └── index.html

├── tracking/

│   ├── list.html

│   ├── create.html

│   ├── results.html

│   └── detail.html

├── accounts/

│   └── login.html

└── components/

```
├── navbar.html

├── sidebar.html

└── map.html
```

---

# Future Roadmap

Phase 2

* QR Tracking
* Real-time Visitor Tracking
* Telegram Notification
* WhatsApp Notification
* Geofence Detection

Phase 3

* Face Verification
* Selfie Capture
* Live Device Tracking
* Mobile Application
