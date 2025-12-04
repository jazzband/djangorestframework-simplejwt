# tests/test_i18n_translations.py

import pytest
from django.utils.translation import activate
from django.utils.translation import gettext as _

# Mapping: language code → list of messages to test
translations_to_test = {
    "ar": [
        ("Token is invalid", "الرمز غير صالح"),
        ("Token is expired", "انتهت صلاحية الرمز"),
        (
            "No active account found for the given token.",
            "لم يتم العثور على حساب نشط للرمز المقدم.",
        ),
    ],
    "cs": [
        ("Token is invalid", "Token není platný"),
        ("Token is expired", "Platnost tokenu vypršela"),
        (
            "No active account found for the given token.",
            "Pro zadaný token nebyl nalezen žádný aktivní účet.",
        ),
    ],
    "de": [
        ("Token is invalid", "Der Token ist ungültig."),
        ("Token is expired", "Der Token ist abgelaufen"),
        (
            "No active account found for the given token.",
            "Kein aktives Konto für das angegebene Token gefunden.",
        ),
    ],
    "es": [
        ("Token is invalid", "El token no es válido"),
        ("Token is expired", "El token ha expirado"),
        (
            "No active account found for the given token.",
            "No se encontró una cuenta activa para el token proporcionado.",
        ),
    ],
    "fr": [
        ("Token is invalid", "Le jeton est invalide"),
        ("Token is expired", "Le jeton a expiré"),
        (
            "No active account found for the given token.",
            "Aucun compte actif n'a été trouvé pour le token fourni",
        ),
    ],
    "he": [
        ("Token is invalid", "אסימון לא חוקי"),
        ("Token is expired", "האסימון פג תוקף"),
        (
            "No active account found for the given token.",
            "לא נמצא חשבון פעיל עבור הטוקן שסופק",
        ),
    ],
    "id": [
        ("Token is invalid", "Token tidak valid"),
        ("Token is expired", "Token telah kedaluwarsa"),
        (
            "No active account found for the given token.",
            "Tidak ada akun aktif yang ditemukan untuk token yang diberikan",
        ),
    ],
    "it": [
        ("Token is invalid", "Il token non è valido"),
        ("Token is expired", "Il token è scaduto"),
        (
            "No active account found for the given token.",
            "Nessun account attivo trovato per il token fornito",
        ),
    ],
    "ko": [
        ("Token is invalid", "유효하지 않은 토큰입니다"),
        ("Token is expired", "토큰이 만료되었습니다"),
        (
            "No active account found for the given token.",
            "해당 토큰에 대한 활성 계정을 찾을 수 없습니다.",
        ),
    ],
    "nl": [
        ("Token is invalid", "Token is ongeldig"),
        ("Token is expired", "Token is verlopen"),
        (
            "No active account found for the given token.",
            "Geen actief account gevonden voor het token",
        ),
    ],
    "pl": [
        ("Token is invalid", "Token jest niepoprawny"),
        ("Token is expired", "Token wygasł"),
        (
            "No active account found for the given token.",
            "Nie znaleziono aktywnego konta dla podanego tokena.",
        ),
    ],
    "ro": [
        ("Token is invalid", "Token nu este valid"),
        ("Token is expired", "Token-ul a expirat"),
        (
            "No active account found for the given token.",
            "Nu a fost găsit un cont activ pentru token-ul furnizat",
        ),
    ],
    "ru": [
        ("Token is invalid", "Токен недействителен"),
        ("Token is expired", "Токен недействителен"),
        (
            "No active account found for the given token.",
            "Активная учетная запись для данного токена не найдена",
        ),
    ],
    "sl": [
        ("Token is invalid", "Žeton ni veljaven"),
        ("Token is expired", "Žeton je potekel"),
        (
            "No active account found for the given token.",
            "Za dani žeton ni bil najden noben aktiven račun.",
        ),
    ],
    "sv": [
        ("Token is invalid", "Token är ogiltig"),
        ("Token is expired", "Token har löpt ut"),
        (
            "No active account found for the given token.",
            "Inget aktivt konto hittades för den angivna token.",
        ),
    ],
    "tr": [
        ("Token is invalid", "Token geçersiz"),
        ("Token is expired", "Jetonun süresi doldu"),
        (
            "No active account found for the given token.",
            "Belirtilen token için aktif hesap bulunamadı.",
        ),
    ],
    "uk": [
        ("Token is invalid", "Токен недійсний"),
        ("Token is expired", "Термін дії токена закінчився"),
        (
            "No active account found for the given token.",
            "Для цього токена не знайдено активного облікового запису.",
        ),
    ],
    "zh-hans": [
        ("Token is invalid", "令牌无效"),
        ("Token is expired", "令牌已过期"),
        (
            "No active account found for the given token.",
            "未找到与给定令牌对应的有效账户。",
        ),
    ],
}


@pytest.mark.parametrize("lang", translations_to_test.keys())
def test_translations(lang):
    activate(lang)
    for original, expected in translations_to_test[lang]:
        translated = _(original)
        assert translated == expected, (
            f"{lang}: {original} → {translated}, expected: {expected}"
        )
