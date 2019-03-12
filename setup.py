from setuptools import find_packages, setup

setup(
    name='girder-discourse-sso',
    version='0.1.0',
    description='Girder plugin for a Discourse Single-Sign-On provider.',
    url='https://github.com/ImageMarkup/girder_discourse_sso',
    packages=find_packages(exclude=['test']),
    package_data={'girder_discourse_sso': ['webroot.mako']},
    install_requires=[
        'girder>=3.0.0a2',
        'girder-oauth',
        'isic-archive @ https://github.com/ImageMarkup/isic-archive/archive/girder3.tar.gz',
    ],
    entry_points={'girder.plugin': ['girder_discourse_sso = girder_discourse_sso:DiscourseSSO']},
)
