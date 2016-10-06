SpookyOTP
=========

Lightweight Python package for TOTP/HOTP (Google Authenticator) codes

Description
===========

This is a lightweight package for generating TOTP and HOTP codes used
for two-factor authentication. They can be used with Google Authenticator
or FreeOTP.

Some features (such as using different hashing algorithms or displaying
more than 6 digits) do not work with Google Authenticator.

URIs generated (and QR codes encoding them) follow the [Google Authenticator format](https://github.com/google/google-authenticator/wiki/Key-Uri-Format)

Example
=======
    from spookyotp import (get_random_secret, TOTP, from_uri)
    
    secret = get_random_secret(n_bytes=10)
    totp = TOTP(secret, 'Example', 'user@example.org')
    totp.save_qr_code('qr.png')
    
    # you can now load the QR code with your app of choice
    code = input("Enter code: ")  # or raw_input in Python 2
    matches = totp.compare(code)
    if matches:
        print("Correct!")
    else:
        print("Incorrect.")

    # serialization and deserialization is supported via URI
    uri = totp.get_uri()
    new_totp = from_uri(uri)

Why Spooky?
===========

I created the git repo on Halloween, and there is already a project
called PyOTP.
