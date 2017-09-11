Discourse SSO
=============

[Girder](https://github.com/girder/girder) plugin for a
[Discourse](https://www.discourse.org) Single-Sign-On provider. This enables
using Girder authentication for Discourse and avoids requiring users to create
an additional account to use Discourse.

See https://meta.discourse.org/t/official-single-sign-on-for-discourse/13045.

Requirements
------------
* **Girder 2.x**

Configuration
-------------

#### Discourse

Configure the options on the Discourse admin page as follows:

* Set `sso url` to `https://<girder_hostname>/api/v1/discourse_sso`.
* Set `sso secret` to a long random string.
* Enable `enable sso`.

#### Girder

Configure the options on the Discourse SSO plugin configuration page as follows:

* Set `Discourse SSO secret` to the `sso secret` configured in Discourse.
* If Girder is not configured to verify user's email addresses, enable `Require
  Discourse to confirm email address`.
