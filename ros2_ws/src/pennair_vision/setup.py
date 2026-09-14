import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'pennair_vision'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Bhargav',
    maintainer_email='bhargav2k7@gmail.com',
    description='Shape detection nodes',
    license='MIT',
    entry_points={
        'console_scripts': [
            'image_publisher = pennair_vision.image_publisher:main',
            'detector_node = pennair_vision.detector_node:main',
        ],
    },
)