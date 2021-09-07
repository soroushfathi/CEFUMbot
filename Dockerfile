FROM python:latest
COPY bot.py .
RUN pip3 install python-telegram-bot --upgrade
RUN pip3 install requests --upgrade
RUN pip3 install bs4 --upgrade
RUN pip3 install cryptography --upgrade
ENTRYPOINT [ "python3" ]
CMD ["bot.py"]