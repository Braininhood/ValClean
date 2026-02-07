# Email Templates and Flows

This document lists **all email templates** and **when emails are sent** from sign up and verify through order complete and cleaning complete.

---

## 1. Templates (backend/templates/emails/)

| Template | File | When sent |
|----------|------|-----------|
| **booking_confirmation** | `.html`, `.txt` | When an order is created and confirmed (order creation flow). |
| **booking_reminder** | `.html`, `.txt` | 24 hours before appointment (run `python manage.py send_booking_reminders` daily, e.g. cron). |
| **booking_cancellation** | `.html`, `.txt` | When an order is cancelled (guest or customer cancel). |
| **welcome** | `.html`, `.txt` | **Optional** – after sign up. Not sent automatically; call `send_welcome_email(user)` from RegisterView if desired. |
| **cleaning_complete** | `.html`, `.txt` | When staff marks an appointment as **completed** (POST complete action). |

**Verify email** and **password reset** use inline plain-text in `apps/accounts/utils.py` (no HTML template in `emails/`). They are sent when the user requests verification or password reset.

---

## 2. Flow: Sign Up

- **Register:** `POST /api/aut/register/` creates user and returns tokens.
- **Welcome email:** **Not sent by default.** Templates exist: `welcome.html`, `welcome.txt`. To send on sign up, call `send_welcome_email(user)` from `RegisterView` after user creation (see `apps/notifications/email_service.send_welcome_email`).

---

## 3. Flow: Verify Email

- **Request:** `POST /api/aut/verify-email/request/` – sends verification email (plain text from `apps/accounts/utils.send_verification_email`).
- **Confirm:** `POST /api/aut/verify-email/confirm/` with token + code – marks email verified.
- **Resend:** `POST /api/aut/verify-email/resend/` (authenticated).
- **Template:** No file in `emails/`; message is built in `accounts/utils.py`. For production you can add `verify_email.html`/`.txt` and use `EmailService.send_templated_email`.

---

## 4. Flow: Password Reset

- **Request:** `POST /api/aut/password-reset/request/` – sends reset email (plain text from `apps/accounts/utils.send_password_reset_email`).
- **Confirm:** `POST /api/aut/password-reset/confirm/` with token + code + new password.
- **Template:** No file in `emails/`; message is built in `accounts/utils.py`.

---

## 5. Flow: Order Complete (Booking)

- **When:** Order is created via `POST /api/bkg/orders/` and status set to `confirmed`.
- **Email:** `send_booking_confirmation(order)` in `apps/orders/views.py` (OrderPublicViewSet create).
- **Template:** `booking_confirmation.html`, `booking_confirmation.txt`.
- **Recipient:** `order.guest_email` or `order.customer.email`.

---

## 6. Flow: Booking Reminder (24h Before)

- **When:** Run daily: `python manage.py send_booking_reminders` (or cron / Celery).
- **Email:** `send_booking_reminder(appointment)` for appointments in the next 23–25 hours.
- **Template:** `booking_reminder.html`, `booking_reminder.txt`.
- **Recipient:** From appointment’s order (customer or guest email).

---

## 7. Flow: Booking Cancellation

- **When:** Order is cancelled (guest cancel, customer cancel, or admin).
- **Email:** `send_booking_cancellation(order)` (called from order cancel endpoints).
- **Template:** `booking_cancellation.html`, `booking_cancellation.txt`.
- **Recipient:** `order.guest_email` or `order.customer.email`.

---

## 8. Flow: Cleaning Complete (Job Done)

- **When:** Staff marks appointment as completed: `POST /api/st/appointments/{id}/complete/` (or equivalent complete action).
- **Email:** `send_cleaning_complete(appointment)` in `apps/appointments/views.py` (complete action).
- **Template:** `cleaning_complete.html`, `cleaning_complete.txt`.
- **Recipient:** From appointment’s order (customer or guest email).

---

## 9. Summary Table

| Event | Template | Sent by | Trigger |
|-------|----------|---------|---------|
| Sign up | welcome | Optional (not by default) | Call `send_welcome_email(user)` from RegisterView if desired. |
| Verify email | (inline in utils) | `accounts/utils.send_verification_email` | User requests verification. |
| Password reset | (inline in utils) | `accounts/utils.send_password_reset_email` | User requests reset. |
| Order confirmed | booking_confirmation | `notifications/email_service.send_booking_confirmation` | Order created & confirmed. |
| 24h before appointment | booking_reminder | `send_booking_reminders` management command | Daily cron. |
| Order cancelled | booking_cancellation | `notifications/email_service.send_booking_cancellation` | Order cancelled. |
| Cleaning complete | cleaning_complete | `notifications/email_service.send_cleaning_complete` | Staff completes job. |

---

## 10. Enabling Welcome Email on Sign Up

To send the welcome email when a user registers, in `backend/apps/accounts/views.py` inside `RegisterView.create`, after `user = serializer.save()` (and after any Customer creation), add:

```python
try:
    from apps.notifications.email_service import send_welcome_email
    send_welcome_email(user, customer_name=user.get_full_name() or user.email)
except Exception as e:
    import logging
    logging.getLogger(__name__).warning('Failed to send welcome email: %s', e)
```

---

## 11. Configuration

- **From address:** `DEFAULT_FROM_EMAIL` in settings (e.g. `noreply@valclean.uk`).
- **Backend:** In development, `EMAIL_BACKEND` is often `console`; in production set SMTP (e.g. Gmail) in `.env`: `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`.
- **Frontend URL:** `FRONTEND_URL` in settings (used in links in emails).
