from setuptools import setup, find_packages
from pathlib import Path

# Read the README file to use as the long description for the package
long_description = (Path(__file__).parent / "README.md").read_text()

setup(
    # Name of the package
    name='django-swift-crud',

    # Version of this release
    version='0.1.2',

    # Automatically find all packages in the current directory
    packages=find_packages(),

    # Include additional files specified in MANIFEST.in
    include_package_data=True,

    # List of dependencies required to install and run the package
    install_requires=[
        'Django>=3.0',  # Django version 3.0 or higher
    ],

    # Specify the minimum Python version required
    python_requires='>=3.7',

    # Short description of the package
    description='A Django package to simplify CRUD operations using a base view class.',

    # Long description of the package, read from the README file
    long_description=long_description,
    long_description_content_type='text/markdown',  # Specify the format of the long description

    # Package author details
    author='Khaled Sukkar',
    author_email='khaled.sukkar.contact@gmail.com',

    # License under which the package is released
    license='MIT',

    # Platforms that the package can run on
    platforms='any',

    # URL for the package's homepage or source code repository
    url='https://github.com/khaledsukkar2/django-simple-crud',

    # Classifiers help users find your project by categorizing it
    classifiers=[
        'Development Status :: 3 - Alpha',  # Development status of the package
        'Framework :: Django',  # Framework that the package is compatible with
        'Framework :: Django :: 3.0',  # Specific versions of Django supported
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Intended Audience :: Developers',  # Intended audience for the package
        'License :: OSI Approved :: MIT License',  # License type
        'Natural Language :: English',  # Language of the package
        'Operating System :: OS Independent',  # OS compatibility
        'Programming Language :: Python',  # Programming language used
        'Programming Language :: Python :: 3',  # Specific Python versions supported
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Application Frameworks',  # Category of the package
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    # Keywords to help users find the package
    keywords='django CRUD views mixins',
)
