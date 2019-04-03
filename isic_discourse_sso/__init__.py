# -*- coding: utf-8 -*-
from girder.plugin import GirderPlugin

from isic_discourse_sso import api


class DiscourseSSO(GirderPlugin):
    DISPLAY_NAME = 'Discourse SSO'

    def load(self, info):
        info['apiRoot'].discourse_sso = api.DiscourseSsoResource()
