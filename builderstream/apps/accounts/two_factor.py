"""
Two-factor authentication utilities.

Uses pyotp (bundled with django-otp dependency chain) for TOTP.
Backup codes are 8-character alphanumeric strings, stored hashed.
"""
import base64
import io
import os
import secrets
import string

import pyotp
import qrcode
from django.contrib.auth.hashers import check_password, make_password


BACKUP_CODE_LENGTH = 8
BACKUP_CODE_COUNT = 10


class TOTPService:

    @staticmethod
    def generate_secret() -> str:
        """Return a new base32 TOTP secret."""
        return pyotp.random_base32()

    @staticmethod
    def get_provisioning_uri(user, secret: str) -> str:
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user.email,
            issuer_name="BuilderStream",
        )

    @staticmethod
    def get_qr_code_base64(provisioning_uri: str) -> str:
        """Return a data:image/png;base64,... string for the QR code."""
        img = qrcode.make(provisioning_uri)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return "data:image/png;base64," + base64.b64encode(buf.read()).decode()

    @staticmethod
    def verify_code(secret: str, code: str) -> bool:
        """Validate a 6-digit TOTP code (allows ±1 window)."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

    @staticmethod
    def generate_backup_codes() -> tuple[list[str], list[str]]:
        """
        Return (plaintext_codes, hashed_codes).
        plaintext_codes is shown once to the user; hashed_codes are stored.
        """
        alphabet = string.ascii_uppercase + string.digits
        codes = [
            "".join(secrets.choice(alphabet) for _ in range(BACKUP_CODE_LENGTH))
            for _ in range(BACKUP_CODE_COUNT)
        ]
        hashed = [make_password(c) for c in codes]
        return codes, hashed

    @staticmethod
    def verify_backup_code(user, code: str) -> bool:
        """
        Check if code matches any stored backup code and consume it.
        Returns True if valid (and removes the used code).
        """
        stored = user.two_factor_backup_codes or []
        for i, hashed in enumerate(stored):
            if check_password(code.upper(), hashed):
                # Consume the code
                stored.pop(i)
                user.two_factor_backup_codes = stored
                user.save(update_fields=["two_factor_backup_codes"])
                return True
        return False

    @staticmethod
    def enable_2fa(user, secret: str, code: str) -> tuple[list[str], list[str]]:
        """
        Verify code against secret and enable 2FA for the user.
        Returns (plaintext_backup_codes, hashed_backup_codes).
        Raises ValueError if code is invalid.
        """
        if not TOTPService.verify_code(secret, code):
            raise ValueError("Invalid verification code.")

        plaintext, hashed = TOTPService.generate_backup_codes()
        user.two_factor_secret = secret
        user.two_factor_enabled = True
        user.two_factor_backup_codes = hashed
        user.save(update_fields=["two_factor_secret", "two_factor_enabled", "two_factor_backup_codes"])
        return plaintext, hashed

    @staticmethod
    def disable_2fa(user, code: str):
        """Disable 2FA after verifying the current code (or a backup code)."""
        valid = TOTPService.verify_code(user.two_factor_secret, code)
        if not valid:
            valid = TOTPService.verify_backup_code(user, code)
        if not valid:
            raise ValueError("Invalid code.")
        user.two_factor_enabled = False
        user.two_factor_secret = ""
        user.two_factor_backup_codes = []
        user.save(update_fields=["two_factor_enabled", "two_factor_secret", "two_factor_backup_codes"])
