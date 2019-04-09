from setuptools import find_packages, setup

setup(
    name='isic-discourse-sso',
    version='1.0.0',
    description='Girder plugin for a Discourse Single-Sign-On provider.',
    url='https://github.com/ImageMarkup/isic-discourse-sso',
    license='Apache 2.0',
    packages=find_packages(exclude=['test']),
    python_requires='>=3.6',
    install_requires=['girder>=3.0.0a2'],
    entry_points={'girder.plugin': ['isic_discourse_sso = isic_discourse_sso:DiscourseSSO']},
)
