"""
Google Drive upload helper using a Service Account.

Usage:
    from portal.services.google_drive import upload_image_to_drive
    result = upload_image_to_drive(request.FILES['image_file'])
    # result['direct_image_url'] -> use as image_url in model
    # result['file_id']          -> store as drive_file_id

Google packages are imported lazily so the module loads even when
google-api-python-client is not installed.
"""

import io
import os

from django.conf import settings
from django.core.exceptions import ValidationError

ALLOWED_MIME_TYPES = frozenset({'image/jpeg', 'image/png', 'image/webp', 'image/gif'})
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def upload_image_to_drive(file_obj, filename=None):
    """
    Upload an image to Google Drive via Service Account.

    Args:
        file_obj: Django UploadedFile (from request.FILES).
        filename: optional override for the Drive filename.

    Returns:
        dict with keys: file_id, view_url, direct_image_url, web_content_link

    Raises:
        RuntimeError: config missing, credentials file not found, or Drive API error.
        ValidationError: file too large or not an allowed image type.
    """
    folder_id = getattr(settings, 'GOOGLE_DRIVE_FOLDER_ID', '')
    sa_path = getattr(settings, 'GOOGLE_SERVICE_ACCOUNT_FILE', '')

    if not folder_id:
        raise RuntimeError(
            'GOOGLE_DRIVE_FOLDER_ID ไม่ได้ตั้งค่า '
            'กรุณาเพิ่มใน .env แล้วรีสตาร์ท server'
        )
    if not sa_path or not os.path.isfile(sa_path):
        raise RuntimeError(
            f'ไม่พบ Service Account file: "{sa_path}" '
            'กรุณาตรวจสอบ GOOGLE_SERVICE_ACCOUNT_FILE ใน .env '
            'และวาง service-account.json ไว้ใน root project '
            '(ห้าม commit ไฟล์นี้เข้า git)'
        )

    # --- Validate file size ---
    # Seek to end to get size without reading content into memory yet.
    file_obj.seek(0, 2)
    size = file_obj.tell()
    file_obj.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValidationError(
            f'ไฟล์ใหญ่เกิน 5 MB (ขนาดจริง {size / 1024 / 1024:.1f} MB) '
            'กรุณาบีบอัดรูปก่อนอัปโหลด'
        )

    # --- Validate MIME type ---
    # content_type is set by Django's ImageField after PIL verification,
    # sourced from the browser's Content-Type header.
    content_type = getattr(file_obj, 'content_type', '')
    if content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            f'ประเภทไฟล์ "{content_type}" ไม่รองรับ '
            'รองรับเฉพาะ JPG, PNG, WEBP, GIF'
        )

    # --- Import Google packages lazily ---
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        from googleapiclient.http import MediaIoBaseUpload
    except ImportError as exc:
        raise RuntimeError(
            'ยังไม่ได้ติดตั้ง Google API packages '
            'กรุณารัน: pip install google-api-python-client google-auth google-auth-httplib2'
        ) from exc

    # --- Build authenticated Drive service ---
    creds = service_account.Credentials.from_service_account_file(
        sa_path,
        scopes=['https://www.googleapis.com/auth/drive.file'],
    )
    service = build('drive', 'v3', credentials=creds)

    upload_name = filename or getattr(file_obj, 'name', 'image')
    file_metadata = {
        'name': upload_name,
        'parents': [folder_id],
    }
    # Read file content into BytesIO so it can be re-read if Drive retries.
    media = MediaIoBaseUpload(
        io.BytesIO(file_obj.read()),
        mimetype=content_type,
        resumable=False,
    )

    # --- Upload ---
    try:
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink,webContentLink',
        ).execute()
    except HttpError as exc:
        status = exc.resp.status if exc.resp else '?'
        raise RuntimeError(
            f'Google Drive API error (HTTP {status}): '
            'ตรวจสอบว่าแชร์ Drive Folder ให้ Service Account email เป็น Editor แล้ว '
            'และ folder ID ถูกต้อง'
        ) from exc

    file_id = uploaded['id']

    # --- Make file publicly readable if configured ---
    # Required so <img src="..."> loads for all users without authentication.
    # Note: drive.google.com/uc?export=view&id=<id> can be unreliable for
    # large files or files that trigger Google's virus-scan page.
    # The file_id is stored so the display URL can later be changed to
    # drive.google.com/thumbnail?id=<id>&sz=w1000 without a re-upload.
    if getattr(settings, 'GOOGLE_DRIVE_MAKE_PUBLIC', True):
        try:
            service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'},
            ).execute()
        except HttpError:
            # Non-fatal: file is uploaded but may not display publicly.
            # Committee will see a broken image on the public page.
            pass

    direct_image_url = f'https://drive.google.com/uc?export=view&id={file_id}'

    return {
        'file_id': file_id,
        'view_url': uploaded.get('webViewLink', ''),
        'direct_image_url': direct_image_url,
        'web_content_link': uploaded.get('webContentLink', ''),
    }
