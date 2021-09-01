FROM python:latest
COPY bot.py .
RUN pip install python-telegram-bot --upgrade
RUN pip install requests --upgrade
RUN pip install bs4 --upgrade
RUN pip install cryptography --upgrade
ENTRYPOINT [ "python3" ]
CMD ["bot.py"]