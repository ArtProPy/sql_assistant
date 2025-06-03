from setuptools import setup, find_packages

setup(
    name='sql_assistant',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'SQLAlchemy==2.0.30',  # Работа с БД
        'loguru==0.7.2',  # Логи
        'asyncpg==0.30.0',  # Работа с асинхронными запросами к PostgreSQL
        # Для тестов
        'pytest==7.4.4',
        'pytest-asyncio==0.23.6',
        'pytest_subtests==0.11.0',
        'httpx==0.25.2',
        'PyYAML==6.0.1'
    ],
    author='Артем Проценко',
    author_email='artpropy@gmail.com',
    description='Помогает работать с sql_alchemy',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ArtProPy/sql_assistant.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',  # Версия Python
)
