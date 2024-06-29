from setuptools import setup, find_packages

setup(
    name='django-simple-crud',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.0',
    ],
    description='A Django package to simplify CRUD operations using a base view class.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Khaled Sukkar',
    author_email='khaled.sukkar.contact@gmail.com',
    license = 'BSD',
    platforms='any',
    url=' https://github.com/khaledsukkar2/django-simple-crud.git',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
