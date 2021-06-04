from distutils.core import setup
setup(
  name = 'rhprocessor',         
  packages = ['rhprocessor'],
  version = '0.0.1-beta.1',   
  license='MIT',
  description = 'Pipeline processor',
  author = 'rhodie',
  author_email = 'rhandref@gmail.com',
  url = 'https://github.com/rhodief/rhprocessor',
  download_url = 'https://github.com/rhodief/rhprocessor/archive/refs/tags/v0.0.1-beta.1.tar.gz',
  keywords = ['pipeline', 'processor'],
  install_requires=[],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.8',
  ],
)

## python setup.py sdist
## twine upload dist/*
## pip install rhprocessor --upgrade