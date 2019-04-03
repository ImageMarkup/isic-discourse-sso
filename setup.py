from setuptools import find_packages, setup

setup(
    name='isic-discourse-sso',
    version='0.1.0',
    description='Girder plugin for a Discourse Single-Sign-On provider.',
    url='https://github.com/ImageMarkup/isic_discourse_sso',
    packages=find_packages(exclude=['test']),
    package_data={'isic_discourse_sso': ['webroot.mako']},
    install_requires=[
        'girder>=3.0.0a2',
        'girder-oauth',
        'isic-archive',
    ],
    entry_points={'girder.plugin': ['isic_discourse_sso = isic_discourse_sso:DiscourseSSO']},
)
