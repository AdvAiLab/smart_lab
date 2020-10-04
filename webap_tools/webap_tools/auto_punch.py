import calendar
import json
import sys
import threading
from datetime import datetime, timedelta
from random import randint
from time import ctime

import schedule
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .webap_login import WebAp


class AutoPunching(WebAp):

    def _nav_to_checkform(self):
        self._nav_to_menu("spnode_[B40]_兼任助理差勤作業")
        labor_section = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#SubMenu_dgData > tbody > tr.TRAlternatingItemStyle > td:nth-child(1) > a")))
        labor_section.click()

    def _check_in(self):
        check_in_bt = self.wait.until(
            EC.presence_of_element_located((By.ID, "B4001A_btnIN")))
        check_in_bt.click()
        self.wait.until(EC.alert_is_present())
        alert = self.browser.switch_to.alert
        if alert.text == "打上班卡完成":
            print("上班打卡成功")
        elif alert.text == "不允許重複打卡!!!":
            print("失敗，重複打卡")
        print("Checking in done at %s", ctime())
        alert.accept()
        self.logout()

    def _check_out(self, work_content="寫程式"):
        work_content_area = self.wait.until(
            EC.presence_of_element_located((By.ID, "B4001A_txtJOB_NOTES")))
        work_content_area.send_keys(work_content)
        check_out_bt = self.wait.until(
            EC.presence_of_element_located((By.ID, "B4001A_btnOFF")))
        check_out_bt.click()
        self.wait.until(EC.alert_is_present())
        alert = self.browser.switch_to.alert
        if alert.text == "打下班卡完成":
            print("下班打卡成功")
        elif alert.text == "不允許重複打卡!!!":
            print("失敗，重複打卡")
        print("Checking out done at %s" % ctime())
        alert.accept()
        self.logout()

    def _fill_break_time(self, start_time="12:15", end_time="12:45"):
        break_time_start = self.wait.until(
            EC.presence_of_element_located((By.ID, "B4001A_txtBREAK_STM")))
        break_time_start.send_keys(start_time)
        break_time_end = self.wait.until(
            EC.presence_of_element_located((By.ID, "B4001A_txtBREAK_ETM")))
        break_time_end.send_keys(end_time)

    def calendar_plan_month_job(self, holiday_list=(),
                                login_delay=2):
        '''
        :param year:
        :param month:
        :param start_day:
        :param end_day:
        :param duty_datetime: {<weekday>: [<start_time>, <end_time>]}
        :param holiday_list:
        :param login_delay:
        :return:
        '''
        duty_datetime = self.config["duty_datetime"]
        year = self.config["year"]
        month = self.config["month"]
        start_day = self.config["start_day"]
        end_day = self.config["end_day"]
        c = calendar.Calendar(firstweekday=6)
        login_delta = timedelta(minutes=login_delay)
        today = datetime.today()
        if today > datetime(year, month, start_day):
            start_day = today
        print("排程開始日為%s月%s號" % (month, start_day))
        print("國定假日為%s" % str(holiday_list))
        for date in c.itermonthdates(year, month):
            weekday = date.strftime("%A").lower()
            if date.month == month and date.day not in holiday_list \
                    and date.day in range(start_day, end_day + 1) \
                    and weekday in duty_datetime.keys():

                # Calculate check-in time.
                check_in_time = duty_datetime[weekday][0]
                check_in_time = datetime.strptime(check_in_time, "%H:%M").time()
                check_in_time = datetime.combine(date, check_in_time)
                check_in_time = check_in_time - timedelta(minutes=randint(0, 5))

                print(date.ctime(), date.weekday())

                # Login to webap system and navigate to checking page
                login_time = check_in_time - login_delta
                if (login_time - datetime.now()).days >= 0:
                    print("login_time=%s " % login_time.ctime())
                    print("check_in_time=%s " % check_in_time.ctime())
                    print("second to wait: %s" % (
                            login_time - datetime.now()).total_seconds())
                    threading.Timer((login_time - datetime.now()).total_seconds(), self._nav_to_checkform).start()

                    # Check in
                    threading.Timer((check_in_time - datetime.now()).total_seconds(), self._check_in).start()
                    # threading.Timer((check_in_time - datetime.now()).total_seconds(), self.logout).start()

                    print()
                else:
                    print("今天上班卡時間已過，繼續排程下班卡")

                # Check out
                check_out_time = duty_datetime[weekday][1]
                check_out_time = datetime.strptime(check_out_time, "%H:%M").time()
                check_out_time = datetime.combine(date, check_out_time)
                check_out_time = check_out_time + timedelta(minutes=randint(0, 5))

                login_time = check_out_time - login_delta
                if (login_time - datetime.now()).days >= 0:
                    threading.Timer((login_time - datetime.now()).total_seconds(), self._nav_to_checkform).start()
                    print("login_time=%s " % login_time.ctime())

                    if check_out_time - check_in_time > timedelta(hours=4.5):
                        print("break_time= 12:15 ~ 12:45")
                        threading.Timer((check_out_time - datetime.now()).total_seconds(), self._fill_break_time).start()
                    threading.Timer((check_out_time - datetime.now()).total_seconds(), self._check_out).start()

                    # threading.Timer((check_out_time - datetime.now()).total_seconds(), self.logout).start()

                    print("check_out_time=%s " % check_out_time.ctime())
                    print()
                else:
                    print("今天下班卡時間已過，繼續排程下一天")

    def test_job(self, arg="default"):
        print("I'm working. arg=" + arg)
        print(datetime.now())

