"""Custom CAPTCHA challenge for the sign-up form.

django-simple-captcha's built-in ``math_challenge`` chooses the operator at
random from ``(+, *, -)`` and treats ``CAPTCHA_MATH_CHALLENGE_OPERATOR`` as the
*display* symbol for multiplication only. Forcing that setting to ``'+'`` there
made a ``10*4`` problem (answer 40) render as ``"10+4="`` while the stored answer
stayed 40 — so every human answer looked wrong.

This keeps the challenge to simple, unambiguous single-digit **addition**: the
image the user sees and the answer stored in the CaptchaStore are always the same
sum, so a correct answer always validates. Wire it in via
``CAPTCHA_CHALLENGE_FUNCT`` in settings.
"""
import random


def add_challenge():
    """Return ``("a + b =", "<a+b>")`` for two single digits.

    The first element is what gets rendered into the image; the second is the
    exact string the CaptchaField compares the typed answer against.
    """
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    return ('%d + %d =' % (a, b), str(a + b))
